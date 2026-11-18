#!/usr/bin/env python3
"""Ad / promo voiceover (广告配音·宣传片配音): an ad script -> a voice track that fits a target length (15/30/60 s),
optionally mixed over your own music bed with automatic ducking (the music dips while the voice speaks).

  python3 scripts/ad_voice.py selftest
  python3 scripts/ad_voice.py demo-bgm OUT.wav [--seconds 20]          # synthesise a plain test music bed (original, offline)
  python3 scripts/ad_voice.py plan SCRIPT.txt --seconds 15 [--cps 4.2]
  python3 scripts/ad_voice.py build SCRIPT.txt -o OUT --seconds 15 --voice 角色名 [--bgm music.wav] [--refit] [--dry-run]
  python3 scripts/ad_voice.py mix VOICE.wav --bgm music.wav -o MIX.wav [--duck 10]

Script (UTF-8 text): sentences of the ad; a blank line is a short breath (--gap); a line `[停顿 0.5]` / `[pause 0.5]` is
a fixed pause; `#` lines are notes. Several versions for A/B tests: start each with a line `=== 版本名`.
Per version the script works out one speaking speed so that intro + voice + outro fits --seconds, generates every
sentence with that speed (cached), measures the real length and, with --refit, regenerates once at a corrected speed.
Outputs per version: OUT/版本名/voice.wav, mix.wav (with --bgm), ad.srt, report.txt; OUT/report.txt sums up all versions.
Music: PCM WAV only (convert mp3 first: ffmpeg -i music.mp3 music.wav). Use music you own or are licensed to use.
Python 3.9+ standard library only. MIT licence.
"""
import argparse, contextlib, io, array, math, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_kit as K  # noqa: E402

VERSION = "1.0.0"
RATE = K.RATE
PAUSE_RE = re.compile(r"^\s*[\[【(（]\s*(?:停顿|暂停|pause)\s*([0-9]+(?:\.[0-9]+)?)\s*(?:秒|s|sec)?\s*[\]】)）]\s*$", re.I)
VER_RE = re.compile(r"^\s*={3,}\s*(.*?)\s*$")


# ------------------------------------------------------------------ script

def parse(path):
    """-> [(version_name, [('text', s) | ('pause', sec) | ('gap', None)])]"""
    raw = open(path, encoding="utf-8-sig").read().replace("\r", "")
    versions, cur, name = [], [], "main"
    for line in raw.split("\n"):
        m = VER_RE.match(line)
        if m:
            if any(k == "text" for k, _ in cur):
                versions.append((name, cur))
            name, cur = (m.group(1) or "v%d" % (len(versions) + 1)), []
            continue
        p = PAUSE_RE.match(line)
        if p:
            cur.append(("pause", float(p.group(1))))
        elif not line.strip():
            if cur and cur[-1][0] == "text":
                cur.append(("gap", None))
        elif not line.lstrip().startswith("#"):
            for s in K.sentences(line):
                cur.append(("text", s))
    if any(k == "text" for k, _ in cur):
        versions.append((name, cur))
    if not versions:
        raise K.KitError("稿子里没有可朗读的文字。每行写一两句广告词；多版本用单独一行 === 版本名 分开。")
    names = [n for n, _ in versions]
    if len(set(names)) != len(names):
        raise K.KitError("版本名重复：%s。每个 === 后面的名字要不同。" % ", ".join(names))
    out = []
    for n, items in versions:
        while items and items[-1][0] == "gap":
            items.pop()
        out.append((n, items))
    return out


def safe(name):
    return re.sub(r"[\\/:*?\"<>|\s]+", "_", name).strip("_") or "main"


def count_chars(text):
    return len(re.findall(r"[\u4e00-\u9fff0-9]", text)) + len(re.findall(r"[A-Za-z]+", text))


