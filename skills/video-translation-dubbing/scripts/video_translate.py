#!/usr/bin/env python3
"""Video translation (视频翻译·双语字幕·英文配音): subtitles of a video -> a translation table -> bilingual / translated
subtitles -> optional dubbing in the target language, each line placed at its original time code.

  python3 scripts/video_translate.py selftest
  python3 scripts/video_translate.py recognize VIDEO_OR_AUDIO -o OUT [--dry-run]     # speech -> OUT/source.srt (official client)
  python3 scripts/video_translate.py table SUBTITLE -o table.tsv                       # SRT (.srt or SRT text in .txt) -> table
  python3 scripts/video_translate.py fill table.tsv translations.txt [-o table.tsv]   # one translated line per row, in order
  python3 scripts/video_translate.py check table.tsv [--strict]                        # missing / too long / overlapping lines
  python3 scripts/video_translate.py subs table.tsv -o OUT [--order target-first]      # bilingual.srt, target.srt, source.srt, bilingual.vtt
  python3 scripts/video_translate.py dub table.tsv -o OUT --voice 角色名 --language en [--refit] [--dry-run]

Table (UTF-8, tab separated, header line): id, start, end, source, target. The translation itself is written by your agent
or by you into the `target` column (or with `fill`); this script does not call any translation service.
`dub` speaks every `target` line with your own account role, speeds a line up (up to --max-speed) when its estimate is
longer than its time slot, places it at its start time and pushes it later only if the previous line is still running.
Outputs: OUT/dub.wav (full timeline), dub.srt (real dubbed timings), dub_report.txt, cache/.
Python 3.9+ standard library only. MIT licence.
"""
import argparse, contextlib, io, hashlib, os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_kit as K  # noqa: E402

VERSION = "1.0.0"
RATE = K.RATE
TC_RE = re.compile(r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})")
HEAD = ["id", "start", "end", "source", "target"]


