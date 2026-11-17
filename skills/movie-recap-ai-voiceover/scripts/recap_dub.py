#!/usr/bin/env python3
"""Movie / TV / short-drama recap voiceover (电影解说配音) on top of the official client.

  python3 scripts/recap_dub.py selftest                         offline self test (no key, no network)
  python3 scripts/recap_dub.py check SCRIPT [--cast cast.md]    offline: how every line is parsed + estimated overruns
  python3 scripts/recap_dub.py cast  SCRIPT [-o cast.md]        list speakers, write a voice sheet to fill in
  python3 scripts/recap_dub.py build SCRIPT -o OUT [--cast cast.md] [--dry-run] [--fit] [--retake 3,7]

SCRIPT may be any of (detected from the content, not only the extension):
  * a recap script (.md/.txt): untagged lines are narration;  角色：台词 / 角色（语气）：台词 / [角色|语气] 台词
      `=== 镜1 | 雨夜街口 ===` shot headers, `> 画面：...` picture notes, `[pause 0.6]` / `[停顿 0.6]`,
      optional time codes at the start of a line: `00:01:12.5 文案`, `[00:01:12-00:01:18] 文案`, `@72.5 文案`
  * a storyboard / shot list table (.csv/.tsv): 镜号 / 画面 / 开始 / 结束 / 时长 / 角色 / 文案(台词) / 语气 / 语速
  * SRT subtitles (.srt, or SRT text saved as .txt): every cue is placed at its start time; `角色：` prefixes are kept

Voices (front matter of SCRIPT or a separate --cast file):
  旁白: actor_id=ROLE_ID speed=1.0      角色: voice=账号里的角色名称
  (roles only: cloning from a reference audio URL, ref=, was removed in client 1.3.0)
  @tones: 低沉=TAG_LABEL, 紧张=TAG_LABEL   (map script tones to the account's tags[].label)

Outputs in OUT/: voiceover.wav (full mix), stems/narration.wav + stems/dialogue.wav (+ stems/roles/*.wav),
voiceover.srt, voiceover_roles.srt, cues.csv (timing sheet), manifest.json, report.md (overruns, idle picture),
lines/ (per-line cache: edit one line, only that line is regenerated).
--dry-run needs no key and makes no API call (placeholder tones with estimated length).
Python 3.9+ standard library only. MIT licence (see LICENSE.txt).
"""
import argparse
import array
import csv
import hashlib
import io
import json
import math
import os
import re
import shutil
import sys
import tempfile
import uuid
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from voiceover import ScriptError, generate_line, payload_for, read_wav, split_caption, ts  # noqa: E402

VERSION = "1.1.0"
DRY_RATE = 24000
CHARS_PER_SEC = 4.5          # rough Chinese speaking rate, used only for estimates and --dry-run
NARR_WORDS = ("narrator", "旁白", "解说", "画外音", "OS", "VO")
ALIASES = {"actor": "actor_id", "voice": "actor_name", "name": "actor_name"}
REMOVED = ("ref", "ref_text", "reference_audio_url", "reference_text")
VOICE_KEYS = ("actor_id", "actor_name", "model", "language", "speed", "tags", "track")
TC = r"\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d{1,3})?"
SHOT_RE = re.compile(r"^\s*(?:={2,}\s*(?P<a>.+?)\s*={2,}|#{2,}\s*(?P<b>.+?))\s*$")
PAUSE_RE = re.compile(r"^\s*\[(?:pause|停顿)\s*(?P<s>[\d.]+)\s*(?:s|秒)?\]\s*$", re.I)
NOTE_RE = re.compile(r"^\s*(?:<!--\s*(?P<n>.*?)\s*-->|>\s*(?P<q>.+?))\s*$")  # `> 画面：…` (older scripts: HTML comment)
TIME_RE = re.compile(r"^\s*(?:\[\s*(?P<a1>%s)\s*(?:[-–~→]+\s*(?P<a2>%s))?\s*\]|(?P<b1>%s)(?:\s*[-–~→]+\s*(?P<b2>%s))?(?=\s)|@(?P<c1>%s|\d+(?:\.\d+)?))\s*(?P<rest>.*)$"
                     % (TC, TC, TC, TC, TC))
BRACKET_RE = re.compile(r"^\s*\[(?P<who>[^\]|｜]+)(?:[|｜](?P<emo>[^\]]+))?\]\s*[:：]?\s*(?P<text>.*)$")
COLON_RE = re.compile(r"^\s*(?P<who>[^\s:：，,。！？!?（(【\[“\"]{1,10})\s*(?:[（(](?P<emo>[^）)]{1,10})[）)])?\s*[:：]\s*(?P<text>.+)$")
LEAD_EMO_RE = re.compile(r"^\s*[（(](?P<emo>[^）)]{1,10})[）)]\s*(?P<text>.*)$")
SRT_TIME_RE = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")
PLACEHOLDER_RE = re.compile(r"^(YOUR_|NARRATOR_|ACTOR_|HERO_|.*_VOICE_ID$|.*_ID$)")
COLS = {
    "shot": ("镜号", "镜头", "shot", "场次", "分镜"),
    "picture": ("画面", "画面内容", "镜头内容", "picture", "visual", "备注"),
    "speaker": ("角色", "说话人", "人物", "speaker", "role", "character"),
    "text": ("文案", "解说词", "解说", "台词", "对白", "文本", "text", "line", "narration"),
    "emotion": ("语气", "情绪", "tone", "emotion"),
    "start": ("开始", "起始", "入点", "start", "in"),
    "end": ("结束", "出点", "end", "out"),
    "duration": ("时长", "秒数", "duration", "len"),
    "speed": ("语速", "speed"),
}


