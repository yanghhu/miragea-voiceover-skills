#!/usr/bin/env python3
"""Picture-book / bedtime-story voicing (睡前故事·绘本配音): a page-by-page story text -> one story audio, one audio per page,
subtitles and a page timing table. Narrator and characters can use different account roles; a soft page-turn chime and a
pause separate pages.

  python3 scripts/picture_book.py selftest
  python3 scripts/picture_book.py cast STORY.txt
  python3 scripts/picture_book.py plan STORY.txt [--speed 0.9]
  python3 scripts/picture_book.py build STORY.txt -o OUT [--voice 旁白角色] [--role 小熊=角色名 ...] [--speed 0.9] [--dry-run]

Story file (UTF-8 text): a line `## 第1页` (or `## page 1`) starts a page; a line `角色名：台词` is spoken by that role,
any other line is narration (role 旁白). Lines starting with `#` (single) are notes. Without --role a character uses the
narrator voice. Outputs: OUT/story.wav, OUT/pages/pageNN.wav, story.srt, pages.csv, cache/ (a sentence is generated once).
Python 3.9+ standard library only. MIT licence.
"""
import argparse, csv, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_kit as K  # noqa: E402

VERSION = "1.0.0"
PAGE_RE = re.compile(r"^\s*##\s*(?:第\s*([0-9]+)\s*页|page\s*([0-9]+))?\s*(.*)$", re.I)
ROLE_RE = re.compile(r"^\s*([^\s：:#\[\]]{1,12})\s*[：:]\s*(.+)$")
NARR = "旁白"


def parse(path):
    raw = open(path, encoding="utf-8-sig").read().replace("\r", "")
    pages, cur, title = [], None, ""
    for line in raw.split("\n"):
        if not line.strip():
            continue
        m = PAGE_RE.match(line)
        if m and line.lstrip().startswith("##"):
            cur = {"no": len(pages) + 1, "lines": []}
            pages.append(cur)
            continue
        if line.lstrip().startswith("#"):
            if not title:
                title = line.lstrip("# ").strip()
            continue
        if cur is None:
            cur = {"no": 1, "lines": []}
            pages.append(cur)
        m = ROLE_RE.match(line)
        if m:
            cur["lines"].append((m.group(1), m.group(2).strip()))
        else:
            cur["lines"].append((NARR, line.strip()))
    pages = [p for p in pages if p["lines"]]
    if not pages:
        raise K.KitError("故事里没有可朗读的文字：用 ## 第1页 分页，每行一句旁白，或写 小熊：台词")
    for i, p in enumerate(pages, 1):
        p["no"] = i
    return title, pages


def role_map(pairs):
    out = {}
    for p in pairs or []:
        if "=" not in p:
            raise K.KitError("--role 要写成 角色名=账号里的角色名称，例如 --role 小熊=我的声音")
        k, v = p.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def cmd_cast(a):
    _, pages = parse(a.story)
    stat = {}
    for p in pages:
        for r, t in p["lines"]:
            c = stat.setdefault(r, [0, 0, set()])
            c[0] += 1
            c[1] += len(t)
            c[2].add(p["no"])
    print("共 %d 页，%d 个角色" % (len(pages), len(stat)))
    for r, (n, ch, ps) in sorted(stat.items(), key=lambda x: -x[1][1]):
        print("%s\t%d 句\t%d 字\t出现在第 %s 页" % (r, n, ch, ",".join(str(x) for x in sorted(ps))))
    return 0


def page_seconds(p, speed):
    f = 1.0 / (speed or 1.0)
    return sum(K.estimate_seconds(t) for _, t in p["lines"]) * f + 0.5 * len(p["lines"])


def cmd_plan(a):
    _, pages = parse(a.story)
    t = 0.0
    for p in pages:
        s = page_seconds(p, a.speed)
        print("第%d页  %s  约 %.0f 秒  %d 句  %s" % (p["no"], K.ts(t, ".")[:8], s, len(p["lines"]), p["lines"][0][1][:16]))
        t += s + a.page_gap
    print("共 %d 页，预计总长约 %.1f 分钟（粗估，以 build 实测为准）" % (len(pages), t / 60))
    return 0


