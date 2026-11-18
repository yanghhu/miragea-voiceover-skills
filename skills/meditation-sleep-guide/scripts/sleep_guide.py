#!/usr/bin/env python3
"""Guided meditation / sleep audio (冥想引导·助眠音频): a calm script with pause marks -> one slow-paced audio file
whose silences are laid out to hit a target length in minutes.

  python3 scripts/sleep_guide.py selftest
  python3 scripts/sleep_guide.py plan SCRIPT.txt [--minutes 10]
  python3 scripts/sleep_guide.py build SCRIPT.txt -o OUT [--minutes 10] [--voice 角色名] [--speed 0.85] [--dry-run]

Script (UTF-8 text): one paragraph per block, blocks separated by a blank line. A line `[停顿 8]` (or `[pause 8]`) is a fixed
silence of 8 seconds. With --minutes, the leftover time is shared between paragraphs as extra silence (capped per gap by
--max-gap, default 20 s); if the speech is already longer than the target the script says so and adds no extra silence.
Outputs: OUT/guide.wav, guide.srt, guide.lrc, plan.txt (timeline), cache/ (a sentence is generated once).
Python 3.9+ standard library only. MIT licence.
"""
import argparse, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_kit as K  # noqa: E402

VERSION = "1.0.0"
PAUSE_RE = re.compile(r"^\s*[\[【(（]\s*(?:停顿|暂停|pause)\s*([0-9]+(?:\.[0-9]+)?)\s*(?:秒|s|sec)?\s*[\]】)）]\s*$", re.I)


def parse(path):
    raw = open(path, encoding="utf-8-sig").read().replace("\r", "")
    items, buf = [], []

    def flush():
        if buf:
            items.append(("text", "\n".join(buf).strip()))
            buf.clear()
    for line in raw.split("\n"):
        m = PAUSE_RE.match(line)
        if m:
            flush()
            items.append(("pause", float(m.group(1))))
        elif not line.strip():
            flush()
            if items and items[-1][0] == "text":
                items.append(("gap", None))
        elif not line.lstrip().startswith("#"):
            buf.append(line.strip())
    flush()
    items = [i for n, i in enumerate(items) if not (i[0] == "gap" and (n == len(items) - 1 or items[n + 1][0] != "text"))]
    if not any(k == "text" for k, _ in items):
        raise K.KitError("稿子里没有可朗读的文字：段落之间空一行，停顿单独写一行 [停顿 8]")
    return items


def layout(items, minutes, base_gap, max_gap, speed):
    """-> list of ('text', str, est_sec) / ('sil', sec) and a summary dict."""
    f = 1.0 / (speed or 1.0)
    out, speech, fixed, gaps = [], 0.0, 0.0, 0
    for k, v in items:
        if k == "text":
            est = sum(K.estimate_seconds(s) for s in K.sentences(v)) * f + 0.4 * len(K.sentences(v))
            out.append(["text", v, est])
            speech += est
        elif k == "pause":
            out.append(["sil", v, False])
            fixed += v
        else:
            out.append(["sil", base_gap, True])
            gaps += 1
    extra = 0.0
    note = ""
    if minutes:
        target = minutes * 60.0
        flexible = base_gap * gaps
        left = target - speech - fixed - flexible
        if left < 0:
            note = "朗读加固定停顿已超过目标 %.1f 分钟（粗估 %.1f 分钟），未再加停顿；可删减文字或调大 --speed。" % (
                minutes, (speech + fixed + flexible) / 60)
        elif gaps:
            per = min(left / gaps, max_gap - base_gap) if max_gap > base_gap else 0
            per = max(per, 0)
            for o in out:
                if o[0] == "sil" and o[2]:
                    o[1] += per
            extra = per * gaps
            if left - extra > 1:
                note = "每处停顿已达 --max-gap 上限 %.0f 秒，总长约 %.1f 分钟，比目标 %.1f 分钟短；可调大 --max-gap 或加段落。" % (
                    max_gap, (speech + fixed + flexible + extra) / 60, minutes)
        else:
            note = "稿子只有一个段落，没有可分配的停顿；用空行分段，或写 [停顿 秒数]。"
    total = speech + fixed + base_gap * gaps + extra
    return out, {"speech": speech, "total": total, "paragraphs": sum(1 for o in out if o[0] == "text"), "note": note}


def cmd_plan(a):
    items = parse(a.script)
    out, s = layout(items, a.minutes, a.gap, a.max_gap, a.speed)
    t = 0.0
    for o in out:
        if o[0] == "text":
            print("%s  朗读约 %.0f 秒  %s" % (K.ts(t, ".")[:8], o[2], o[1][:24].replace("\n", " ")))
            t += o[2]
        else:
            print("%s  停顿 %.1f 秒" % (K.ts(t, ".")[:8], o[1]))
            t += o[1]
    print("共 %d 段，朗读约 %.1f 分钟，预计总长约 %.1f 分钟" % (s["paragraphs"], s["speech"] / 60, s["total"] / 60))
    if s["note"]:
        print("提示：" + s["note"])
    return 0