class Fail(ScriptError):
    pass


# ------------------------------------------------------------------ parsing

def seconds(v):
    v = str(v).strip().replace(",", ".").rstrip("sS秒")
    if not v:
        return None
    if ":" in v:
        parts = [float(p) for p in v.split(":")]
        while len(parts) < 3:
            parts.insert(0, 0.0)
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return float(v)


def is_narrator(name, voices=None):
    if voices and (voices.get(name) or {}).get("track") in ("narration", "旁白", "解说"):
        return True
    if voices and (voices.get(name) or {}).get("track") in ("dialogue", "台词", "角色"):
        return False
    low = name.lower()
    return any(low == w.lower() or low.startswith(w.lower()) for w in NARR_WORDS)


def parse_voice(name, rest):
    v = {}
    for k, val in re.findall(r'(\w+)=("[^"]*"|\S+)', rest):
        if k in REMOVED:
            raise Fail("角色 %s 用了 %s=：音频链接直接克隆已停用（官方客户端 1.3.0 起只用账号里的角色）。先用 "
                       "python3 scripts/miragea_audio.py create-actor --file 你的录音.wav --name 角色名称 建角色，"
                       "再写 actor_id=角色ID 或 voice=角色名称" % (name, k))
        k, val = ALIASES.get(k, k), val.strip('"')
        if k == "speed":
            try:
                val = float(val)
            except ValueError:
                raise Fail("角色 %s 的 speed=%s 不是数字" % (name, val))
            if not 0.25 <= val <= 4:
                raise Fail("角色 %s 的 speed 必须在 0.25–4 之间" % name)
        elif k == "tags":
            val = [t for t in re.split(r"[,，]", val) if t]
        elif k not in VOICE_KEYS:
            raise Fail("角色 %s 有未知参数 %s=（可用：actor_id voice speed model tags language track）" % (name, k))
        v[k] = val
    if v.get("actor_id") and v.get("actor_name"):
        raise Fail("角色 %s：actor_id= 和 voice= 只写一个" % name)
    return v


