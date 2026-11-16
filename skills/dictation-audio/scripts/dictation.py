#!/usr/bin/env python3
"""Dictation audio (听写音频): a word list -> one numbered dictation track with writing pauses + answer key.

  python3 scripts/dictation.py selftest                         offline self test (no key, no network)
  python3 scripts/dictation.py check WORDS.txt [--repeat 2 --gap 6]    offline: items and estimated length
  python3 scripts/dictation.py build WORDS.txt -o OUT --voice 角色名 [--say word|hint|both] [--repeat 2]
                                      [--gap 6] [--number zh|en|none] [--shuffle --seed 7] [--language en] [--dry-run]

WORDS.txt: one item per line, optionally `词条 | 提示`: e.g. `apple | 苹果`, `春天 | 春天的春`, or a whole
sentence for 句子听写. `#` lines are comments; a line `== 第一单元 ==` starts a new section (read aloud).
--say word   read the item (default; Chinese words, English words, sentences)
--say hint   read only the hint (e.g. the Chinese meaning) -> pupils write the English word
--say both   read the item, then the hint
--language   language hint sent with the item (e.g. en for English words); hints and numbers use --hint-language

Outputs in OUT/: dictation.wav, answer_key.txt (numbered, in the order played), dictation.lrc + dictation.srt
(timeline), info.json, cache/ (every word / number is generated once and reused).
Python 3.9+ standard library only. MIT licence (see LICENSE.txt).
"""
import argparse
import json
import os
import random
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_kit as K  # noqa: E402

VERSION = "1.0.0"
SECTION_RE = re.compile(r"^\s*={2,}\s*(.+?)\s*={2,}\s*$")
EN_NUM = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
          "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]


def parse(path):
    items, section = [], None
    for raw in open(path, encoding="utf-8-sig").read().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = SECTION_RE.match(line)
        if m:
            section = m.group(1)
            items.append({"section": section})
            continue
        word, _, hint = (x.strip() for x in line.partition("|"))
        if word:
            items.append({"word": word, "hint": hint or None})
    if not any("word" in i for i in items):
        raise K.KitError("词表里没有词条：每行一个，可写成 `词条 | 提示`")
    return items


