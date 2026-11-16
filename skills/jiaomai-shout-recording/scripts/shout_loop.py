#!/usr/bin/env python3
"""Hawker / shop announcement recordings (叫卖录音 / 喊话录音 / 店铺促销广播) for loudspeakers.

  python3 scripts/shout_loop.py selftest                         offline self test (no key, no network)
  python3 scripts/shout_loop.py templates [-o DIR]               list (or save) the built-in example scripts
  python3 scripts/shout_loop.py check SCRIPT.txt [--loop-minutes 10]   offline: lines, estimated length, loop count
  python3 scripts/shout_loop.py build SCRIPT.txt -o OUT --voice 角色名 [--loop-minutes 10] [--chime] [--dry-run]
  python3 scripts/shout_loop.py build --text "清仓大甩卖，全场十元三件！" -o OUT --voice 角色名

SCRIPT.txt: one slogan per line, read in order; `#` lines are comments; a line `[停顿 2]` / `[pause 2]`
inserts that many seconds. Each line may start with `(语气标签)` to pass a tag to the API, e.g. `(激昂)快来看！`
(labels must exist in `miragea_audio.py capabilities`).

Outputs in OUT/: single.wav (one pass, for checking), loop.wav (full passes repeated until at least
--loop-minutes, with --loop-gap seconds between passes), script.txt, info.json, cache/.
Loudspeakers and megaphones usually play MP3 from a USB stick / TF card: convert with ffmpeg (see SKILL.md).
Python 3.9+ standard library only. MIT licence (see LICENSE.txt).
"""
import argparse
import json
import math
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_kit as K  # noqa: E402

VERSION = "1.0.0"
PAUSE_RE = re.compile(r"^\s*\[(?:pause|停顿)\s*([\d.]+)\s*(?:s|秒)?\]\s*$", re.I)
TAG_RE = re.compile(r"^\s*[（(]([^）)]{1,8})[）)]\s*(.+)$")

TEMPLATES = {
    "地摊清仓": ["走过路过不要错过，清仓处理，全场十元三件！", "款式多多，先到先挑，挑到就是赚到！", "最后几天，卖完就收摊，快来看一看！"],
    "水果摊": ["新鲜到货的砂糖橘，又甜又多汁！", "五块钱一斤，十块钱三斤，可以先尝后买！", "当天现摘，不甜不要钱！"],
    "早餐铺": ["热乎乎的包子豆浆，刚出锅！", "鲜肉包、菜包、豆沙包，两块钱一个！", "上班上学的朋友，带一份早餐再出发！"],
    "超市闭店": ["[停顿 0.5]", "亲爱的顾客朋友们，本店将在三十分钟后结束今天的营业。", "请您抓紧时间选购，到收银台结账。", "感谢您的光临，祝您生活愉快，欢迎明天再来！"],
    "门店促销": ["店庆三天，全场商品八折起！", "会员到店消费再送精美礼品一份！", "活动时间有限，欢迎进店选购！"],
    "旧物回收": ["回收旧手机、旧电脑、旧家电！", "上门回收，现场称重，当面结算！", "有需要的朋友请到门口找我们！"],
}


