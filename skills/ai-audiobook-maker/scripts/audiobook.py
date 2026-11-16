#!/usr/bin/env python3
"""AI audiobook maker (AI有声书): a long novel / book TXT -> one audio file per chapter, with subtitles.

  python3 scripts/audiobook.py selftest                          offline self test (no key, no network)
  python3 scripts/audiobook.py plan BOOK.txt -o OUT              offline: detect chapters -> OUT/plan.md + chapters.json
  python3 scripts/audiobook.py build BOOK.txt -o OUT --voice 旁白角色名 [--dialogue-voice 对白角色名]
                                     [--chapters 1-3,5] [--speed 1.0] [--dry-run]

Chapters are found from lines such as `第十二章 雨夜`, `第3回`, `卷一`, `序章` / `楔子` / `尾声` / `番外…`,
`Chapter 7`, or Markdown `#`/`##` headings; a book with none is cut every --split-chars characters at a
paragraph end. Text files in UTF-8, UTF-8 with BOM or GB18030/GBK are read automatically.
Quoted speech (“…” 「…」 『…』) can use a second voice (--dialogue-voice); everything else is narration.

Outputs in OUT/: audio/NNN-<title>.wav, subtitles/NNN-<title>.srt + .lrc (for players that show lyrics),
playlist.m3u, chapters.json (duration and files of every chapter), progress.json, cache/ (per sentence;
re-running resumes and only generates what is missing or changed).
Python 3.9+ standard library only. MIT licence (see LICENSE.txt).
"""
import argparse
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_kit as K  # noqa: E402

VERSION = "1.0.0"
CN_NUM = "0-9零〇一二三四五六七八九十百千两壹贰叁肆伍陆柒捌玖拾佰仟"
HEAD_RES = [
    re.compile(r"^\s*(第[%s]+[章回节卷集篇部幕][^\n]{0,40})\s*$" % CN_NUM),
    re.compile(r"^\s*(卷[%s]+[^\n]{0,30})\s*$" % CN_NUM),
    re.compile(r"^\s*((?:序章|序言|楔子|引子|前言|尾声|后记|终章|番外)[^\n。！？]{0,30})\s*$"),
    re.compile(r"^\s*((?:Chapter|CHAPTER|Part|PART)\s+[\w.-]+[^\n]{0,60})\s*$"),
    re.compile(r"^\s*#{1,3}\s+([^\n]{1,60})\s*$"),
]
QUOTE_RE = re.compile(r"(“[^”]*”|「[^」]*」|『[^』]*』)")