def split_front(text):
    """-> (voices, tone_map, body). HTML comments that are not alone on a line are dropped."""
    voices, tmap = {}, {}
    m = re.match(r"^\ufeff?\s*---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return voices, tmap, text
    for raw in m.group(1).splitlines():
        s = raw.split("    #")[0].strip()
        if not s or s.startswith("#") or ":" not in s:
            continue
        name, rest = [x.strip() for x in s.split(":", 1)]
        if name in ("@tones", "@emotions", "@语气", "@情绪"):
            for pair in re.split(r"[,，;；]", rest):
                if "=" in pair:
                    a, b = [x.strip() for x in pair.split("=", 1)]
                    tmap[a] = [t for t in re.split(r"[+＋]", b) if t]
            continue
        voices[name] = parse_voice(name, rest)
    return voices, tmap, text[m.end():]


def split_speaker(s, known):
    m = BRACKET_RE.match(s)
    if m and not re.match(r"^(pause|停顿)\b", m.group("who"), re.I) and not re.match(r"^\s*%s" % TC, m.group("who")):
        who, emo, text = m.group("who").strip(), (m.group("emo") or "").strip(), m.group("text").strip()
    else:
        m = COLON_RE.match(s)
        w = m.group("who") if m else ""
        if m and (w in known or is_narrator(w) or (not known and len(w) <= 4)):
            who, emo, text = m.group("who").strip(), (m.group("emo") or "").strip(), m.group("text").strip()
        else:
            who, emo, text = None, "", s.strip()
    lm = LEAD_EMO_RE.match(text)
    if lm:
        emo, text = emo or lm.group("emo").strip(), lm.group("text").strip()
    return who, emo, text


def looks_like_srt(text):
    return len(SRT_TIME_RE.findall(text[:4000])) >= 1 and re.search(r"(^|\n)\s*\d+\s*\n\s*\d+:\d+:\d+[,.]\d+\s*-->", text) is not None


def parse_text(body, known, narrator):
    lines, shot, note = [], "", ""
    body = re.sub(r"<!--(?:(?!-->).)*?\n.*?-->", "", body, flags=re.S)  # multi-line comments: ignore
    for raw in body.splitlines():
        s = raw.strip()
        if not s:
            continue
        nm = NOTE_RE.match(s)
        if nm:
            note = nm.group("n") or nm.group("q")
            continue
        s = re.sub(r"<!--.*?-->", "", s).strip()
        sm = SHOT_RE.match(s)
        if sm:
            shot = (sm.group("a") or sm.group("b")).strip()
            continue
        if s.startswith("#") or not s:
            continue
        pm = PAUSE_RE.match(s)
        if pm:
            lines.append({"pause": float(pm.group("s"))})
            continue
        start = end = None
        tm = TIME_RE.match(s)
        if tm:
            t1 = tm.group("a1") or tm.group("b1") or tm.group("c1")
            t2 = tm.group("a2") or tm.group("b2")
            start, end, s = seconds(t1), (seconds(t2) if t2 else None), tm.group("rest").strip()
        who, emo, text = split_speaker(s, known)
        if not text:
            continue
        l = {"speaker": who or narrator, "emotion": emo, "text": text, "shot": shot, "picture": note, "start": start}
        if end is not None and start is not None and end > start:
            l["slot"] = end - start
        note = ""
        lines.append(l)
    return lines


def parse_table(path, narrator):
    with open(path, encoding="utf-8-sig", newline="") as f:
        sample = f.read()
    delim = "\t" if path.lower().endswith(".tsv") or sample.count("\t") > sample.count(",") else ","
    rows = [r for r in csv.reader(io.StringIO(sample), delimiter=delim) if any(c.strip() for c in r)]
    if not rows:
        raise Fail("分镜表是空的：%s" % path)
    head = [h.strip().lower() for h in rows[0]]
    idx = {}
    for key, names in COLS.items():
        for i, h in enumerate(head):
            if i in idx.values():
                continue
            if any(h == n.lower() for n in names):
                idx.setdefault(key, i)
    for key, names in COLS.items():
        for i, h in enumerate(head):
            if key not in idx and i not in idx.values() and any(h.startswith(n.lower()) for n in names):
                idx[key] = i
    if "text" not in idx:
        raise Fail("分镜表需要一列 文案 / 解说词 / 台词（text）；当前表头：%s" % "、".join(rows[0]))
    get = lambda r, k: (r[idx[k]].strip() if k in idx and idx[k] < len(r) else "")
    lines, last_shot = [], ""
    for n, r in enumerate(rows[1:], 2):
        text = get(r, "text")
        if not text:
            continue
        if get(r, "speaker"):
            lm = LEAD_EMO_RE.match(text)
            who, emo2, text2 = get(r, "speaker"), (lm.group("emo").strip() if lm else ""), (lm.group("text").strip() if lm else text)
        else:
            who, emo2, text2 = split_speaker(text, set())
        try:
            start = seconds(get(r, "start")) if get(r, "start") else None
            end = seconds(get(r, "end")) if get(r, "end") else None
            dur = seconds(get(r, "duration")) if get(r, "duration") else None
        except ValueError:
            raise Fail("分镜表第 %d 行的时间格式无法识别（支持 12.5、00:12.5、00:00:12,500）" % n)
        l = {"speaker": who or narrator, "emotion": get(r, "emotion") or emo2, "text": text2,
             "shot": get(r, "shot") or last_shot, "picture": get(r, "picture"), "start": start}
        if dur:
            l["slot"] = dur
        elif end is not None and start is not None and end > start:
            l["slot"] = end - start
        if get(r, "speed"):
            l["speed"] = float(get(r, "speed").rstrip("xX倍"))
        last_shot = l["shot"]
        lines.append(l)
    return lines


def parse_srt(text, known, narrator):
    lines = []
    for block in re.split(r"\n\s*\n", text.strip()):
        m = SRT_TIME_RE.search(block)
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0
        body = " ".join(x.strip() for x in block[m.end():].strip().splitlines() if x.strip())
        body = re.sub(r"<[^>]+>|\{[^}]+\}", "", body).strip()
        if not body:
            continue
        who, emo, txt = split_speaker(body, known)
        lines.append({"speaker": who or narrator, "emotion": emo, "text": txt, "shot": "", "picture": "",
                      "start": start, "slot": max(0.0, end - start)})
    return lines


def load(path, cast=None):
    if not os.path.exists(path):
        raise Fail("找不到稿件文件：%s（examples/ 下有可直接试跑的示例）" % path)
    with open(path, encoding="utf-8-sig") as f:
        raw = f.read()
    voices, tmap, body = split_front(raw)
    if cast:
        if not os.path.exists(cast):
            raise Fail("找不到音色表：%s（用 cast 命令生成）" % cast)
        with open(cast, encoding="utf-8-sig") as f:
            cv, ct, _ = split_front(f.read())
        voices.update(cv)
        tmap.update(ct)
    narrator = next((n for n in voices if is_narrator(n, voices)), "旁白")
    low = path.lower()
    if low.endswith((".csv", ".tsv")):
        lines, kind = parse_table(path, narrator), "table"
    elif low.endswith((".srt", ".vtt")) or looks_like_srt(body):
        lines, kind = parse_srt(body, set(voices), narrator), "srt"
    else:
        lines, kind = parse_text(body, set(voices), narrator), "script"
    if not any("text" in l for l in lines):
        raise Fail("%s 里没有找到可配音的句子" % path)
    n = 0
    for l in lines:
        if "text" in l:
            n += 1
            l["_n"] = n
            l["track"] = "narration" if is_narrator(l["speaker"], voices) else "dialogue"
    return voices, tmap, lines, kind


# ------------------------------------------------------------------ helpers

def estimate(text, speed=1.0):
    units = len(re.findall(r"[\u4e00-\u9fff]", text)) + len(re.findall(r"[A-Za-z0-9]+", text)) * 1.5
    return max(0.6, units / CHARS_PER_SEC / (speed or 1.0))


def speed_of(l, voices, fit=None):
    return (fit or {}).get(l["_n"]) or l.get("speed") or voices.get(l["speaker"], {}).get("speed") or 1.0


def tone(role_index, narration, secs):
    n = int(DRY_RATE * secs)
    freq = 180.0 if narration else 300.0 * (2 ** ((role_index % 6) / 6.0))
    fade = int(DRY_RATE * 0.03)
    buf = array.array("h", (int(1500 * min(1.0, i / fade, (n - i) / fade) * math.sin(2 * math.pi * freq * i / DRY_RATE))
                            for i in range(n)))
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(DRY_RATE)
        w.writeframes(buf.tobytes())
    return out.getvalue()


def write_wav(path, params, samples):
    with wave.open(path, "wb") as w:
        w.setnchannels(params[0])
        w.setsampwidth(2)
        w.setframerate(params[2])
        w.writeframes(samples.tobytes())


def has_voice(v):
    return bool(v.get("actor_id") or v.get("actor_name"))


def speakers(lines):
    out = {}
    for l in lines:
        if "text" in l:
            r = out.setdefault(l["speaker"], {"lines": 0, "chars": 0, "track": l["track"], "tones": {}})
            r["lines"] += 1
            r["chars"] += len(l["text"])
            if l.get("emotion"):
                r["tones"][l["emotion"]] = r["tones"].get(l["emotion"], 0) + 1
    return out


def slots(lines, locked):
    """Available seconds per line in locked mode: own slot, else until the next timed line."""
    res = {}
    if not locked:
        return res
    timed = [l for l in lines if "text" in l]
    for i, l in enumerate(timed):
        if l.get("slot"):
            res[l["_n"]] = l["slot"]
        elif l.get("start") is not None:
            nxt = next((x["start"] for x in timed[i + 1:] if x.get("start") is not None), None)
            if nxt is not None:
                res[l["_n"]] = max(0.0, nxt - l["start"])
    return res


# ------------------------------------------------------------------ commands

def cmd_check(a):
    voices, tmap, lines, kind = load(a.file, a.cast)
    sp = speakers(lines)
    locked = any(l.get("start") is not None for l in lines if "text" in l)
    sl = slots(lines, locked)
    print("输入类型 %s | 句数 %d | 说话人 %d | 带时间码 %d 句 | 模式 %s" % (
        {"script": "解说稿", "table": "分镜表", "srt": "SRT 字幕"}[kind], sum(1 for l in lines if "text" in l), len(sp),
        sum(1 for l in lines if l.get("start") is not None), "对轨" if locked else "顺排"))
    est_total, warn = 0.0, []
    for l in lines:
        if "pause" in l:
            print("     [停顿 %.2fs]" % l["pause"])
            est_total += l["pause"]
            continue
        d = estimate(l["text"], speed_of(l, voices))
        est_total += d
        at = (" @%s" % ts(l["start"])[3:]) if l.get("start") is not None else ""
        slot = sl.get(l["_n"])
        flag = ""
        if slot is not None and d > slot + 0.05:
            flag = "  ⚠ 预计 %.1fs > 画面 %.1fs" % (d, slot)
            warn.append(l["_n"])
        print("%3d  %-6s %-4s %-4s%s  %s%s" % (l["_n"], l["speaker"], "旁白" if l["track"] == "narration" else "台词",
                                             l.get("emotion") or "-", at, l["text"][:40], flag))
    print("预计总时长约 %.0f 秒（按每秒 %.1f 字估算，正式时长以生成结果为准）" % (est_total, CHARS_PER_SEC))
    missing = [r for r in sp if not has_voice(voices.get(r, {}))]
    if missing:
        print("还没有音色的说话人：%s → python3 scripts/recap_dub.py cast %s -o cast.md" % ("、".join(missing), a.file))
    if warn:
        print("预计超出画面时长的句子：%s（build 后看 report.md，或加 --fit）" % "、".join(map(str, warn)))
    return 0


def cmd_cast(a):
    voices, tmap, lines, kind = load(a.file, a.cast)
    sp = speakers(lines)
    tones = sorted({t for r in sp.values() for t in r["tones"]})
    out = ["---", "# 每个说话人一行：actor_id=账号里角色的ID，或 voice=角色名称（miragea_audio.py actors 查询；",
           "# 没有角色先 create-actor 用本人授权录音创建）；speed 0.25-4。旁白类名称自动进解说分轨。"]
    for name, r in sorted(sp.items(), key=lambda x: (x[1]["track"] != "narration", -x[1]["lines"])):
        v = voices.get(name)
        if v:
            opts = " ".join("%s=%s" % ({"actor_name": "voice"}.get(k, k),
                                       ",".join(x) if isinstance(x, list) else (json.dumps(x, ensure_ascii=False) if k == "actor_name" and " " in str(x) else x))
                            for k, x in v.items())
        else:
            opts = "actor_id=YOUR_CLONED_VOICE_ID speed=%s" % ("1.0" if r["track"] == "narration" else "1.0")
        out.append("%s: %s    # %s，%d 句 / %d 字%s" % (name, opts, "解说旁白" if r["track"] == "narration" else "角色台词",
                                                     r["lines"], r["chars"], ("，语气：" + "、".join(r["tones"])) if r["tones"] else ""))
    if tones:
        out.append("# 语气 → 语气标签：右边填 capabilities 里所选模式 tags[].label 的原文")
        out.append("@tones: " + ", ".join("%s=%s" % (t, "+".join(tmap.get(t, [])) or t) for t in tones))
    out.append("---")
    text = "\n".join(out) + "\n"
    if a.output:
        if os.path.exists(a.output) and not a.force:
            raise Fail("%s 已存在；加 --force 覆盖" % a.output)
        with open(a.output, "w", encoding="utf-8") as f:
            f.write(text)
        print("已写入 %s（%d 个说话人）" % (a.output, len(sp)), file=sys.stderr)
    print(text, end="")
    return 0


def line_payload(l, voice, tmap, a):
    v = dict(voice)
    v.pop("track", None)
    v["speed"] = a.fit_speed.get(l["_n"]) or l.get("speed") or voice.get("speed")
    tags = list(v.get("tags") or [])
    if l.get("emotion") and not a.no_tone:
        for t in tmap.get(l["emotion"], [l["emotion"]]):
            if t and t not in tags:
                tags.append(t)
    v["tags"] = tags
    return payload_for(l["text"], v, a.model)


def render_line(l, voice, tmap, a, role_index, cache, salt):
    if a.dry_run:
        return tone(role_index, l["track"] == "narration", estimate(l["text"], speed_of(l, {l["speaker"]: voice}, a.fit_speed))), None
    p = line_payload(l, voice, tmap, a)
    extra = salt + (uuid.uuid4().hex if l["_n"] in a.retake_set else "")
    digest = hashlib.sha256((json.dumps(p, sort_keys=True, ensure_ascii=False) + extra).encode()).hexdigest()
    src = os.path.join(cache, digest[:24] + ".wav")
    if not os.path.exists(src):
        print("生成第 %d 句  %s  %s" % (l["_n"], l["speaker"], l["text"][:30]), file=sys.stderr)
        a.generated += 1
        generate_line(p, src, "rc-" + digest[:40], a.wait_timeout)
    else:
        a.reused += 1
    with open(src, "rb") as f:
        return f.read(), src


def preflight(a, voices, lines):
    """Real (non dry-run) builds: refuse before any network call when the key or voices are missing."""
    if a.dry_run:
        return
    if not os.environ.get("MIRAGEA_API_KEY"):
        raise Fail("未设置 MIRAGEA_API_KEY，本次没有调用任何接口。正式配音需要 API Key 和账号里克隆好的音色；"
                   "先用 --dry-run 离线跑通（例：python3 scripts/recap_dub.py build %s -o out --dry-run），"
                   "拿到 Key 后 export MIRAGEA_API_KEY=你的key 再运行。" % a.file)
    sp = speakers(lines)
    missing = [r for r in sp if not has_voice(voices.get(r, {}))]
    if missing:
        raise Fail("这些说话人还没有音色：%s。运行 cast %s -o cast.md，填入角色的 actor_id 或 voice=角色名称（miragea_audio.py actors 查询）后加 --cast cast.md"
                   % ("、".join(missing), a.file))
    fake = [r for r in sp if PLACEHOLDER_RE.match(str(voices[r].get("actor_id") or "x"))]
    if fake:
        raise Fail("这些说话人的 actor_id 还是示例占位符：%s。换成 miragea_audio.py actors 返回的真实 actor_id" % "、".join(fake))


def cmd_build(a):
    voices, tmap, lines, kind = load(a.file, a.cast)
    a.retake_set = {int(x) for x in re.split(r"[,，\s]+", a.retake or "") if x.strip().isdigit()}
    a.fit_speed, a.generated, a.reused = {}, 0, 0
    preflight(a, voices, lines)
    sp = list(speakers(lines))
    locked = any(l.get("start") is not None for l in lines if "text" in l) and not a.sequential
    sl = slots(lines, locked)
    os.makedirs(os.path.join(a.output, "lines"), exist_ok=True)
    salt = uuid.uuid4().hex if a.fresh else ""
    passes = 2 if (a.fit and locked) else 1
    for attempt in range(passes):
        params, clips = None, {}
        for l in lines:
            if "text" not in l:
                continue
            data, src = render_line(l, voices.get(l["speaker"], {}), tmap, a, sp.index(l["speaker"]),
                                    os.path.join(a.output, "lines"), salt)
            prm, frames = read_wav(data, src or "placeholder")
            if prm[1] != 2:
                raise Fail("只能拼接 16 位 PCM WAV（%s）" % (src or "placeholder"))
            if params and prm != params:
                raise Fail("第 %d 句的 WAV 格式 %s 与前面 %s 不一致" % (l["_n"], prm, params))
            params = params or prm
            clips[l["_n"]] = (frames, src)
        ch, _, rate = params
        t, placed, prev_shot = 0.0, [], None
        for l in lines:
            if "pause" in l:
                t += l["pause"]
                continue
            frames, src = clips[l["_n"]]
            dur = len(frames) / float(ch * 2 * rate)
            if locked and l.get("start") is not None:
                start = l["start"] if a.allow_overlap else max(l["start"], t)
            else:
                if placed:
                    t += a.shot_gap if (l.get("shot") and l["shot"] != prev_shot) else a.gap
                start = t
            slot = sl.get(l["_n"])
            placed.append(dict(l, start_at=round(start, 3), end_at=round(start + dur, 3), dur=round(dur, 3), avail=slot,
                               shift=round(start - l["start"], 3) if l.get("start") is not None else 0.0, file=src, frames=frames))
            t, prev_shot = start + dur, l.get("shot")
        over = [p for p in placed if p["avail"] is not None and p["dur"] > p["avail"] + 0.05]
        if attempt == 0 and passes == 2 and over:
            for p in over:
                a.fit_speed[p["_n"]] = round(min(4.0, max(0.25, speed_of(p, voices) * p["dur"] / max(p["avail"] - 0.05, 0.1))), 2)
            print("--fit：%d 句超出画面时长，按建议语速重配" % len(over), file=sys.stderr)
            continue
        break

    total = max(p["end_at"] for p in placed)
    nframes = int(math.ceil(total * rate)) + 1
    blank = lambda: array.array("h", bytes(nframes * ch * 2))
    mix, tracks, roles = blank(), {"narration": blank(), "dialogue": blank()}, {r: blank() for r in sp}

    def add(dst, buf, off):
        for k, s in enumerate(buf):
            j = off + k
            if j >= len(dst):
                break
            v = dst[j] + s
            dst[j] = 32767 if v > 32767 else (-32768 if v < -32768 else v)

    for p in placed:
        buf = array.array("h")
        buf.frombytes(p["frames"])
        off = int(round(p["start_at"] * rate)) * ch
        for dst in (mix, tracks[p["track"]], roles[p["speaker"]]):
            add(dst, buf, off)
    os.makedirs(os.path.join(a.output, "stems", "roles"), exist_ok=True)
    write_wav(os.path.join(a.output, "voiceover.wav"), params, mix)
    write_wav(os.path.join(a.output, "stems", "narration.wav"), params, tracks["narration"])
    write_wav(os.path.join(a.output, "stems", "dialogue.wav"), params, tracks["dialogue"])
    role_files = {}
    for k, r in enumerate(sp):
        fn = "stems/roles/%02d_%s.wav" % (k + 1, re.sub(r"[^\w\u4e00-\u9fff-]+", "_", r))
        write_wav(os.path.join(a.output, fn), params, roles[r])
        role_files[r] = fn

    cues = []
    for p in placed:
        chunks = split_caption(p["text"], a.max_chars)
        tot, s0 = sum(len(c) for c in chunks) or 1, p["start_at"]
        for c in chunks:
            d = p["dur"] * len(c) / tot
            cues.append((s0, s0 + d, p["speaker"], c))
            s0 += d
    for name, labelled in (("voiceover.srt", False), ("voiceover_roles.srt", True)):
        with open(os.path.join(a.output, name), "w", encoding="utf-8") as f:
            for k, (s, e, who, c) in enumerate(cues, 1):
                f.write("%d\n%s --> %s\n%s\n\n" % (k, ts(s), ts(e), ("%s：%s" % (who, c)) if labelled else c))
    rel = lambda f: f and os.path.relpath(f, a.output)
    over = [p for p in placed if p["avail"] is not None and p["dur"] > p["avail"] + 0.05]
    idle = [p for p in placed if p["avail"] is not None and p["avail"] - p["dur"] >= a.idle]
    with open(os.path.join(a.output, "cues.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["序号", "镜号", "画面", "说话人", "分轨", "语气", "文案", "开始", "结束", "时长", "画面可用", "超出秒数", "被顺延", "音频文件"])
        for p in placed:
            ov = round(p["dur"] - p["avail"], 2) if p["avail"] is not None else ""
            w.writerow([p["_n"], p.get("shot", ""), p.get("picture", ""), p["speaker"], "旁白" if p["track"] == "narration" else "台词",
                        p.get("emotion", ""), p["text"], ts(p["start_at"]), ts(p["end_at"]), p["dur"],
                        round(p["avail"], 2) if p["avail"] is not None else "", ov if (ov != "" and ov > 0.05) else "",
                        p["shift"] if p["shift"] > 0.001 else "", rel(p["file"]) or ""])
    manifest = {"version": VERSION, "input": os.path.basename(a.file), "input_kind": kind, "dry_run": a.dry_run,
                "mode": "locked" if locked else "sequential", "duration": round(total, 3),
                "tracks": {"mix": "voiceover.wav", "narration": "stems/narration.wav", "dialogue": "stems/dialogue.wav", "roles": role_files},
                "speakers": speakers(lines), "overruns": [p["_n"] for p in over], "fit_speed": a.fit_speed,
                "lines": [{"n": p["_n"], "shot": p.get("shot", ""), "picture": p.get("picture", ""), "speaker": p["speaker"],
                           "track": p["track"], "tone": p.get("emotion", ""), "text": p["text"], "start": p["start_at"],
                           "end": p["end_at"], "duration": p["dur"], "available": p["avail"], "shift": p["shift"],
                           "file": rel(p["file"])} for p in placed]}
    with open(os.path.join(a.output, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    nar = sum(p["dur"] for p in placed if p["track"] == "narration")
    rep = ["# 解说配音报告", "",
           "- 输入：%s（%s）；模式：%s%s" % (os.path.basename(a.file), {"script": "解说稿", "table": "分镜表", "srt": "SRT 字幕"}[kind],
                                       "对轨（按时间码落位）" if locked else "顺排（按句间停顿依次排列）",
                                       "；--dry-run 占位音，时长按每秒 %.1f 字估算" % CHARS_PER_SEC if a.dry_run else ""),
           "- 总时长 %.1f 秒，%d 句；解说旁白 %.1f 秒，角色台词 %.1f 秒" % (total, len(placed), nar, sum(p["dur"] for p in placed) - nar),
           ("- 本次新生成 %d 句，复用缓存 %d 句" % (a.generated, a.reused)) if not a.dry_run else "- 未调用接口",
           "", "| 说话人 | 分轨 | 句数 | 单独音轨 |", "|---|---|---|---|"]
    rep += ["| %s | %s | %d | `%s` |" % (r, "旁白" if speakers(lines)[r]["track"] == "narration" else "台词",
                                         sum(1 for p in placed if p["speaker"] == r), role_files[r]) for r in sp]
    if locked:
        rep += ["", "## 超出画面时长的句子", ""]
        if over:
            rep += ["| 序号 | 说话人 | 文案 | 实际 | 画面可用 | 建议语速 | 或删约几字 |", "|---|---|---|---|---|---|---|"]
            for p in over:
                sug = min(4.0, speed_of(p, voices, a.fit_speed) * p["dur"] / max(p["avail"] - 0.05, 0.1))
                cut = math.ceil(len(p["text"]) * (1 - max(p["avail"] - 0.05, 0.1) / p["dur"]))
                rep.append("| %d | %s | %s | %.2fs | %.2fs | %.2f | %d |" % (p["_n"], p["speaker"], p["text"][:20], p["dur"], p["avail"], sug, cut))
            rep += ["", "处理顺序：先删字（解说稿宁短勿赶），其次给这句加语速，或加 `--fit` 按建议语速自动重配（会产生新的生成任务）。建议语速高于 1.3 时听感偏赶。"]
        else:
            rep.append("无，所有句子都落在各自的画面时间内。")
        if idle:
            rep += ["", "## 画面空着较久的句子（可补一句或留给原声 / 音乐）", ""]
            rep += ["- 第 %d 句后空 %.1f 秒：%s" % (p["_n"], p["avail"] - p["dur"], p["text"][:20]) for p in idle]
        shifted = [p for p in placed if p["shift"] > 0.001]
        if shifted:
            rep += ["", "## 因上一句没说完被顺延的句子", ""] + ["- 第 %d 句顺延 %.2f 秒" % (p["_n"], p["shift"]) for p in shifted]
        if a.fit_speed:
            rep += ["", "已按 --fit 重配：" + "、".join("第%d句→语速%.2f" % kv for kv in sorted(a.fit_speed.items()))]
    with open(os.path.join(a.output, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep) + "\n")
    print("完成：%s/voiceover.wav（%.1f 秒，%d 句，%s）+ stems/narration.wav + stems/dialogue.wav + voiceover.srt + cues.csv + report.md%s%s"
          % (a.output, total, len(placed), "对轨" if locked else "顺排",
             ("  | %d 句超出画面时长，见 report.md" % len(over)) if over else "",
             "  [dry-run：占位音，未调用接口]" if a.dry_run else ""))
    return 0


# ------------------------------------------------------------------ selftest

SELF_SCRIPT = """---
旁白: actor_id=NARRATOR_VOICE_ID speed=1.0
阿岚: actor_id=ROLE_VOICE_ID
@tones: 低沉=TAG_LOW
---
=== 镜1 | 测试 ===
> 画面：空镜
00:00:00.0 这是一句解说旁白。
[00:00:03-00:00:04] 阿岚（低沉）：这一句台词明显超过了一秒钟的画面。
@6 最后一句解说。
"""
SELF_SRT = "1\n00:00:00,000 --> 00:00:02,500\n第一句字幕旁白。\n\n2\n00:00:03,000 --> 00:00:05,000\n阿岚：第二句是角色。\n"


def cmd_selftest(a):
    results, tmp = [], tempfile.mkdtemp(prefix="recap_selftest_")
    ex = os.path.join(os.path.dirname(HERE), "examples")

    def ok(name, cond, detail=""):
        results.append(bool(cond))
        print("%s  %s%s" % ("PASS" if cond else "FAIL", name, ("  " + detail) if detail and not cond else ""))

    def build(src, out, *extra):
        ns = build_parser().parse_args(["build", src, "-o", out, "--dry-run"] + list(extra))
        return ns.fn(ns)

    saved_key = os.environ.pop("MIRAGEA_API_KEY", None)
    try:
        p = os.path.join(tmp, "t.md")
        open(p, "w", encoding="utf-8").write(SELF_SCRIPT)
        v, tm, lines, kind = load(p)
        spoken = [l for l in lines if "text" in l]
        ok("解析解说稿：3 句、旁白/台词分轨、语气、时间码", len(spoken) == 3 and spoken[1]["speaker"] == "阿岚" and spoken[1]["track"] == "dialogue"
           and spoken[0]["track"] == "narration" and spoken[1]["emotion"] == "低沉" and spoken[1]["slot"] == 1.0 and spoken[2]["start"] == 6.0)
        ok("画面注释记入计划表", spoken[0]["picture"] == "画面：空镜")
        out = os.path.join(tmp, "o1")
        with open(os.devnull, "w") as dn:
            so, se, sys.stdout, sys.stderr = sys.stdout, sys.stderr, dn, dn
            try:
                rc = build(p, out)
            finally:
                sys.stdout, sys.stderr = so, se
        man = json.load(open(os.path.join(out, "manifest.json"), encoding="utf-8"))
        ok("dry-run 生成 voiceover.wav / 两条分轨 / SRT / cues.csv / report.md", rc == 0 and all(os.path.exists(os.path.join(out, f)) for f in
           ("voiceover.wav", "stems/narration.wav", "stems/dialogue.wav", "voiceover.srt", "voiceover_roles.srt", "cues.csv", "report.md")))
        with wave.open(os.path.join(out, "voiceover.wav")) as w1, wave.open(os.path.join(out, "stems/dialogue.wav")) as w2:
            ok("分轨与总轨等长", w1.getnframes() == w2.getnframes() and w1.getnframes() > 0)
        ok("超时报告抓到第 2 句", man["overruns"] == [2] and "超出画面时长" in open(os.path.join(out, "report.md"), encoding="utf-8").read())
        ok("顺延：第 3 句不早于第 2 句结束", man["lines"][2]["start"] >= man["lines"][1]["end"] - 1e-6)
        srt = open(os.path.join(out, "voiceover.srt"), encoding="utf-8").read()
        ok("SRT 时间码格式正确", len(SRT_TIME_RE.findall(srt)) >= 3)
        out2 = os.path.join(tmp, "o2")
        with open(os.devnull, "w") as dn:
            so, se, sys.stdout, sys.stderr = sys.stdout, sys.stderr, dn, dn
            try:
                build(p, out2, "--fit")
            finally:
                sys.stdout, sys.stderr = so, se
        man2 = json.load(open(os.path.join(out2, "manifest.json"), encoding="utf-8"))
        ok("--fit 后不再超时", man2["overruns"] == [] and man2["fit_speed"].get("2", man2["fit_speed"].get(2, 0)) > 1)
        s = os.path.join(tmp, "subs.txt")
        open(s, "w", encoding="utf-8").write(SELF_SRT)
        v, tm, lines, kind = load(s)
        ok("识别 .txt 里的 SRT 内容", kind == "srt" and len(lines) == 2 and lines[1]["speaker"] == "阿岚" and lines[0]["slot"] == 2.5)
        ok("音色写法 voice=角色名称", parse_voice("旁白", "voice=我的声音 speed=1.1") == {"actor_name": "我的声音", "speed": 1.1})
        try:
            parse_voice("旁白", "ref=https://example.com/a.wav")
            ok("旧的音频链接写法给出迁移提示", False, "没有报错")
        except Fail as e:
            ok("旧的音频链接写法给出迁移提示", "create-actor" in str(e))
        ns = build_parser().parse_args(["build", p, "-o", os.path.join(tmp, "o3")])
        called = []
        real = globals()["generate_line"]
        globals()["generate_line"] = lambda *x, **k: called.append(1)
        try:
            ns.fn(ns)
            ok("无 Key 正式生成被拒绝", False, "没有报错")
        except Fail as e:
            ok("无 Key 正式生成：中文提示、未调用接口", "MIRAGEA_API_KEY" in str(e) and not called)
        finally:
            globals()["generate_line"] = real
        if os.path.isdir(ex):
            for f in sorted(os.listdir(ex)):
                if f.startswith("cast"):
                    continue
                o = os.path.join(tmp, "ex_" + re.sub(r"\W", "_", f))
                with open(os.devnull, "w") as dn:
                    so, se, sys.stdout, sys.stderr = sys.stdout, sys.stderr, dn, dn
                    try:
                        rc = build(os.path.join(ex, f), o)
                    except Exception as e:  # noqa
                        rc = str(e)
                    finally:
                        sys.stdout, sys.stderr = so, se
                ok("示例 examples/%s 离线跑通" % f, rc == 0 and os.path.exists(os.path.join(o, "voiceover.wav")), str(rc))
        else:
            print("SKIP  examples/ 目录不在 %s" % ex)
    finally:
        if saved_key is not None:
            os.environ["MIRAGEA_API_KEY"] = saved_key
        shutil.rmtree(tmp, ignore_errors=True)
    passed = sum(results)
    print("selftest %s：%d/%d 通过（未使用 API Key，未联网）" % ("通过" if passed == len(results) else "失败", passed, len(results)))
    return 0 if passed == len(results) else 1


# ------------------------------------------------------------------ cli

def build_parser():
    p = argparse.ArgumentParser(prog="recap_dub.py", description="电影解说配音：解说稿 / 分镜表 / SRT → 旁白+台词分轨配音、SRT、对轨计划表")
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("selftest", help="离线自检：不需要 Key、不联网")
    s.set_defaults(fn=cmd_selftest)
    k = sub.add_parser("check", help="离线：逐句显示解析结果、预计时长和预计超时")
    k.add_argument("file")
    k.add_argument("--cast")
    k.set_defaults(fn=cmd_check)
    c = sub.add_parser("cast", help="列出说话人并生成音色表")
    c.add_argument("file")
    c.add_argument("--cast")
    c.add_argument("-o", "--output")
    c.add_argument("--force", action="store_true")
    c.set_defaults(fn=cmd_cast)
    b = sub.add_parser("build", help="生成配音")
    b.add_argument("file")
    b.add_argument("-o", "--output", default="recap_out")
    b.add_argument("--cast", help="音色表（front matter 格式）")
    b.add_argument("--gap", type=float, default=0.3, help="顺排模式句间停顿秒数（默认 0.3）")
    b.add_argument("--shot-gap", type=float, default=0.5, help="顺排模式换镜停顿秒数（默认 0.5）")
    b.add_argument("--sequential", action="store_true", help="忽略时间码，按句顺排")
    b.add_argument("--allow-overlap", action="store_true", help="对轨模式：严格按时间码，即使与上一句重叠")
    b.add_argument("--fit", action="store_true", help="对轨模式：超时句按建议语速自动重配一次")
    b.add_argument("--idle", type=float, default=2.0, help="报告画面空着超过多少秒的句子（默认 2）")
    b.add_argument("--max-chars", type=int, default=16, help="每条字幕最多字数（默认 16）")
    b.add_argument("--model", choices=("expressive", "standard"))
    b.add_argument("--no-tone", action="store_true", help="语气只从文本里去掉，不作为标签提交")
    b.add_argument("--retake", help="重新生成这些句子的新版本，例如 3,7")
    b.add_argument("--fresh", action="store_true", help="全部句子生成新版本")
    b.add_argument("--wait-timeout", type=float, default=600)
    b.add_argument("--dry-run", action="store_true", help="离线试跑：占位音、不需要 Key、不调用接口")
    b.set_defaults(fn=cmd_build)
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        return a.fn(a)
    except ScriptError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2
    except (OSError, ValueError, csv.Error) as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