def parse(text):
    items = []
    for raw in text.replace("\r", "").split("\n"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = PAUSE_RE.match(line)
        if m:
            items.append({"pause": float(m.group(1))})
            continue
        tag, body = None, line
        m = TAG_RE.match(line)
        if m:
            tag, body = m.group(1), m.group(2)
        items.append({"text": body.strip(), "tag": tag})
    if not any("text" in i for i in items):
        raise K.KitError("稿件里没有可读的句子：每行写一句叫卖词，# 开头的行是注释。")
    return items


def load(a):
    if a.text:
        return parse(a.text.replace("\\n", "\n"))
    if not a.script:
        raise K.KitError("请给出稿件文件，或用 --text \"叫卖词\"")
    return parse(open(a.script, encoding="utf-8-sig").read())


def plan_loop(single, minutes, loop_gap):
    target = minutes * 60
    if target <= 0:
        return 1
    return max(1, int(math.ceil((target + loop_gap) / (single + loop_gap))))


def cmd_check(a):
    items = load(a)
    est = sum(i.get("pause", 0) or K.estimate_seconds(i.get("text", "")) + a.gap for i in items)
    n = plan_loop(est, a.loop_minutes, a.loop_gap)
    print("%d 句，单遍约 %.1f 秒（粗估）；循环 %d 遍 ≈ %.1f 分钟" % (sum(1 for i in items if "text" in i), est, n,
          (n * est + (n - 1) * a.loop_gap) / 60))
    for i in items:
        print("  " + ("[停顿 %.1f 秒]" % i["pause"] if "pause" in i else ("(%s) " % i["tag"] if i["tag"] else "") + i["text"]))
    return 0


def cmd_build(a):
    K.check_speed(a.speed)
    items = load(a)
    K.require_key(a.dry_run)
    v = ["--dry-run"] if a.dry_run else K.voice_args(a.voice, a.actor_id)
    out = a.output
    os.makedirs(out, exist_ok=True)
    one = K.silence(a.lead)
    if a.chime:
        one += K.chime() + K.silence(0.3)
    lines = []
    for n, it in enumerate(items, 1):
        if "pause" in it:
            one += K.silence(it["pause"])
            continue
        tags = [it["tag"]] if it.get("tag") else a.tag
        audio = K.generate(it["text"], v, os.path.join(out, "cache"), a.dry_run, model=a.model, speed=a.speed,
                           tags=tags, label="%d/%d  %s" % (n, len(items), it["text"][:30]))
        one += audio + K.silence(a.gap)
        lines.append(it["text"])
    one = K.normalize(one, a.peak)
    single = K.duration(one)
    K.write_wav(os.path.join(out, "single.wav"), one)
    passes = plan_loop(single, a.loop_minutes, a.loop_gap)
    loop = K.silence(0)
    for i in range(passes):
        loop += one
        if i + 1 < passes:
            loop += K.silence(a.loop_gap)
    K.write_wav(os.path.join(out, "loop.wav"), loop)
    open(os.path.join(out, "script.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    info = {"single_seconds": round(single, 2), "passes": passes, "loop_seconds": round(K.duration(loop), 2),
            "speed": a.speed, "chime": a.chime, "peak_dbfs": a.peak, "dry_run": a.dry_run}
    json.dump(info, open(os.path.join(out, "info.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("单遍 %.1f 秒 → %s/single.wav；循环 %d 遍共 %.1f 分钟 → loop.wav%s" % (
        single, out, passes, K.duration(loop) / 60, "  [dry-run：占位提示音，未调用接口]" if a.dry_run else ""))
    return 0


def cmd_templates(a):
    for name, lines in TEMPLATES.items():
        if a.output:
            os.makedirs(a.output, exist_ok=True)
            open(os.path.join(a.output, name + ".txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("【%s】" % name)
        for l in lines:
            print("  " + l)
    if a.output:
        print("已保存到 %s/（每个场景一个 .txt，改成你自己的商品和价格再用）" % a.output)
    return 0


def cmd_selftest(a):
    items = parse("# 注释\n(激昂)快来看！\n[停顿 1.5]\n十元三件。")
    assert items == [{"text": "快来看！", "tag": "激昂"}, {"pause": 1.5}, {"text": "十元三件。", "tag": None}], items
    assert plan_loop(10, 1, 2) == 6
    d = tempfile.mkdtemp()
    class A: pass
    x = A(); x.text = "\n".join(TEMPLATES["地摊清仓"]); x.script = None; x.output = d
    x.voice = x.actor_id = x.model = x.speed = None; x.tag = []
    x.dry_run, x.chime, x.lead, x.gap, x.loop_gap, x.loop_minutes, x.peak = True, True, 0.2, 0.6, 2.0, 0.5, -1.0
    cmd_build(x)
    info = json.load(open(d + "/info.json"))
    assert info["loop_seconds"] >= 30 and info["passes"] >= 2, info
    print("selftest ok")
    return 0


def main():
    p = argparse.ArgumentParser(prog="shout_loop.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("selftest").set_defaults(fn=cmd_selftest)
    t = s.add_parser("templates"); t.add_argument("-o", "--output"); t.set_defaults(fn=cmd_templates)
    for name in ("check", "build"):
        c = s.add_parser(name)
        c.add_argument("script", nargs="?")
        c.add_argument("--text", help="slogans inline; separate lines with \\n")
        c.add_argument("--loop-minutes", type=float, default=10, help="loop.wav length target (0 = one pass)")
        c.add_argument("--loop-gap", type=float, default=2.0, help="seconds between passes")
        c.add_argument("--gap", type=float, default=0.6, help="seconds between lines")
        if name == "build":
            c.add_argument("-o", "--output", default="shout_out")
            c.add_argument("--voice", help="exact role name in your account")
            c.add_argument("--actor-id")
            c.add_argument("--speed", type=float, help="0.25-4; hawking usually sounds right around 1.1-1.2")
            c.add_argument("--model", choices=("expressive", "standard"))
            c.add_argument("--tag", action="append", default=[], help="tone tag for lines without (标签)")
            c.add_argument("--chime", action="store_true", help="ding-dong before each pass (shop announcements)")
            c.add_argument("--lead", type=float, default=0.3, help="silence at the start of each pass")
            c.add_argument("--peak", type=float, default=-1.0, help="peak level dBFS (louder = closer to 0)")
            c.add_argument("--dry-run", action="store_true", help="offline: placeholder tones, no key, no API call")
        c.set_defaults(fn=cmd_check if name == "check" else cmd_build)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    K.run(main)