def read_text(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise K.KitError("无法识别文件编码：%s（请另存为 UTF-8）" % path)


def heading(line):
    if len(line.strip()) > 60:
        return None
    for r in HEAD_RES:
        m = r.match(line)
        if m:
            return m.group(1).strip()
    return None


def split_chapters(text, split_chars=6000):
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u3000", " ")
    chapters, cur_title, cur = [], None, []
    for line in text.split("\n"):
        h = heading(line)
        if h:
            if cur_title is not None or "".join(cur).strip():
                chapters.append([cur_title or "开篇", "\n".join(cur).strip()])
            cur_title, cur = h, []
        else:
            cur.append(line)
    if cur_title is not None or "".join(cur).strip():
        chapters.append([cur_title or "开篇", "\n".join(cur).strip()])
    chapters = [c for c in chapters if c[1] or c[0] != "开篇"]
    if len(chapters) == 1 and chapters[0][0] == "开篇" and len(chapters[0][1]) > split_chars:
        body, parts, buf = chapters[0][1], [], ""
        for para in body.split("\n"):
            buf += para + "\n"
            if len(buf) >= split_chars:
                parts.append(buf.strip())
                buf = ""
        if buf.strip():
            parts.append(buf.strip())
        chapters = [["第%d部分" % (i + 1), p] for i, p in enumerate(parts)]
    return [{"index": i + 1, "title": t, "text": b} for i, (t, b) in enumerate(chapters)]


def segments(sentence):
    """-> [(kind, text)] where kind is 'dialogue' for quoted speech, else 'narration'."""
    out = []
    for part in QUOTE_RE.split(sentence):
        if not part.strip():
            continue
        kind = "dialogue" if QUOTE_RE.fullmatch(part) else "narration"
        text = part[1:-1].strip() if kind == "dialogue" else part.strip(" ，,")
        if text and re.search(r"[\w\u4e00-\u9fff]", text):
            out.append((kind, text))
    return out


def safe_name(s):
    return re.sub(r"[\\/:*?\"<>|\s]+", "_", s).strip("_")[:40] or "chapter"


def parse_range(spec, n):
    if not spec:
        return list(range(1, n + 1))
    picked = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        a, _, b = part.partition("-")
        try:
            lo, hi = int(a), int(b or a)
        except ValueError:
            raise K.KitError("--chapters 写法如 1-3,5，收到：%s" % spec)
        picked.update(range(lo, hi + 1))
    bad = [i for i in picked if not 1 <= i <= n]
    if bad:
        raise K.KitError("--chapters 超出范围：本书共 %d 章，收到 %s" % (n, sorted(bad)))
    return sorted(picked)


def chapter_stats(ch, max_chars):
    sents = K.sentences(ch["text"], max_chars)
    chars = len(re.sub(r"\s", "", ch["text"]))
    dlg = sum(1 for s in sents if any(k == "dialogue" for k, _ in segments(s)))
    est = sum(K.estimate_seconds(s) for s in sents)
    return sents, chars, dlg, est


def cmd_plan(a):
    chs = split_chapters(read_text(a.book), a.split_chars)
    os.makedirs(a.output, exist_ok=True)
    rows, meta, total = [], [], 0.0
    for ch in chs:
        sents, chars, dlg, est = chapter_stats(ch, a.max_chars)
        total += est
        rows.append("| %d | %s | %d | %d | %d | %.1f |" % (ch["index"], ch["title"], chars, len(sents), dlg, est / 60))
        meta.append({"index": ch["index"], "title": ch["title"], "chars": chars, "sentences": len(sents),
                     "dialogue_sentences": dlg, "estimated_minutes": round(est / 60, 1)})
    plan = ["# 有声书分章计划", "", "源文件：`%s`　共 %d 章，预计约 %.0f 分钟（按每秒约 %.1f 字粗估，实际以生成为准）。"
            % (os.path.basename(a.book), len(chs), total / 60, K.CHARS_PER_SEC), "",
            "| 章 | 标题 | 字数 | 句数 | 含对白句 | 预计分钟 |", "|---|---|---|---|---|---|"] + rows + [
            "", "章节识别不对时：在原文里把章节标题单独成行（如 `第三章 标题`、`## 标题`），再运行 plan。"]
    open(os.path.join(a.output, "plan.md"), "w", encoding="utf-8").write("\n".join(plan) + "\n")
    json.dump({"book": os.path.basename(a.book), "chapters": meta}, open(os.path.join(a.output, "chapters.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("%d 章，预计约 %.0f 分钟 → %s/plan.md、chapters.json" % (len(chs), total / 60, a.output))
    for m in meta[:12]:
        print("  %3d  %-24s %6d 字  约 %.1f 分钟" % (m["index"], m["title"][:24], m["chars"], m["estimated_minutes"]))
    if len(meta) > 12:
        print("  ……（共 %d 章，完整列表见 plan.md）" % len(meta))
    return 0


def cmd_build(a):
    K.check_speed(a.speed)
    K.require_key(a.dry_run)
    narr = ["--dry-run"] if a.dry_run else K.voice_args(a.voice, a.actor_id)
    dlg = narr
    if a.dialogue_voice or a.dialogue_actor_id:
        dlg = ["--dry-run-dialogue"] if a.dry_run else K.voice_args(a.dialogue_voice, a.dialogue_actor_id)
    chs = split_chapters(read_text(a.book), a.split_chars)
    picked = parse_range(a.chapters, len(chs))
    out = a.output
    for d in ("audio", "subtitles", "cache"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    prog_path = os.path.join(out, "progress.json")
    progress = json.load(open(prog_path, encoding="utf-8")) if os.path.exists(prog_path) else {}
    done = []
    for ch in chs:
        if ch["index"] not in picked:
            continue
        sents = K.sentences(ch["text"], a.max_chars)
        pcm, cues, t = K.silence(0.3), [], 0.3
        items = ([("title", ch["title"])] if a.read_titles else []) + [("sent", s) for s in sents]
        for n, (kind, s) in enumerate(items, 1):
            segs = [("narration", s)] if kind == "title" else segments(s)
            start = t
            for seg_kind, text in segs:
                v = dlg if seg_kind == "dialogue" else narr
                audio = K.generate(text, v, os.path.join(out, "cache"), a.dry_run, model=a.model, speed=a.speed,
                                   label="第%d章 %d/%d  %s" % (ch["index"], n, len(items), text[:30]))
                pcm += audio
                t += K.duration(audio)
                if seg_kind != segs[-1][0] or text != segs[-1][1]:
                    pcm += K.silence(0.12)
                    t += 0.12
            cues.append((start, t, s))
            g = a.chapter_gap if kind == "title" else a.gap
            pcm += K.silence(g)
            t += g
        pcm += K.silence(0.8)
        t += 0.8
        stem = "%03d-%s" % (ch["index"], safe_name(ch["title"]))
        wav = os.path.join(out, "audio", stem + ".wav")
        K.write_wav(wav, K.normalize(pcm, a.peak))
        K.write_srt(os.path.join(out, "subtitles", stem + ".srt"), cues)
        K.write_lrc(os.path.join(out, "subtitles", stem + ".lrc"), cues, ch["title"])
        progress[str(ch["index"])] = {"title": ch["title"], "file": "audio/%s.wav" % stem, "seconds": round(t, 2),
                                      "sentences": len(sents), "dry_run": a.dry_run}
        json.dump(progress, open(prog_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        done.append((ch["index"], ch["title"], t, stem))
        print("第%d章 %s  %.1f 秒 → audio/%s.wav" % (ch["index"], ch["title"], t, stem))
    entries = sorted(progress.items(), key=lambda kv: int(kv[0]))
    with open(os.path.join(out, "playlist.m3u"), "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for _, e in entries:
            f.write("#EXTINF:%d,%s\n%s\n" % (round(e["seconds"]), e["title"], e["file"]))
    json.dump({"book": os.path.basename(a.book), "chapters": [dict(index=int(k), **v) for k, v in entries]},
              open(os.path.join(out, "chapters.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total = sum(x[2] for x in done)
    print("完成 %d 章，共 %.1f 分钟 → %s/playlist.m3u、chapters.json%s" % (len(done), total / 60, out,
          "  [dry-run：占位提示音，未调用接口]" if a.dry_run else ""))
    return 0


SAMPLE = """第一章 灯塔
海边的小镇只有一座灯塔。守塔人老周每天傍晚爬上一百二十级台阶，把灯点亮。
那天，一个背着画板的女孩敲开了塔门。“请问，我能在上面画一张日落吗？”
老周看了看天色，说：“可以，但要在灯亮之前下来。”

第二章 画
女孩画得很慢，海风一次次掀起她的画纸。
“灯亮了，船就知道回家的路。”老周说。
女孩在画的角落添了一点黄色的光。
"""


def cmd_selftest(a):
    assert heading("第十二章 雨夜") == "第十二章 雨夜"
    assert heading("Chapter 3 The Sea") == "Chapter 3 The Sea"
    assert heading("## 尾声") == "尾声"
    assert heading("他走进第一章节的教室，看见很多很多的人在里面坐着读书写字，大家都非常认真地听老师讲课，没有一个人说话") is None
    chs = split_chapters(SAMPLE)
    assert [c["title"] for c in chs] == ["第一章 灯塔", "第二章 画"], chs
    assert segments("老周说：“可以。”") == [("narration", "老周说："), ("dialogue", "可以。")]
    assert parse_range("1-2", 2) == [1, 2]
    assert K.sentences("你好。“走吧！”他说。") == ["你好。", "“走吧！”", "他说。"]
    d = tempfile.mkdtemp()
    book = os.path.join(d, "book.txt")
    open(book, "wb").write(SAMPLE.encode("gb18030"))
    class A: pass
    x = A(); x.book = book; x.output = d + "/o"; x.split_chars = 6000; x.max_chars = 120
    cmd_plan(x)
    x.voice = x.actor_id = x.dialogue_voice = x.dialogue_actor_id = None
    x.dry_run, x.chapters, x.speed, x.model, x.read_titles = True, None, None, None, True
    x.gap, x.chapter_gap, x.peak = 0.35, 1.0, -1.0
    cmd_build(x)
    assert os.path.getsize(d + "/o/audio/001-第一章_灯塔.wav") > 1000
    assert open(d + "/o/playlist.m3u", encoding="utf-8").read().count("#EXTINF") == 2
    print("selftest ok")
    return 0


def main():
    p = argparse.ArgumentParser(prog="audiobook.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("selftest", help="offline self test").set_defaults(fn=cmd_selftest)
    for name in ("plan", "build"):
        c = s.add_parser(name)
        c.add_argument("book")
        c.add_argument("-o", "--output", default="audiobook_out")
        c.add_argument("--split-chars", type=int, default=6000, help="no chapter headings: cut every N characters")
        c.add_argument("--max-chars", type=int, default=120, help="longest sentence sent in one request")
        if name == "build":
            c.add_argument("--voice", help="narrator: exact role name in your account")
            c.add_argument("--actor-id", help="narrator: role ID")
            c.add_argument("--dialogue-voice", help="optional second role for quoted speech")
            c.add_argument("--dialogue-actor-id")
            c.add_argument("--chapters", help="e.g. 1-3,5 (default: all)")
            c.add_argument("--speed", type=float)
            c.add_argument("--model", choices=("expressive", "standard"))
            c.add_argument("--gap", type=float, default=0.35, help="seconds between sentences")
            c.add_argument("--chapter-gap", type=float, default=1.0, help="seconds after the chapter title")
            c.add_argument("--no-titles", dest="read_titles", action="store_false", help="do not read chapter titles")
            c.add_argument("--peak", type=float, default=-1.0, help="normalise each chapter to this peak dBFS")
            c.add_argument("--dry-run", action="store_true", help="offline: placeholder tones, no key, no API call")
        c.set_defaults(fn=cmd_plan if name == "plan" else cmd_build)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    K.run(main)