def est_speech(items, cps, gap):
    """estimated seconds at speed 1 (speech only) and fixed silence seconds"""
    f = K.CHARS_PER_SEC / cps
    speech = sum(K.estimate_seconds(v) * f for k, v in items if k == "text")
    fixed = sum(v for k, v in items if k == "pause") + gap * sum(1 for k, _ in items if k == "gap")
    return speech, fixed


def fit_speed(items, seconds, intro, outro, cps, gap, lo, hi):
    """-> (speed, info dict)"""
    speech, fixed = est_speech(items, cps, gap)
    window = seconds - intro - outro - fixed
    chars = sum(count_chars(v) for k, v in items if k == "text")
    info = {"speech1": speech, "fixed": fixed, "window": window, "chars": chars, "note": ""}
    if window <= 0.5:
        raise K.KitError("目标 %.1f 秒放不下片头 %.1f 秒 + 片尾 %.1f 秒 + 固定停顿 %.1f 秒，调小 --intro / --outro 或删停顿。"
                         % (seconds, intro, outro, fixed))
    need = speech / window
    sp = min(max(need, lo), hi)
    info["need"] = need
    if need > hi:
        keep = int(chars * hi / need)
        info["note"] = "稿子偏长：按 --max-speed %.2f 也要约 %.1f 秒，超出 %.1f 秒。建议删到约 %d 字（现 %d 字），或调高 --max-speed。" % (
            hi, speech / hi, speech / hi - window, keep, chars)
    elif need < lo:
        info["note"] = "稿子偏短：按 --min-speed %.2f 念完约 %.1f 秒，剩余 %.1f 秒由片尾音乐补齐。" % (lo, speech / lo, window - speech / lo)
    info["cpm"] = chars / (speech / sp) * 60 if speech else 0
    return round(sp, 2), info


# ------------------------------------------------------------------ audio

def envelope_gain(voice, duck_db, threshold_db=-40.0, attack=0.08, release=0.35, win=0.02):
    """per-window music gain (linear): 1.0 where the voice is silent, 10^(-duck/20) where it speaks, smoothed."""
    n = max(1, int(win * RATE))
    thr = 32767 * 10 ** (threshold_db / 20.0)
    low = 10 ** (-duck_db / 20.0)
    target = []
    for i in range(0, len(voice), n):
        seg = voice[i:i + n]
        rms = math.sqrt(sum(v * v for v in seg) / len(seg)) if seg else 0
        target.append(low if rms > thr else 1.0)
    # look-ahead so the dip starts slightly before the first word
    ahead = max(1, int(attack / win))
    tgt = [min(target[i:i + ahead + 1]) for i in range(len(target))]
    out, g = [], 1.0
    a, r = win / attack, win / release
    for t in tgt:
        g += (t - g) * (a if t < g else r)
        out.append(g)
    return out, n