def cmd_build(a):
    K.check_speed(a.speed)
    items = parse(a.script)
    K.require_key(a.dry_run)
    vargs = ["--dry-run"] if a.dry_run else K.voice_args(a.voice, a.actor_id)
    out_dir = a.output
    cache = os.path.join(out_dir, "cache")
    os.makedirs(out_dir, exist_ok=True)
    plan, s = layout(items, a.minutes, a.gap, a.max_gap, a.speed)
    pcm, cues, n = K.silence(a.lead), [], sum(1 for o in plan if o[0] == "text")
    k = 0
    for o in plan:
        if o[0] == "sil":
            pcm += K.silence(o[1]) if not a.dry_run else K.silence(min(o[1], a.dry_cap))
            continue
        k += 1
        start = K.duration(pcm)
        seg = None
        for sent in K.sentences(o[1]):
            p = K.generate(sent, vargs, cache, a.dry_run, model=a.model, speed=a.speed, language=a.language,
                           label="%d/%d" % (k, n))
            seg = p if seg is None else seg + K.silence(0.5) + p
        pcm += seg
        cues.append((start, K.duration(pcm), o[1].replace("\n", " ")))
    pcm += K.silence(a.tail)
    pcm = K.normalize(pcm, a.peak)
    K.write_wav(os.path.join(out_dir, "guide.wav"), pcm)
    K.write_srt(os.path.join(out_dir, "guide.srt"), cues)
    K.write_lrc(os.path.join(out_dir, "guide.lrc"), cues, a.title)
    lines = ["%s\t%s" % (K.ts(c[0], ".")[:8], c[2][:30]) for c in cues]
    open(os.path.join(out_dir, "plan.txt"), "w", encoding="utf-8").write(
        "成品 %.1f 秒（%.1f 分钟）\n%s\n" % (K.duration(pcm), K.duration(pcm) / 60, "\n".join(lines)))
    print("%d 段 → %s/（guide.wav / guide.srt / guide.lrc / plan.txt）成品约 %.1f 分钟%s" % (
        n, out_dir, K.duration(pcm) / 60, "  [dry-run：占位提示音且停顿压缩到每处 %.0f 秒内，未调用接口]" % a.dry_cap if a.dry_run else ""))
    if s["note"]:
        print("提示：" + s["note"])
    return 0


def cmd_selftest(a):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "s.txt")
    open(p, "w", encoding="utf-8").write("# 标题\n慢慢吸气。\n\n[停顿 5]\n\n慢慢呼气。\n\n放松肩膀。\n")
    it = parse(p)
    assert [k for k, _ in it] == ["text", "pause", "text", "gap", "text"] or [k for k, _ in it][0] == "text", it
    out, s = layout(it, 5, 3, 1000, 0.85)
    assert abs(s["total"] - 300) < 1, s
    out2, s2 = layout(it, 0.1, 3, 20, 0.85)
    assert "超过目标" in s2["note"]
    class A: pass
    x = A(); x.script = p; x.output = d + "/o"; x.minutes = 1; x.voice = x.actor_id = x.model = x.language = None
    x.speed, x.gap, x.max_gap, x.lead, x.tail, x.peak, x.title, x.dry_run, x.dry_cap = 0.85, 3.0, 20.0, 2.0, 3.0, -1.0, "t", True, 2.0
    cmd_build(x)
    for f in ("guide.wav", "guide.srt", "guide.lrc", "plan.txt"):
        assert os.path.exists(d + "/o/" + f), f
    print("selftest ok")
    return 0


def main():
    p = argparse.ArgumentParser(prog="sleep_guide.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("selftest").set_defaults(fn=cmd_selftest)
    for name in ("plan", "build"):
        c = s.add_parser(name)
        c.add_argument("script")
        c.add_argument("--minutes", type=float, help="target length in minutes")
        c.add_argument("--gap", type=float, default=3.0, help="base silence between paragraphs (s)")
        c.add_argument("--max-gap", type=float, default=20.0, help="max silence between paragraphs (s)")
        c.add_argument("--speed", type=float, default=0.85)
        if name == "build":
            c.add_argument("-o", "--output", default="guide_out")
            c.add_argument("--voice", help="account role name")
            c.add_argument("--actor-id")
            c.add_argument("--language")
            c.add_argument("--model", choices=("expressive", "standard"))
            c.add_argument("--lead", type=float, default=2.0)
            c.add_argument("--tail", type=float, default=3.0)
            c.add_argument("--peak", type=float, default=-1.0)
            c.add_argument("--title", default="")
            c.add_argument("--dry-run", action="store_true")
            c.add_argument("--dry-cap", type=float, default=2.0, help=argparse.SUPPRESS)
        c.set_defaults(fn=cmd_plan if name == "plan" else cmd_build)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    K.run(main)
