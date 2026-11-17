#!/usr/bin/env python3
"""Video/audio -> editable script -> new voiceover, on top of the official client (miragea_audio.py).

  python3 scripts/video_copy.py extract MEDIA -o OUT [--dry-run]   recognize speech -> OUT/transcript.txt, transcript.srt, rewrite.md
  python3 scripts/video_copy.py revoice rewrite.md -o OUT [--voice ROLE_NAME] [--dry-run]   edited rewrite.md -> voiceover via scripts/voiceover.py
  python3 scripts/video_copy.py selftest                            offline self check

extract uses the client's real `recognize` subcommand (srt + txt). --dry-run uses a bundled sample
transcript, needs no key and makes no API call. Python 3.9+ standard library only.
"""
import argparse, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.join(HERE, "miragea_audio.py")
VOICE = os.path.join(HERE, "voiceover.py")
SAMPLE = ["大家好，今天讲三个提升睡眠质量的小习惯。", "第一，睡前一小时放下手机。", "第二，固定每天起床的时间。", "第三，卧室保持安静和偏暗。", "坚持一周，你会感受到变化。"]
SPLIT = re.compile(r"(?<=[。！？!?；;])")


def sentences(text):
    out = []
    for para in text.replace("\r", "").split("\n"):
        for s in SPLIT.split(para):
            s = s.strip()
            if s:
                out.append(s)
    return out


def write(path, s):
    if os.path.exists(path):
        os.remove(path)
    open(path, "w", encoding="utf-8").write(s)


def run_recognize(media, out, fmt):
    p = os.path.join(out, "transcript." + fmt)
    if os.path.exists(p):
        os.remove(p)
    r = subprocess.run([sys.executable, CLIENT, "recognize", "--file", media, "--wait", "--subtitle-format", fmt, "--output", p],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write((r.stdout + r.stderr)[-600:] + "\n")
        raise SystemExit(r.returncode or 1)
    return p


def cmd_extract(a):
    os.makedirs(a.output, exist_ok=True)
    if a.dry_run:
        txt = "\n".join(SAMPLE) + "\n"
        write(os.path.join(a.output, "transcript.txt"), txt)
        srt = "".join("%d\n00:00:%02d,000 --> 00:00:%02d,800\n%s\n\n" % (i + 1, i * 3, i * 3 + 2, s) for i, s in enumerate(SAMPLE))
        write(os.path.join(a.output, "transcript.srt"), srt)
        lines = SAMPLE
    else:
        if not os.environ.get("MIRAGEA_API_KEY"):
            sys.stderr.write("MIRAGEA_API_KEY 未设置：请先设置环境变量，或加 --dry-run 离线试跑。\n")
            raise SystemExit(2)
        if not os.path.isfile(a.media):
            sys.stderr.write("找不到文件: %s\n" % a.media)
            raise SystemExit(2)
        run_recognize(a.media, a.output, "srt")
        t = run_recognize(a.media, a.output, "txt")
        lines = sentences(open(t, encoding="utf-8").read())
    sheet = ["---", "# 主播的音色：在下一行写 voice=角色名称 或 actor_id=角色ID（miragea_audio.py actors 查；没有角色先 create-actor），",
             "# 或者 revoice 时加 --voice 角色名称",
             "主播:", "---", "",
             "# 下面 # 开头的行是识别出的原文（不会被朗读）。请只做自己的原创改写，写在 [主播] 行里；不要照搬他人文案。"]
    for i, s in enumerate(lines, 1):
        sheet += ["# 原文%d: %s" % (i, s), "[主播] "]
    write(os.path.join(a.output, "rewrite.md"), "\n".join(sheet) + "\n")
    print("wrote %s/transcript.txt, transcript.srt, rewrite.md (%d sentences)%s" % (a.output, len(lines), "  [dry-run: sample transcript, no API call]" if a.dry_run else ""))


def cmd_revoice(a):
    body = open(a.file, encoding="utf-8").read()
    filled = [l for l in body.splitlines() if re.match(r"^\s*\[[^\]]+\]\s*\S", l) and not l.strip().startswith(("<!--", "#"))]
    if not filled:
        sys.stderr.write("rewrite.md 里还没有写任何改写句（[主播] 后面为空）。\n")
        raise SystemExit(2)
    cmd = [sys.executable, VOICE, "script", a.file, "-o", a.output]
    if a.voice:
        cmd += ["--voice", a.voice]
    if a.actor_id:
        cmd += ["--actor-id", a.actor_id]
    if a.dry_run:
        cmd.append("--dry-run")
    raise SystemExit(subprocess.call(cmd))


def cmd_selftest(a):
    assert sentences("你好。今天！\n明天？") == ["你好。", "今天！", "明天？"]
    import tempfile
    d = tempfile.mkdtemp()
    class A: pass
    x = A(); x.output = d + "/o"; x.dry_run = True; x.media = ""
    cmd_extract(x)
    assert os.path.getsize(d + "/o/rewrite.md") > 100
    print("selftest ok")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="c", required=True)
    e = s.add_parser("extract"); e.add_argument("media", nargs="?", default=""); e.add_argument("-o", "--output", default="out"); e.add_argument("--dry-run", action="store_true"); e.set_defaults(f=cmd_extract)
    r = s.add_parser("revoice"); r.add_argument("file"); r.add_argument("-o", "--output", default="out_voice"); r.add_argument("--dry-run", action="store_true"); r.add_argument("--voice", help="exact role name in the account"); r.add_argument("--actor-id"); r.set_defaults(f=cmd_revoice)
    t = s.add_parser("selftest"); t.set_defaults(f=cmd_selftest)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