def mix(voice, music, duck_db=10.0, bgm_db=-14.0, fade_in=0.3, fade_out=1.0):
    """voice, music: array('h') mono at RATE. Music is looped/trimmed to the voice length."""
    L = len(voice)
    if not len(music):
        raise K.KitError("背景音乐文件是空的。")
    music = K.normalize(music, -1.0)
    bed = array.array("h", bytes(2 * L))
    for i in range(L):
        bed[i] = music[i % len(music)]
    gains, n = envelope_gain(voice, duck_db)
    base = 10 ** (bgm_db / 20.0)
    fi, fo = max(1, int(fade_in * RATE)), max(1, int(fade_out * RATE))
    out = array.array("h", bytes(2 * L))
    for i in range(L):
        g = base * gains[min(i // n, len(gains) - 1)]
        if i < fi:
            g *= i / fi
        if i > L - fo:
            g *= max(0.0, (L - i) / fo)
        v = voice[i] + bed[i] * g
        out[i] = 32767 if v > 32767 else (-32768 if v < -32768 else int(v))
    return K.normalize(out, -1.0)


def demo_bed(seconds):
    """A plain, original test bed: soft chord pad + light pulse, so the mix can be tried without any music file."""
    chords = [(261.63, 329.63, 392.0), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66)]
    bar = 2.0
    out = array.array("h")
    t = 0.0
    k = 0
    while t < seconds:
        c = chords[k % len(chords)]
        n = int(bar * RATE)
        seg = array.array("h", bytes(2 * n))
        for i in range(n):
            x = i / RATE
            env = min(1.0, x / 0.15, (bar - x) / 0.3)
            pulse = 0.6 + 0.4 * (1 if (x % 0.5) < 0.12 else 0)
            v = sum(math.sin(2 * math.pi * f * x) for f in c) / 3
            seg[i] = int(32767 * 0.3 * env * pulse * v)
        out += seg
        t += bar
        k += 1
    return out[: int(seconds * RATE)]


def placeholder(text, speed, cps):
    return K.tone(180, K.estimate_seconds(text) * (K.CHARS_PER_SEC / cps) / speed, level=0.05)


# ------------------------------------------------------------------ commands

def cmd_plan(a):
    for name, items in parse(a.script):
        sp, info = fit_speed(items, a.seconds, a.intro, a.outro, a.cps, a.gap, a.min_speed, a.max_speed)
        print("[%s] %d 字，正常语速朗读约 %.1f 秒；目标 %.0f 秒（片头 %.1f + 人声 %.1f + 片尾 %.1f）→ 建议语速 %.2f，约每分钟 %.0f 字"
              % (name, info["chars"], info["speech1"], a.seconds, a.intro, info["window"] + info["fixed"], a.outro, sp, info["cpm"]))
        if info["note"]:
            print("  提示：" + info["note"])
    print("（按每秒 %.1f 字粗估；正式生成后 report.txt 给出实测语速，可用 --cps 校准）" % a.cps)
    return 0


def render_version(name, items, a, vargs, speed, cache):
    """-> voice pcm (with intro/outro), cues, sentence count"""
    pcm, cues = K.silence(a.intro), []
    for k, v in items:
        if k == "pause":
            pcm += K.silence(v)
        elif k == "gap":
            pcm += K.silence(a.gap)
        else:
            start = K.duration(pcm)
            if a.dry_run:
                seg = placeholder(v, speed, a.cps)
            else:
                seg = K.generate(v, vargs, cache, False, model=a.model, speed=speed, language=a.language, label="%s: %s" % (name, v[:16]))
            pcm += seg
            cues.append((start, K.duration(pcm), v))
    return pcm, cues


def cmd_build(a):
    K.check_speed(a.min_speed)
    K.check_speed(a.max_speed)
    versions = parse(a.script)
    K.require_key(a.dry_run)
    vargs = ["--dry-run"] if a.dry_run else K.voice_args(a.voice, a.actor_id)
    music = K.read_wav_file(a.bgm) if a.bgm else None
    os.makedirs(a.output, exist_ok=True)
    cache = os.path.join(a.output, "cache")
    summary = []
    for name, items in versions:
        sp, info = fit_speed(items, a.seconds, a.intro, a.outro, a.cps, a.gap, a.min_speed, a.max_speed)
        pcm, cues = render_version(name, items, a, vargs, sp, cache)
        voice_len = K.duration(pcm) - a.intro
        refit = ""
        if a.refit and not a.dry_run and voice_len > info["window"] + info["fixed"] + 0.15:
            new = min(a.max_speed, round(sp * voice_len / (info["window"] + info["fixed"]), 2))
            if new > sp:
                refit = "实测人声 %.1f 秒超出，已按语速 %.2f 重配一次" % (voice_len, new)
                sp = new
                pcm, cues = render_version(name, items, a, vargs, sp, cache)
                voice_len = K.duration(pcm) - a.intro
        target = int(round(a.seconds * RATE))
        pcm += K.silence(a.outro)
        over = len(pcm) - target
        if over < 0:
            pcm += K.silence(-over / RATE)
        pcm = K.normalize(pcm, a.peak)
        d = os.path.join(a.output, safe(name))
        K.write_wav(os.path.join(d, "voice.wav"), pcm)
        K.write_srt(os.path.join(d, "ad.srt"), cues)
        if music is not None:
            K.write_wav(os.path.join(d, "mix.wav"), mix(pcm, music, a.duck, a.bgm_gain, a.fade_in, a.fade_out))
        speech_only = sum(c[1] - c[0] for c in cues)
        cps_real = info["chars"] / speech_only * sp if speech_only else 0
        lines = ["版本：%s" % name, "目标：%.1f 秒；成品：%.2f 秒%s" % (a.seconds, K.duration(pcm), "（超出 %.2f 秒，未裁剪人声）" % (over / RATE) if over > 0 else ""),
                 "语速：%.2f；字数：%d；人声段：%.2f 秒" % (sp, info["chars"], voice_len)]
        if not a.dry_run:
            lines.append("实测：正常语速约每秒 %.2f 字（下次 plan / build 可加 --cps %.2f 让预估更准）" % (cps_real, cps_real))
        if refit:
            lines.append(refit)
        if info["note"]:
            lines.append("提示：" + info["note"])
        lines.append("文件：voice.wav%s、ad.srt" % ("、mix.wav（背景音乐 %+.0f dB，人声处再压低 %.0f dB）" % (a.bgm_gain, a.duck) if music is not None else ""))
        open(os.path.join(d, "report.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        summary.append("%s\t%.2f 秒\t语速 %.2f\t%s" % (name, K.duration(pcm), sp, "超时" if over > 0 else "合格"))
        print("[%s] %d 句 → %s/  成品 %.2f 秒，语速 %.2f%s" % (name, len(cues), d, K.duration(pcm), sp, "（含 mix.wav）" if music is not None else ""))
        if info["note"]:
            print("  提示：" + info["note"])
    open(os.path.join(a.output, "report.txt"), "w", encoding="utf-8").write("\n".join(summary) + "\n")
    if a.dry_run:
        print("[dry-run：占位提示音，未调用接口；时长按粗估语速计算]")
    return 0


def cmd_mix(a):
    voice = K.read_wav_file(a.voice_wav)
    music = K.read_wav_file(a.bgm)
    out = mix(voice, music, a.duck, a.bgm_gain, a.fade_in, a.fade_out)
    K.write_wav(a.output, out)
    print("已混音 → %s（%.2f 秒，背景音乐 %+.0f dB，人声处再压低 %.0f dB）" % (a.output, K.duration(out), a.bgm_gain, a.duck))
    return 0


def cmd_demo(a):
    K.write_wav(a.out, demo_bed(a.seconds))
    print("已生成测试用背景音乐 %s（%.0f 秒，脚本合成的和弦铺底，仅用于试跑混音）" % (a.out, a.seconds))
    return 0


def cmd_selftest(a):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "s.txt")
    open(p, "w", encoding="utf-8").write("# 备注\n=== A\n冬天到了。\n\n暖手宝买一送一！\n=== B\n[停顿 0.3]\n今天下单，明天到家。\n")
    v = parse(p)
    assert [n for n, _ in v] == ["A", "B"], v
    assert [k for k, _ in v[0][1]] == ["text", "gap", "text"], v[0]
    sp, info = fit_speed(v[0][1], 6, 0.5, 1.0, 4.2, 0.3, 0.8, 1.35)
    assert 0.8 <= sp <= 1.35 and info["window"] > 0
    sp2, info2 = fit_speed([("text", "很长" * 60)], 5, 0.5, 0.5, 4.2, 0.3, 0.8, 1.35)
    assert sp2 == 1.35 and "偏长" in info2["note"]
    bed = demo_bed(3)
    voice = K.silence(1) + K.tone(300, 1, level=0.5) + K.silence(1)
    m = mix(voice, bed, duck_db=12, bgm_db=-6)
    assert len(m) == len(voice)
    quiet = K.peak(m[int(0.5 * RATE):int(0.6 * RATE)])
    assert quiet > 0
    class A: pass
    x = A(); x.script = p; x.output = d + "/o"; x.seconds = 6; x.intro = 0.5; x.outro = 1.0; x.cps = 4.2; x.gap = 0.3
    x.min_speed, x.max_speed, x.voice, x.actor_id, x.model, x.language = 0.8, 1.35, None, None, None, None
    x.peak, x.duck, x.bgm_gain, x.fade_in, x.fade_out, x.refit, x.dry_run = -1.0, 10.0, -14.0, 0.3, 1.0, False, True
    K.write_wav(d + "/bed.wav", bed)
    x.bgm = d + "/bed.wav"
    with contextlib.redirect_stdout(io.StringIO()):
        cmd_build(x)
    for f in ("A/voice.wav", "A/mix.wav", "A/ad.srt", "A/report.txt", "B/voice.wav", "report.txt"):
        assert os.path.exists(d + "/o/" + f), f
    assert abs(K.duration(K.read_wav_file(d + "/o/A/voice.wav")) - 6) < 0.01
    print("selftest ok（解析、卡时长、混音压低、dry-run 生成全部通过，未联网）")
    return 0


def main():
    p = argparse.ArgumentParser(prog="ad_voice.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("selftest").set_defaults(fn=cmd_selftest)
    d = s.add_parser("demo-bgm")
    d.add_argument("out")
    d.add_argument("--seconds", type=float, default=20.0)
    d.set_defaults(fn=cmd_demo)
    for name in ("plan", "build"):
        c = s.add_parser(name)
        c.add_argument("script")
        c.add_argument("--seconds", type=float, required=True, help="target length of the finished ad, e.g. 15 / 30 / 60")
        c.add_argument("--intro", type=float, default=0.5, help="music-only lead-in before the voice (s)")
        c.add_argument("--outro", type=float, default=1.0, help="music-only tail after the voice (s)")
        c.add_argument("--gap", type=float, default=0.3, help="pause for a blank line (s)")
        c.add_argument("--cps", type=float, default=K.CHARS_PER_SEC, help="reading rate used for estimates (chars/s at speed 1)")
        c.add_argument("--min-speed", type=float, default=0.8)
        c.add_argument("--max-speed", type=float, default=1.35)
        if name == "build":
            c.add_argument("-o", "--output", default="ad_out")
            c.add_argument("--voice", help="account role name")
            c.add_argument("--actor-id")
            c.add_argument("--language")
            c.add_argument("--model", choices=("expressive", "standard"))
            c.add_argument("--bgm", help="your own / licensed music bed, PCM WAV")
            c.add_argument("--duck", type=float, default=10.0, help="extra music dip under the voice (dB)")
            c.add_argument("--bgm-gain", type=float, default=-14.0, help="music level vs the voice (dB)")
            c.add_argument("--fade-in", type=float, default=0.3)
            c.add_argument("--fade-out", type=float, default=1.0)
            c.add_argument("--peak", type=float, default=-1.0)
            c.add_argument("--refit", action="store_true", help="regenerate once at a corrected speed if the real voice runs long")
            c.add_argument("--dry-run", action="store_true")
        c.set_defaults(fn=cmd_plan if name == "plan" else cmd_build)
    m = s.add_parser("mix")
    m.add_argument("voice_wav")
    m.add_argument("--bgm", required=True)
    m.add_argument("-o", "--output", default="mix.wav")
    m.add_argument("--duck", type=float, default=10.0)
    m.add_argument("--bgm-gain", type=float, default=-14.0)
    m.add_argument("--fade-in", type=float, default=0.3)
    m.add_argument("--fade-out", type=float, default=1.0)
    m.set_defaults(fn=cmd_mix)
    a = p.parse_args()
    if getattr(a, "seconds", 1) is not None and getattr(a, "seconds", 1) <= 0:
        raise K.KitError("--seconds 必须大于 0")
    return a.fn(a)


if __name__ == "__main__":
    K.run(main)