def cmd_build(a):
    K.check_speed(a.speed)
    title, pages = parse(a.story)
    K.require_key(a.dry_run)
    rmap = role_map(a.role)
    voices = {}

    def vargs_for(role):
        if a.dry_run:
            return ["--dry-run"]
        if role not in voices:
            if role in rmap:
                voices[role] = K.voice_args(rmap[role], None)
            else:
                voices[role] = K.voice_args(a.voice, a.actor_id)
        return voices[role]
    out_dir = a.output
    cache = os.path.join(out_dir, "cache")
    os.makedirs(os.path.join(out_dir, "pages"), exist_ok=True)
    story, cues, rows = K.silence(a.lead), [], []
    chime = K.gain(K.chime(), -8)
    for p in pages:
        page, t0 = K.silence(0.0), K.duration(story)
        for role, text in p["lines"]:
            start = K.duration(story) + K.duration(page)
            seg = None
            for sent in K.sentences(text):
                w = K.generate(sent, vargs_for(role), cache, a.dry_run, model=a.model, speed=a.speed, language=a.language,
                               label="第%d页 %s" % (p["no"], role))
                seg = w if seg is None else seg + K.silence(0.3) + w
            page = page + seg + K.silence(a.line_gap)
            cues.append((start, start + K.duration(seg), "%s：%s" % (role, text) if role != NARR else text))
        wavp = os.path.join(out_dir, "pages", "page%02d.wav" % p["no"])
        K.write_wav(wavp, K.normalize(page, a.peak))
        story = story + page
        rows.append((p["no"], K.ts(t0, ".")[:8], round(K.duration(page), 1), len(p["lines"])))
        if p["no"] < len(pages):
            story = story + (K.silence(0.2) + chime if a.chime else K.silence(0)) + K.silence(a.page_gap)
    story = story + K.silence(a.tail)
    K.write_wav(os.path.join(out_dir, "story.wav"), K.normalize(story, a.peak))
    K.write_srt(os.path.join(out_dir, "story.srt"), cues)
    with open(os.path.join(out_dir, "pages.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["page", "start", "seconds", "lines"])
        w.writerows(rows)
    print("%d 页 → %s/（story.wav / pages/ / story.srt / pages.csv）成品约 %.1f 分钟%s" % (
        len(pages), out_dir, K.duration(story) / 60, "  [dry-run：占位提示音，未调用接口]" if a.dry_run else ""))
    return 0


def cmd_selftest(a):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "s.txt")
    open(p, "w", encoding="utf-8").write("# 小熊睡觉\n## 第1页\n夜深了。\n小熊：我困了。\n## 第2页\n星星亮了。\n")
    t, pages = parse(p)
    assert t == "小熊睡觉" and len(pages) == 2 and pages[0]["lines"][1] == ("小熊", "我困了。"), pages
    try:
        role_map(["坏"])
        raise SystemExit("role_map should fail")
    except K.KitError:
        pass
    class A: pass
    x = A(); x.story = p; x.output = d + "/o"; x.voice = x.actor_id = x.model = x.language = None; x.role = ["小熊=某角色"]
    x.speed, x.lead, x.tail, x.peak, x.line_gap, x.page_gap, x.chime, x.dry_run = 0.9, 1.0, 2.0, -1.0, 0.5, 1.5, True, True
    cmd_build(x)
    for f in ("story.wav", "story.srt", "pages.csv", "pages/page01.wav", "pages/page02.wav"):
        assert os.path.exists(d + "/o/" + f), f
    print("selftest ok")
    return 0


def main():
    p = argparse.ArgumentParser(prog="picture_book.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("selftest").set_defaults(fn=cmd_selftest)
    s.add_parser("cast").set_defaults(fn=cmd_cast)
    s.choices["cast"].add_argument("story")
    for name in ("plan", "build"):
        c = s.add_parser(name)
        c.add_argument("story")
        c.add_argument("--speed", type=float, default=0.9)
        c.add_argument("--page-gap", type=float, default=1.5, help="silence after the page-turn chime (s)")
        if name == "build":
            c.add_argument("-o", "--output", default="story_out")
            c.add_argument("--voice", help="narrator account role name")
            c.add_argument("--actor-id", help="narrator role ID")
            c.add_argument("--role", action="append", help="角色名=账号角色名称，可重复")
            c.add_argument("--language")
            c.add_argument("--model", choices=("expressive", "standard"))
            c.add_argument("--lead", type=float, default=1.5)
            c.add_argument("--tail", type=float, default=2.5)
            c.add_argument("--line-gap", type=float, default=0.5)
            c.add_argument("--peak", type=float, default=-1.0)
            c.add_argument("--no-chime", dest="chime", action="store_false")
            c.add_argument("--dry-run", action="store_true")
        c.set_defaults(fn=cmd_plan if name == "plan" else cmd_build)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    K.run(main)