def tc(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000.0


def parse_srt(path):
    raw = open(path, encoding="utf-8-sig").read().replace("\r", "")
    rows = []
    for block in re.split(r"\n\s*\n", raw):
        lines = [x for x in block.split("\n") if x.strip()]
        for i, line in enumerate(lines):
            m = TC_RE.search(line)
            if m:
                g = m.groups()
                text = " ".join(x.strip() for x in lines[i + 1:])
                text = re.sub(r"\s*\{\\[^}]*\}\s*", "", text).strip()
                if text:
                    rows.append([str(len(rows) + 1), K.ts(tc(*g[:4])), K.ts(tc(*g[4:])), text, ""])
                break
    if not rows:
        raise K.KitError("没有读到字幕：需要 SRT 格式（序号、00:00:01,000 --> 00:00:03,000、文字，空行分隔）。")
    return rows


def read_table(path):
    rows = []
    for n, line in enumerate(open(path, encoding="utf-8-sig").read().replace("\r", "").split("\n")):
        if not line.strip() or (n == 0 and line.lower().startswith("id\t")):
            continue
        cells = line.split("\t")
        if len(cells) < 4:
            raise K.KitError("对照表第 %d 行列数不对：需要 id、start、end、source、target 五列，用 Tab 分隔。" % (n + 1))
        cells = (cells + [""])[:5]
        m1, m2 = TC_RE.search(cells[1] + " --> " + cells[2]), None
        if not m1:
            raise K.KitError("对照表第 %d 行时间码格式不对：%s / %s（应为 00:00:01,000）" % (n + 1, cells[1], cells[2]))
        rows.append(cells)
    if not rows:
        raise K.KitError("对照表是空的。先用 table 命令从字幕生成。")
    return rows


def times(row):
    g = TC_RE.search(row[1] + " --> " + row[2]).groups()
    return tc(*g[:4]), tc(*g[4:])


def write_table(path, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\t".join(HEAD) + "\n")
        for r in rows:
            f.write("\t".join(c.replace("\t", " ").replace("\n", " ") for c in r) + "\n")


def is_cjk(text):
    return len(re.findall(r"[\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af]", text)) > len(text) / 3


def wrap(text, width):
    """wrap Latin text at spaces, CJK text by characters; at most two lines"""
    if len(text) <= width:
        return text
    if is_cjk(text):
        half = (len(text) + 1) // 2
        return text[:half] + "\n" + text[half:]
    words, a = text.split(), ""
    for i, w in enumerate(words):
        if len(a) + len(w) + 1 > max(width, len(text) // 2 + 1) and a:
            return a + "\n" + " ".join(words[i:])
        a = (a + " " + w).strip()
    return a


def est(text, cps, wps=K.WORDS_PER_SEC):
    """rough seconds at speed 1: CJK characters / cps + Latin words / wps"""
    han = len(re.findall(r"[\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af0-9]", text))
    latin = len(re.findall(r"[A-Za-z\u00c0-\u024f]+(?:'[A-Za-z]+)?", text))
    return max(0.6, han / cps + latin / wps)


# ------------------------------------------------------------------ commands

def cmd_recognize(a):
    out = os.path.join(a.output, "source.srt")
    if a.dry_run:
        note = "" if os.path.exists(a.media) else "（注意：文件 %s 现在不存在，正式运行前请确认路径）" % a.media
        print("[dry-run] 将调用官方客户端 recognize 识别 %s → %s，未读取文件、未调用接口%s" % (a.media, out, note))
        print("下一步：python3 scripts/video_translate.py table %s -o %s" % (out, os.path.join(a.output, "table.tsv")))
        return 0
    if not os.path.isfile(a.media):
        raise FileNotFoundError(a.media)
    K.require_key(False)
    os.makedirs(a.output, exist_ok=True)
    if os.path.exists(out):
        raise K.KitError("%s 已存在，官方客户端不覆盖文件：换一个 -o 目录，或删掉旧文件。" % out)
    h = hashlib.sha256(open(a.media, "rb").read()).hexdigest()
    cmd = [sys.executable, K.CLIENT, "recognize", "--file", a.media, "--wait", "--output", out, "--subtitle-format", "srt",
           "--idempotency-key", "vt-" + h[:40]]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        sys.stderr.write((r.stdout + r.stderr)[-1500:] + "\n")
        raise K.KitError("识别失败。直接重跑同一条命令：同一个文件使用同一个幂等键，服务端返回原任务，不会重复创建。")
    print("已识别 → %s\n下一步：python3 scripts/video_translate.py table %s -o %s" % (out, out, os.path.join(a.output, "table.tsv")))
    return 0


def cmd_table(a):
    rows = parse_srt(a.subtitle)
    if os.path.exists(a.output) and not a.force:
        raise K.KitError("%s 已存在，避免覆盖已填好的译文：换个文件名，或加 --force。" % a.output)
    write_table(a.output, rows)
    print("%d 行 → %s（第 5 列 target 留空，由 Agent 或你填写译文，或用 fill 命令按行写入）" % (len(rows), a.output))
    return 0


def cmd_fill(a):
    rows = read_table(a.table)
    lines = [x.strip() for x in open(a.translations, encoding="utf-8-sig").read().replace("\r", "").split("\n") if x.strip()]
    if len(lines) != len(rows):
        raise K.KitError("译文 %d 行，对照表 %d 行，行数不一致，没有写入。每行一句译文，顺序与对照表一致。" % (len(lines), len(rows)))
    for r, t in zip(rows, lines):
        r[4] = t
    write_table(a.output or a.table, rows)
    print("已写入 %d 行译文 → %s" % (len(rows), a.output or a.table))
    return 0


def problems(rows, a):
    out = []
    prev_end = 0.0
    for r in rows:
        s, e = times(r)
        slot = e - s
        if e <= s:
            out.append((r[0], "时间码无效：结束不晚于开始"))
        if s < prev_end - 0.001:
            out.append((r[0], "和上一行时间重叠 %.2f 秒" % (prev_end - s)))
        prev_end = max(prev_end, e)
        t = r[4].strip()
        if not t:
            out.append((r[0], "缺译文"))
            continue
        need = est(t, a.cps, a.wps) / a.speed
        if slot > 0 and need > slot * a.max_speed:
            out.append((r[0], "译文偏长：粗估要 %.1f 秒，时长只有 %.1f 秒（--max-speed %.2f 也放不下），建议缩写" % (need, slot, a.max_speed)))
        elif slot > 0 and need > slot:
            out.append((r[0], "配音会加速到约 %.2f 倍（粗估 %.1f 秒 / 时长 %.1f 秒）" % (need / slot * a.speed, need, slot)))
        width = a.max_line_cjk if is_cjk(t) else a.max_line
        if len(t) > width * 2:
            out.append((r[0], "字幕过长：%d 字符，超过两行（每行 %d）" % (len(t), width)))
    return out


def cmd_check(a):
    rows = read_table(a.table)
    probs = problems(rows, a)
    done = sum(1 for r in rows if r[4].strip())
    print("共 %d 行，已翻译 %d 行" % (len(rows), done))
    for i, msg in probs:
        print("  第 %s 行：%s" % (i, msg))
    hard = [p for p in probs if not p[1].startswith("配音会加速")]
    print("检查完成：%s" % ("没有问题" if not probs else "%d 处需要处理，%d 处仅提示" % (len(hard), len(probs) - len(hard))))
    return 1 if (a.strict and hard) else 0


def cmd_subs(a):
    rows = read_table(a.table)
    os.makedirs(a.output, exist_ok=True)
    bi, tgt, src = [], [], []
    for r in rows:
        s, e = times(r)
        t, o = r[4].strip(), r[3].strip()
        tw = wrap(t, a.max_line_cjk if is_cjk(t) else a.max_line) if t else ""
        ow = wrap(o, a.max_line_cjk if is_cjk(o) else a.max_line)
        pair = [x for x in ((tw, ow) if a.order == "target-first" else (ow, tw)) if x]
        bi.append((s, e, "\n".join(pair)))
        src.append((s, e, ow))
        if t:
            tgt.append((s, e, tw))
    K.write_srt(os.path.join(a.output, "bilingual.srt"), bi)
    K.write_srt(os.path.join(a.output, "target.srt"), tgt)
    K.write_srt(os.path.join(a.output, "source.srt"), src)
    with open(os.path.join(a.output, "bilingual.vtt"), "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for s, e, text in bi:
            f.write("%s --> %s\n%s\n\n" % (K.ts(s, "."), K.ts(e, "."), text))
    miss = len(rows) - len(tgt)
    print("%d 行 → %s/（bilingual.srt、bilingual.vtt、target.srt、source.srt）%s" % (
        len(rows), a.output, "；%d 行缺译文，双语字幕里只显示原文" % miss if miss else ""))
    return 0


def cmd_dub(a):
    K.check_speed(a.speed)
    K.check_speed(a.max_speed)
    rows = read_table(a.table)
    todo = [r for r in rows if r[4].strip()]
    if not todo:
        raise K.KitError("对照表里还没有译文（第 5 列 target 为空）。先填译文，或用 fill 命令写入。")
    K.require_key(a.dry_run)
    vargs = ["--dry-run"] if a.dry_run else K.voice_args(a.voice, a.actor_id)
    os.makedirs(a.output, exist_ok=True)
    cache = os.path.join(a.output, "cache")
    pcm, cues, report, cursor = K.silence(0), [], [], 0.0

    def speak(text, sp):
        if a.dry_run:
            return K.tone(180, est(text, a.cps, a.wps) / sp, level=0.05)
        return K.generate(text, vargs, cache, False, model=a.model, speed=sp, language=a.language, label="%s/%d" % (r[0], len(rows)))

    for r in todo:
        s, e = times(r)
        slot = max(0.2, e - s)
        text = r[4].strip()
        sp = a.speed
        need = est(text, a.cps, a.wps) / a.speed
        if need > slot:
            sp = min(a.max_speed, round(a.speed * need / slot, 2))
        seg = speak(text, sp)
        real = K.duration(seg)
        if a.refit and not a.dry_run and real > slot + 0.1 and sp < a.max_speed:
            sp2 = min(a.max_speed, round(sp * real / slot, 2))
            if sp2 > sp:
                sp, seg = sp2, speak(text, sp2)
                real = K.duration(seg)
        start = max(s, cursor)
        if start > K.duration(pcm):
            pcm += K.silence(start - K.duration(pcm))
        pcm += seg
        cursor = K.duration(pcm) + a.min_gap
        cues.append((start, K.duration(pcm), text))
        flag = []
        if start - s > 0.01:
            flag.append("顺延 %.2f 秒" % (start - s))
        if real > slot + 0.01:
            flag.append("超出时长 %.2f 秒" % (real - slot))
        report.append("%s\t%s\t语速 %.2f\t%.2f/%.2f 秒\t%s\t%s" % (r[0], K.ts(start), sp, real, slot, "；".join(flag) or "合格", text[:40]))
    last_end = max(times(r)[1] for r in rows)
    if K.duration(pcm) < last_end + a.tail:
        pcm += K.silence(last_end + a.tail - K.duration(pcm))
    pcm = K.normalize(pcm, a.peak)
    K.write_wav(os.path.join(a.output, "dub.wav"), pcm)
    K.write_srt(os.path.join(a.output, "dub.srt"), cues)
    bad = sum(1 for x in report if "合格" not in x)
    open(os.path.join(a.output, "dub_report.txt"), "w", encoding="utf-8").write(
        "id\t开始\t语速\t实际/时长\t状态\t译文\n" + "\n".join(report) + "\n")
    print("%d 句 → %s/（dub.wav %.1f 秒、dub.srt、dub_report.txt）%s%s" % (
        len(todo), a.output, K.duration(pcm), "；%d 句顺延或超时，见 dub_report.txt" % bad if bad else "；全部在原时间码内",
        "\n[dry-run：占位提示音，未调用接口；时长按粗估语速计算]" if a.dry_run else ""))
    return 0


def cmd_selftest(a):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "a_srt.txt")
    open(p, "w", encoding="utf-8").write("1\n00:00:00,500 --> 00:00:02,000\n你好，欢迎来到我的频道。\n\n2\n00:00:02,200 --> 00:00:04,000\n今天教你做一道菜。\n")
    rows = parse_srt(p)
    assert len(rows) == 2 and rows[1][3] == "今天教你做一道菜。", rows
    t = os.path.join(d, "t.tsv")
    write_table(t, rows)
    tr = os.path.join(d, "tr.txt")
    open(tr, "w", encoding="utf-8").write("Hi, welcome to my channel.\nToday I will show you a very long and detailed recipe for dinner tonight.\n")
    class A: pass
    x = A(); x.table, x.translations, x.output = t, tr, None
    with contextlib.redirect_stdout(io.StringIO()):
        cmd_fill(x)
    rows = read_table(t)
    assert rows[0][4].startswith("Hi")
    x = A(); x.table = t; x.cps = 4.2; x.wps = 2.4; x.speed = 1.0; x.max_speed = 1.3; x.max_line = 42; x.max_line_cjk = 16; x.strict = False
    pr = problems(rows, x)
    assert any(i == "2" for i, _ in pr), pr
    assert wrap("one two three four five six seven eight nine ten eleven", 20).count("\n") == 1
    x.output = d + "/o"; x.order = "target-first"
    with contextlib.redirect_stdout(io.StringIO()):
        cmd_subs(x)
    assert "Hi, welcome" in open(d + "/o/bilingual.srt", encoding="utf-8").read()
    x.voice = x.actor_id = x.model = x.language = None
    x.dry_run, x.refit, x.min_gap, x.tail, x.peak = True, False, 0.1, 0.5, -1.0
    with contextlib.redirect_stdout(io.StringIO()):
        cmd_dub(x)
    for f in ("dub.wav", "dub.srt", "dub_report.txt", "bilingual.vtt", "target.srt", "source.srt"):
        assert os.path.exists(d + "/o/" + f), f
    print("selftest ok（解析、填表、检查、双语字幕、dry-run 生成全部通过，未联网）")
    return 0


def main():
    p = argparse.ArgumentParser(prog="video_translate.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("selftest").set_defaults(fn=cmd_selftest)
    c = s.add_parser("recognize")
    c.add_argument("media")
    c.add_argument("-o", "--output", default="translate_out")
    c.add_argument("--dry-run", action="store_true")
    c.set_defaults(fn=cmd_recognize)
    c = s.add_parser("table")
    c.add_argument("subtitle")
    c.add_argument("-o", "--output", default="table.tsv")
    c.add_argument("--force", action="store_true")
    c.set_defaults(fn=cmd_table)
    c = s.add_parser("fill")
    c.add_argument("table")
    c.add_argument("translations")
    c.add_argument("-o", "--output")
    c.set_defaults(fn=cmd_fill)
    for name, fn in (("check", cmd_check), ("subs", cmd_subs), ("dub", cmd_dub)):
        c = s.add_parser(name)
        c.add_argument("table")
        c.add_argument("--cps", type=float, default=K.CHARS_PER_SEC, help="Chinese/Japanese/Korean chars per second at speed 1 (estimate)")
        c.add_argument("--wps", type=float, default=K.WORDS_PER_SEC, help="Latin words per second at speed 1 (estimate)")
        c.add_argument("--speed", type=float, default=1.0)
        c.add_argument("--max-speed", type=float, default=1.3)
        c.add_argument("--max-line", type=int, default=42, help="Latin characters per subtitle line")
        c.add_argument("--max-line-cjk", type=int, default=16, help="CJK characters per subtitle line")
        if name == "check":
            c.add_argument("--strict", action="store_true")
        else:
            c.add_argument("-o", "--output", default="translate_out")
        if name == "subs":
            c.add_argument("--order", choices=("target-first", "source-first"), default="target-first")
        if name == "dub":
            c.add_argument("--voice", help="account role name")
            c.add_argument("--actor-id")
            c.add_argument("--language", help="language hint for the role, e.g. en / ja / ko")
            c.add_argument("--model", choices=("expressive", "standard"))
            c.add_argument("--refit", action="store_true")
            c.add_argument("--min-gap", type=float, default=0.1)
            c.add_argument("--tail", type=float, default=0.5)
            c.add_argument("--peak", type=float, default=-1.0)
            c.add_argument("--dry-run", action="store_true")
        c.set_defaults(fn=fn)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    K.run(main)