def en_number(n):
    if n <= 20:
        return EN_NUM[n]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    if n < 100:
        return tens[n // 10] + ("-" + EN_NUM[n % 10] if n % 10 else "")
    return str(n)


def number_text(n, style):
    if style == "zh":
        return "第%d个" % n
    if style == "en":
        return "Number %s." % en_number(n)
    return None


def order(items, shuffle, seed):
    """Keep sections in place; shuffle the words inside each section."""
    if not shuffle:
        return items
    rnd = random.Random(seed)
    out, block = [], []
    for it in items + [{"section": None}]:
        if "section" in it:
            rnd.shuffle(block)
            out += block
            block = []
            if it["section"] is not None:
                out.append(it)
        else:
            block.append(it)
    return out


def spoken(it, say):
    w, h = it["word"], it.get("hint")
    if say == "hint":
        if not h:
            raise K.KitError("--say hint 需要每行都写提示：`词条 | 提示`，缺少：%s" % w)
        return [(h, "hint")]
    if say == "both" and h:
        return [(w, "word"), (h, "hint")]
    return [(w, "word")]


def estimate(items, a):
    total = 0.0
    for it in items:
        if "section" in it:
            total += K.estimate_seconds(it["section"]) + 1.5
            continue
        total += 1.2 if a.number != "none" else 0
        parts = spoken(it, a.say)
        total += a.repeat * sum(K.estimate_seconds(t) for t, _ in parts) + (a.repeat - 1) * a.repeat_gap + a.gap
    return total


def cmd_check(a):
    items = order(parse(a.words), a.shuffle, a.seed)
    n = sum(1 for i in items if "word" in i)
    print("%d 个词条，每个读 %d 遍、留 %.0f 秒书写 → 全长约 %.1f 分钟（粗估）" % (n, a.repeat, a.gap, estimate(items, a) / 60))
    k = 0
    for it in items:
        if "section" in it:
            print("  == %s ==" % it["section"])
        else:
            k += 1
            print("  %2d. %s%s" % (k, it["word"], "  | " + it["hint"] if it.get("hint") else ""))
    return 0


def cmd_build(a):
    K.check_speed(a.speed)
    if a.repeat < 1 or a.repeat > 5:
        raise K.KitError("--repeat 取 1–5")
    items = order(parse(a.words), a.shuffle, a.seed)
    for it in items:
        if "word" in it:
            spoken(it, a.say)
    K.require_key(a.dry_run)
    v = ["--dry-run"] if a.dry_run else K.voice_args(a.voice, a.actor_id)
    out = a.output
    cache = os.path.join(out, "cache")
    os.makedirs(out, exist_ok=True)

    def say(text, lang, label):
        return K.generate(text, v, cache, a.dry_run, model=a.model, speed=a.speed, language=lang, label=label)

    pcm, cues, t, k, key = K.silence(0.5), [], 0.5, 0, []
    total = sum(1 for i in items if "word" in i)
    for it in items:
        if "section" in it:
            audio = say(it["section"], a.hint_language, it["section"])
            cues.append((t, t + K.duration(audio), "== %s ==" % it["section"]))
            pcm += audio + K.silence(1.5)
            t += K.duration(audio) + 1.5
            key.append("\n%s" % it["section"])
            continue
        k += 1
        start = t
        nt = number_text(k, a.number)
        if nt:
            audio = say(nt, "en" if a.number == "en" else a.hint_language, "%d/%d" % (k, total))
            pcm += audio + K.silence(0.6)
            t += K.duration(audio) + 0.6
        parts = spoken(it, a.say)
        for r in range(a.repeat):
            for text, kind in parts:
                audio = say(text, a.language if kind == "word" else a.hint_language, "%d/%d  %s" % (k, total, text[:20]))
                pcm += audio + K.silence(0.4)
                t += K.duration(audio) + 0.4
            if r + 1 < a.repeat:
                pcm += K.silence(a.repeat_gap)
                t += a.repeat_gap
        cues.append((start, t, "%d. %s" % (k, it["word"] if a.say != "hint" else it["hint"])))
        pcm += K.silence(a.gap)
        t += a.gap
        key.append("%d. %s%s" % (k, it["word"], "　（%s）" % it["hint"] if it.get("hint") else ""))
    pcm = K.normalize(pcm, a.peak)
    K.write_wav(os.path.join(out, "dictation.wav"), pcm)
    title = os.path.splitext(os.path.basename(a.words))[0]
    open(os.path.join(out, "answer_key.txt"), "w", encoding="utf-8").write(
        "听写答案：%s（共 %d 个，按播放顺序）\n%s\n" % (title, total, "\n".join(key)))
    K.write_lrc(os.path.join(out, "dictation.lrc"), cues, title)
    K.write_srt(os.path.join(out, "dictation.srt"), cues)
    json.dump({"items": total, "seconds": round(t, 2), "repeat": a.repeat, "gap": a.gap, "say": a.say, "shuffle": a.shuffle,
               "seed": a.seed, "dry_run": a.dry_run}, open(os.path.join(out, "info.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%d 个词条，%.1f 分钟 → %s/dictation.wav + answer_key.txt + dictation.lrc%s" % (
        total, t / 60, out, "  [dry-run：占位提示音，未调用接口]" if a.dry_run else ""))
    return 0


def cmd_selftest(a):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "w.txt")
    open(p, "w", encoding="utf-8").write("== Unit 1 ==\napple | 苹果\nbanana | 香蕉\n# c\norange | 橙子\n")
    items = parse(p)
    assert items[0] == {"section": "Unit 1"} and items[1] == {"word": "apple", "hint": "苹果"}
    sh = order(items, True, 7)
    assert sh[0] == {"section": "Unit 1"} and sorted(i["word"] for i in sh[1:]) == ["apple", "banana", "orange"]
    assert en_number(21) == "twenty-one" and number_text(3, "zh") == "第3个"
    class A: pass
    x = A(); x.words = p; x.output = d + "/o"; x.voice = x.actor_id = x.model = x.speed = None
    x.dry_run, x.say, x.repeat, x.repeat_gap, x.gap, x.number, x.shuffle, x.seed = True, "both", 2, 1.0, 4.0, "en", True, 7
    x.language, x.hint_language, x.peak = "en", "zh", -1.0
    cmd_build(x)
    keytxt = open(d + "/o/answer_key.txt", encoding="utf-8").read()
    assert "1. " in keytxt and "（苹果）" in keytxt, keytxt
    assert json.load(open(d + "/o/info.json"))["items"] == 3
    print("selftest ok")
    return 0


def main():
    p = argparse.ArgumentParser(prog="dictation.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("selftest").set_defaults(fn=cmd_selftest)
    for name in ("check", "build"):
        c = s.add_parser(name)
        c.add_argument("words")
        c.add_argument("--say", choices=("word", "hint", "both"), default="word")
        c.add_argument("--repeat", type=int, default=2, help="times each item is read (1-5)")
        c.add_argument("--repeat-gap", type=float, default=1.5, help="seconds between repeats")
        c.add_argument("--gap", type=float, default=6.0, help="writing time after each item (s)")
        c.add_argument("--number", choices=("zh", "en", "none"), default="zh", help="announce 第N个 / Number N")
        c.add_argument("--shuffle", action="store_true", help="shuffle inside each section")
        c.add_argument("--seed", type=int, default=1, help="same seed = same order (for the answer key)")
        if name == "build":
            c.add_argument("-o", "--output", default="dictation_out")
            c.add_argument("--voice", help="exact role name in your account")
            c.add_argument("--actor-id")
            c.add_argument("--language", help="language hint for the items, e.g. en or zh")
            c.add_argument("--hint-language", default="zh", help="language hint for hints, numbers and section titles")
            c.add_argument("--speed", type=float, help="0.25-4; slower (0.8-0.9) suits younger pupils")
            c.add_argument("--model", choices=("expressive", "standard"))
            c.add_argument("--peak", type=float, default=-1.0)
            c.add_argument("--dry-run", action="store_true", help="offline: placeholder tones, no key, no API call")
        c.set_defaults(fn=cmd_check if name == "check" else cmd_build)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    K.run(main)
