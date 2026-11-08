#!/usr/bin/env python3
"""Podcast show notes from a voiced script: chapters with timestamps + full transcript.

  python3 scripts/shownotes.py SCRIPT.md out [--title "第12期 ..."] [--offset 0]

Reads SCRIPT.md (the same file given to `voiceover.py script`) and out/manifest.json, and writes
  out/shownotes.md     title, chapter list `00:00 开场`, speaker-labelled transcript
  out/chapters.json    [{"title", "start"}] for players or editors that import chapters
  out/chapters.txt     one `HH:MM:SS 标题` per line, ready to paste into a podcast platform

Chapters are the `## 标题` lines in the script (they are not read aloud). `--offset` adds seconds
to every timestamp, e.g. the length of an intro music bed placed before the voice.
Python 3.9+ standard library only. MIT licence (see LICENSE.txt).
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voiceover import LINE_RE, PAUSE_RE  # same line grammar as the voiceover script


def stamp(sec, long_form):
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return "%02d:%02d:%02d" % (h, m, s) if long_form else "%02d:%02d" % (m, s)


def chapters_from_script(text):
    """Return [(title, index_of_next_spoken_line)] using the voiceover.py parsing rules."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    m = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n", text, re.S)
    body = text[m.end():] if m else text
    marks, spoken = [], 0
    for raw in body.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            h = re.match(r"^##\s+(.+)$", s)
            if h:
                marks.append((h.group(1).strip(), spoken))
            continue
        if PAUSE_RE.match(s):
            continue
        lm = LINE_RE.match(s)
        if lm and not lm.group("text").strip():
            continue
        spoken += 1
    return marks, spoken


def main(argv=None):
    p = argparse.ArgumentParser(description="voiced podcast script + manifest.json -> shownotes.md, chapters.json, chapters.txt")
    p.add_argument("--version", action="version", version="shownotes.py 1.0.0")
    p.add_argument("script")
    p.add_argument("outdir")
    p.add_argument("--title", default="")
    p.add_argument("--offset", type=float, default=0.0, help="seconds added to every timestamp (intro music etc.)")
    a = p.parse_args(argv)
    with open(a.script, encoding="utf-8") as f:
        marks, spoken = chapters_from_script(f.read())
    with open(os.path.join(a.outdir, "manifest.json"), encoding="utf-8") as f:
        man = json.load(f)
    lines = man["lines"]
    if len(lines) != spoken:
        raise SystemExit("manifest has %d lines but the script has %d: re-run voiceover.py script on this exact file" % (len(lines), spoken))
    total = man.get("duration", 0) + a.offset
    long_form = total >= 3600
    chapters = []
    for title, idx in marks:
        start = (lines[idx]["start"] if idx < len(lines) else man.get("duration", 0)) + a.offset
        chapters.append({"title": title, "start": round(start, 3)})
    if chapters and chapters[0]["start"] > a.offset + 0.5:
        chapters.insert(0, {"title": "开场", "start": round(a.offset, 3)})
    with open(os.path.join(a.outdir, "chapters.json"), "w", encoding="utf-8") as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)
    with open(os.path.join(a.outdir, "chapters.txt"), "w", encoding="utf-8") as f:
        for c in chapters:
            f.write("%s %s\n" % (stamp(c["start"], True), c["title"]))
    out = []
    if a.title:
        out += ["# " + a.title, ""]
    out += ["时长：%s" % stamp(total, True), ""]
    if chapters:
        out += ["## 时间轴", ""] + ["- %s %s" % (stamp(c["start"], long_form), c["title"]) for c in chapters] + [""]
    out += ["## 文字稿", ""]
    prev = None
    for l in lines:
        who = l.get("speaker") or ""
        prefix = "**%s**：" % who if who != prev else ""
        out.append("%s%s" % (prefix, l["text"]))
        out.append("")
        prev = who
    with open(os.path.join(a.outdir, "shownotes.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("wrote shownotes.md (%d chapters, %d lines) + chapters.json + chapters.txt in %s" % (len(chapters), len(lines), a.outdir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
