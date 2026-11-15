#!/usr/bin/env python3
"""Comic-drama / short-drama / animation dialogue dubbing on top of the official client.

  python3 scripts/drama_dub.py cast  SCRIPT [-o cast.md]        list roles, line counts, emotions; write a casting sheet
  python3 scripts/drama_dub.py check SCRIPT [--cast cast.md]    offline: parse, show every line, find missing voices
  python3 scripts/drama_dub.py build SCRIPT -o OUT [--cast cast.md] [--dry-run]

SCRIPT can be
  * a Markdown/text script:   角色（情绪）：台词   |  [角色|情绪] 台词  |  [角色] 台词  |  旁白：……
                              optional shot headers `=== 镜1 ===` / `## 第1场`, `[pause 0.5]`,
                              optional time anchors `@00:12.5 角色：台词` to lock a line to the picture
  * a storyboard table (.csv / .tsv) with columns such as 镜号 / 角色 / 台词 / 情绪 / 开始 / 时长 / 语速
  * subtitles (.srt) whose cue text is `角色：台词` — every line is placed at its cue start time

Voices: a front matter block (in SCRIPT or in a separate --cast file) gives every role one voice:
  角色: actor_id=ID [speed=1.0] [model=expressive|standard] [tags=a,b]
  角色: ref=https://.../sample.wav ref_text="原话"
  @emotions: 愤怒=TAG_LABEL, 低语=TAG_LABEL      (map script emotions to the account's tag labels)

Each line is rendered once with `miragea_audio.py generate --format wav --wait` (cached in OUT/lines/,
so editing one line only re-renders that line). Outputs in OUT/:
  dub.wav            full dialogue track          stems/<role>.wav   one track per role, same length
  dub.srt            subtitles without names      dub_roles.srt      subtitles with role names
  cues.csv           per-line timing sheet        manifest.json      everything above as data
  report.md          roles, duration, lines that overrun their slot with a suggested speed

--dry-run needs no key and makes no API call: each line becomes a soft placeholder tone
(a different pitch per role) with an estimated length, so the whole pipeline can be tested.
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
import sys
import uuid
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voiceover import ScriptError, generate_line, payload_for, read_wav, split_caption, ts  # noqa: E402

VERSION = "1.0.0"
DRY_RATE = 24000
NARRATOR_NAMES = ("旁白", "画外音", "OS", "narrator", "Narrator", "NARRATOR")
ALIASES = {"ref": "reference_audio_url", "ref_text": "reference_text", "actor": "actor_id"}
VOICE_KEYS = ("actor_id", "reference_audio_url", "reference_text", "model", "language", "speed", "tags")
SHOT_RE = re.compile(r"^\s*(?:={2,}\s*(?P<a>.+?)\s*={2,}|#{2,}\s*(?P<b>.+?))\s*$")
PAUSE_RE = re.compile(r"^\s*\[(?:pause|停顿)\s*(?P<s>[\d.]+)\s*s?\]\s*$", re.I)
ANCHOR_RE = re.compile(r"^\s*@(?P<t>\d{1,2}:\d{1,2}(?::\d{1,2})?(?:[.,]\d+)?|\d+(?:\.\d+)?)\s+(?P<rest>.*)$")
BRACKET_RE = re.compile(r"^\s*\[(?P<who>[^\]|｜]+)(?:[|｜](?P<emo>[^\]]+))?\]\s*[:：]?\s*(?P<text>.*)$")
COLON_RE = re.compile(r"^\s*(?P<who>[^\s:：，,。！？!?（(【\[]{1,12})\s*(?:[（(](?P<emo>[^）)]{1,12})[）)])?\s*[:：]\s*(?P<text>.+)$")
LEAD_EMO_RE = re.compile(r"^\s*[（(](?P<emo>[^）)]{1,12})[）)]\s*(?P<text>.*)$")
SRT_TIME_RE = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")
COLS = {
    "shot": ("镜号", "镜头", "shot", "scene", "场次", "分镜"),
    "speaker": ("角色", "说话人", "人物", "role", "speaker", "character"),
    "text": ("台词", "对白", "文本", "line", "text", "dialogue"),
    "emotion": ("情绪", "语气", "emotion", "tone"),
    "start": ("开始", "起始", "入点", "start", "in"),
    "duration": ("时长", "秒数", "duration", "len"),
    "speed": ("语速", "speed"),
}


# ---------------------------------------------------------------- parsing

def seconds(v):
    v = str(v).strip().replace(",", ".")
    if not v:
        return None
    if ":" in v:
        parts = [float(p) for p in v.split(":")]
        while len(parts) < 3:
            parts.insert(0, 0.0)
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return float(v.rstrip("sS秒"))


def parse_voice(name, rest):
    v = {}
    for k, val in re.findall(r'(\w+)=("[^"]*"|\S+)', rest):
        k, val = ALIASES.get(k, k), val.strip('"')
        if k == "speed":
            val = float(val)
            if not 0.25 <= val <= 4:
                raise ScriptError("speed must be 0.25-4 (role %s)" % name)
        elif k == "tags":
            val = [t for t in re.split(r"[,，]", val) if t]
        elif k not in VOICE_KEYS:
            raise ScriptError("unknown voice option %s= (role %s)" % (k, name))
        v[k] = val
    if v.get("actor_id") and v.get("reference_text"):
        raise ScriptError("ref_text only goes with ref= (role %s)" % name)
    return v


def split_front(text):
    """Return (voices, emotion_map, body)."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    voices, emap = {}, {}
    m = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return voices, emap, text
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.strip().startswith("#") or ":" not in raw:
            continue
        name, rest = [x.strip() for x in raw.split(":", 1)]
        if name in ("@emotions", "@情绪"):
            for pair in re.split(r"[,，;；]", rest):
                if "=" in pair:
                    a, b = [x.strip() for x in pair.split("=", 1)]
                    emap[a] = [t for t in re.split(r"[+＋]", b) if t]
            continue
        voices[name] = parse_voice(name, rest)
    return voices, emap, text[m.end():]


def split_line(s, known):
    """'角色（情绪）：台词' / '[角色|情绪] 台词' -> (who, emotion, text). who None = untagged."""
    m = BRACKET_RE.match(s)
    if m and not re.match(r"^(pause|停顿)\b", m.group("who"), re.I):
        who, emo, text = m.group("who").strip(), (m.group("emo") or "").strip(), m.group("text").strip()
    else:
        m = COLON_RE.match(s)
        if m and (m.group("who") in known or m.group("who") in NARRATOR_NAMES or len(m.group("who")) <= 8):
            who, emo, text = m.group("who").strip(), (m.group("emo") or "").strip(), m.group("text").strip()
        else:
            who, emo, text = None, "", s.strip()
    lm = LEAD_EMO_RE.match(text)
    if lm:
        emo, text = emo or lm.group("emo").strip(), lm.group("text").strip()
    return who, emo, text


def parse_text_script(body, known):
    lines, shot = [], ""
    for raw in body.splitlines():
        s = raw.strip()
        if not s or s.startswith("#") and not SHOT_RE.match(s):
            continue
        sm = SHOT_RE.match(s)
        if sm:
            shot = (sm.group("a") or sm.group("b")).strip()
            continue
        pm = PAUSE_RE.match(s)
        if pm:
            lines.append({"pause": float(pm.group("s"))})
            continue
        start = None
        am = ANCHOR_RE.match(s)
        if am:
            start, s = seconds(am.group("t")), am.group("rest")
        who, emo, text = split_line(s, known)
        if not text:
            continue
        lines.append({"speaker": who or "旁白", "emotion": emo, "text": text, "shot": shot, "start": start})
    return lines


def parse_table(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        sample = f.read()
    delim = "\t" if path.lower().endswith(".tsv") or sample.count("\t") > sample.count(",") else ","
    rows = list(csv.reader(io.StringIO(sample), delimiter=delim))
    if not rows:
        raise ScriptError("table is empty")
    head = [h.strip().lower() for h in rows[0]]
    idx = {}
    for key, names in COLS.items():
        for i, h in enumerate(head):
            if any(h == n.lower() or h.startswith(n.lower()) for n in names):
                idx.setdefault(key, i)
    if "text" not in idx:
        raise ScriptError("table needs a 台词/text column; found: %s" % ", ".join(rows[0]))
    get = lambda r, k: (r[idx[k]].strip() if k in idx and idx[k] < len(r) else "")
    lines, last_shot = [], ""
    for r in rows[1:]:
        text = get(r, "text")
        if not text:
            continue
        if get(r, "speaker"):
            lm = LEAD_EMO_RE.match(text)
            who, emo2, text2 = get(r, "speaker"), (lm.group("emo").strip() if lm else ""), (lm.group("text").strip() if lm else text)
        else:
            who, emo2, text2 = split_line(text, set())
        line = {"speaker": who or "旁白", "emotion": get(r, "emotion") or emo2, "text": text2,
                "shot": get(r, "shot") or last_shot, "start": seconds(get(r, "start")) if get(r, "start") else None}
        if get(r, "duration"):
            line["slot"] = seconds(get(r, "duration"))
        if get(r, "speed"):
            line["speed"] = float(get(r, "speed"))
        last_shot = line["shot"]
        lines.append(line)
    return lines


def parse_srt(text, known):
    lines = []
    for block in re.split(r"\n\s*\n", text.strip()):
        m = SRT_TIME_RE.search(block)
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0
        body = " ".join(l.strip() for l in block[m.end():].strip().splitlines() if l.strip())
        body = re.sub(r"<[^>]+>|\{[^}]+\}", "", body)
        if not body:
            continue
        who, emo, txt = split_line(body, known)
        lines.append({"speaker": who or "旁白", "emotion": emo, "text": txt, "shot": "", "start": start, "slot": end - start})
    return lines


def load(script, cast=None):
    with open(script, encoding="utf-8-sig") as f:
        raw = f.read()
    voices, emap, body = split_front(raw)
    if cast:
        with open(cast, encoding="utf-8-sig") as f:
            cv, ce, _ = split_front(f.read())
        voices.update(cv)
        emap.update(ce)
    low = script.lower()
    if low.endswith((".csv", ".tsv")):
        lines = parse_table(script)
    elif low.endswith(".srt"):
        lines = parse_srt(body, set(voices))
    else:
        lines = parse_text_script(body, set(voices))
    if not any("text" in l for l in lines):
        raise ScriptError("no spoken lines found in %s" % script)
    return voices, emap, lines


# ---------------------------------------------------------------- audio helpers

def tone(text, role_index, seconds_):
    """Dry-run placeholder: soft tone, a different pitch per role, faded in/out."""
    n = int(DRY_RATE * seconds_)
    freq = 220.0 * (2 ** (role_index % 7 / 7.0))
    buf = array.array("h")
    fade = int(DRY_RATE * 0.03)
    for i in range(n):
        env = min(1.0, i / fade, (n - i) / fade) if fade else 1.0
        buf.append(int(1800 * env * math.sin(2 * math.pi * freq * i / DRY_RATE)))
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(DRY_RATE)
        w.writeframes(buf.tobytes())
    return out.getvalue()


def estimate(text, speed):
    """Rough speaking length used only by --dry-run (about 4.5 Chinese characters per second)."""
    units = len(re.findall(r"[\u4e00-\u9fff]", text)) + len(re.findall(r"[A-Za-z0-9]+", text)) * 1.5
    return max(0.6, units / 4.5 / (speed or 1.0))


def write_wav(path, params, samples):
    with wave.open(path, "wb") as w:
        w.setnchannels(params[0])
        w.setsampwidth(2)
        w.setframerate(params[2])
        w.writeframes(samples.tobytes())


# ---------------------------------------------------------------- commands

def roles_of(lines):
    roles = {}
    for l in lines:
        if "text" in l:
            r = roles.setdefault(l["speaker"], {"lines": 0, "chars": 0, "emotions": {}})
            r["lines"] += 1
            r["chars"] += len(l["text"])
            if l.get("emotion"):
                r["emotions"][l["emotion"]] = r["emotions"].get(l["emotion"], 0) + 1
    return roles


def cmd_cast(a):
    voices, emap, lines = load(a.file, a.cast)
    roles = roles_of(lines)
    emotions = sorted({e for r in roles.values() for e in r["emotions"]})
    out = ["---", "# 每个角色一行：用你账号里已克隆 / 已保存的音色 actor_id（miragea_audio.py actors 查询），",
           "# 或本人授权的参考音频 ref=URL ref_text=\"音频里的原话\"。speed 0.25-4。"]
    for name, r in sorted(roles.items(), key=lambda x: -x[1]["lines"]):
        if name in voices:
            v = voices[name]
            opts = " ".join("%s=%s" % ({"reference_audio_url": "ref", "reference_text": "ref_text"}.get(k, k),
                                       ",".join(x) if isinstance(x, list) else (json.dumps(x, ensure_ascii=False) if k == "reference_text" else x))
                            for k, x in v.items())
        else:
            opts = "actor_id=YOUR_CLONED_VOICE_ID speed=1.0"
        out.append("%s: %s    # %d 句 / %d 字%s" % (name, opts, r["lines"], r["chars"],
                                                   ("，情绪：" + "、".join(r["emotions"])) if r["emotions"] else ""))
    if emotions:
        out.append("# 情绪 → 语气标签：右边填 capabilities 里所选模式 tags[].label 的原文；留空则只去掉括号不传标签")
        out.append("@emotions: " + ", ".join("%s=%s" % (e, "+".join(emap.get(e, [])) or e) for e in emotions))
    out.append("---")
    text = "\n".join(out) + "\n"
    if a.output:
        if os.path.exists(a.output) and not a.force:
            raise ScriptError("%s exists; add --force to overwrite" % a.output)
        with open(a.output, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote %s (%d roles, %d emotions)" % (a.output, len(roles), len(emotions)), file=sys.stderr)
    print(text, end="")
    return 0


def cmd_check(a):
    voices, emap, lines = load(a.file, a.cast)
    roles = roles_of(lines)
    timed = sum(1 for l in lines if l.get("start") is not None)
    print("lines %d  roles %d  timed %d  mode %s" % (sum(1 for l in lines if "text" in l), len(roles), timed,
                                                    "locked" if timed else "sequential"))
    for i, l in enumerate(lines, 1):
        if "pause" in l:
            print("%3d  [pause %.2fs]" % (i, l["pause"]))
            continue
        at = (" @%s" % ts(l["start"])[3:]) if l.get("start") is not None else ""
        print("%3d  %-8s %-6s%s  %s" % (i, l["speaker"], l.get("emotion") or "-", at, l["text"][:48]))
    missing = [r for r in roles if not (voices.get(r, {}).get("actor_id") or voices.get(r, {}).get("reference_audio_url"))]
    unmapped = sorted({l["emotion"] for l in lines if l.get("emotion") and l["emotion"] not in emap})
    if missing:
        print("roles without a voice: %s  ->  python3 scripts/drama_dub.py cast %s -o cast.md" % ("、".join(missing), a.file))
    if unmapped:
        print("emotions sent as-is (map them with @emotions if your tag labels differ): %s" % "、".join(unmapped))
    return 0


def line_payload(l, voice, emap, a):
    v = dict(voice)
    if l.get("speed"):
        v["speed"] = l["speed"]
    if a.fit_speed.get(l["_n"]):
        v["speed"] = a.fit_speed[l["_n"]]
    tags = list(v.get("tags") or [])
    if l.get("emotion") and not a.no_emotion:
        for t in emap.get(l["emotion"], [l["emotion"]]):
            if t and t not in tags:
                tags.append(t)
    v["tags"] = tags
    return payload_for(l["text"], v, a.model)


def render_line(l, voice, emap, a, role_index, cache, salt):
    if a.dry_run:
        sp = l.get("speed") or voice.get("speed") or 1.0
        return tone(l["text"], role_index, estimate(l["text"], a.fit_speed.get(l["_n"]) or sp)), None
    p = line_payload(l, voice, emap, a)
    extra = salt + (uuid.uuid4().hex if l["_n"] in a.retake else "")
    digest = hashlib.sha256((json.dumps(p, sort_keys=True, ensure_ascii=False) + extra).encode()).hexdigest()
    src = os.path.join(cache, digest[:24] + ".wav")
    if not os.path.exists(src):
        print("line %d  %s  %s" % (l["_n"], l["speaker"], l["text"][:36]), file=sys.stderr)
        generate_line(p, src, "dd-" + digest[:40], a.wait_timeout)
    with open(src, "rb") as f:
        return f.read(), src


def cmd_build(a):
    voices, emap, lines = load(a.file, a.cast)
    roles = list(roles_of(lines))
    a.retake = {int(x) for x in re.split(r"[,，\s]+", a.retake or "") if x.strip()}
    a.fit_speed = {}
    n = 0
    for l in lines:
        if "text" in l:
            n += 1
            l["_n"] = n
    if not a.dry_run:
        missing = [r for r in roles if not (voices.get(r, {}).get("actor_id") or voices.get(r, {}).get("reference_audio_url"))]
        if missing:
            raise ScriptError("roles without a voice: %s. Run `drama_dub.py cast %s -o cast.md`, fill in your cloned "
                              "voice actor_id (from `miragea_audio.py actors`) and pass --cast cast.md" % ("、".join(missing), a.file))
        if not os.environ.get("MIRAGEA_API_KEY"):
            raise ScriptError("MIRAGEA_API_KEY is not set (or add --dry-run to test offline)")
    locked = any(l.get("start") is not None for l in lines) and not a.sequential
    os.makedirs(os.path.join(a.output, "lines"), exist_ok=True)
    salt = uuid.uuid4().hex if a.fresh else ""

    passes = 2 if (a.fit and locked) else 1
    for attempt in range(passes):
        params, clips = None, []
        for l in lines:
            if "text" not in l:
                clips.append(None)
                continue
            data, src = render_line(l, voices.get(l["speaker"], {}), emap, a, roles.index(l["speaker"]),
                                    os.path.join(a.output, "lines"), salt)
            prm, frames = read_wav(data, src or "placeholder")
            if prm[1] != 2:
                raise ScriptError("only 16-bit PCM WAV can be mixed here (%s)" % (src or "placeholder"))
            if params and prm != params:
                raise ScriptError("line %d has a different WAV format %s vs %s" % (l["_n"], prm, params))
            params = params or prm
            clips.append((frames, src))
        ch, _, rate = params
        # timeline
        t, placed, prev_shot = 0.0, [], None
        for i, l in enumerate(lines):
            if "pause" in l:
                t += l["pause"]
                continue
            frames, src = clips[i]
            dur = len(frames) / float(ch * 2 * rate)
            if locked and l.get("start") is not None:
                start = max(l["start"], t if not a.allow_overlap else l["start"])
            else:
                if placed:
                    t += a.shot_gap if (l.get("shot") and l["shot"] != prev_shot) else a.gap
                start = t
            nxt = next((x.get("start") for x in lines[i + 1:] if "text" in x and x.get("start") is not None), None) if locked else None
            slot = l.get("slot") if l.get("slot") else ((nxt - l["start"]) if (nxt is not None and l.get("start") is not None) else None)
            placed.append(dict(l, start_at=round(start, 3), end_at=round(start + dur, 3), dur=round(dur, 3), slot=slot,
                               shift=round(start - l["start"], 3) if l.get("start") is not None else 0.0, file=src, frames=frames))
            t, prev_shot = start + dur, l.get("shot")
        over = [p for p in placed if p["slot"] and p["dur"] > p["slot"] + 0.05]
        if attempt == 0 and passes == 2 and over:
            for p in over:
                base = p.get("speed") or voices.get(p["speaker"], {}).get("speed") or 1.0
                a.fit_speed[p["_n"]] = round(min(4.0, max(0.25, base * p["dur"] / max(p["slot"] - 0.05, 0.1))), 2)
            print("fit: re-rendering %d overrunning line(s) with a faster speed" % len(over), file=sys.stderr)
            continue
        break

    total = max(p["end_at"] for p in placed)
    nframes = int(math.ceil(total * rate)) + 1
    stems = {r: array.array("h", bytes(nframes * ch * 2)) for r in roles}
    mix = array.array("h", bytes(nframes * ch * 2))
    for p in placed:
        buf = array.array("h")
        buf.frombytes(p["frames"])
        off = int(round(p["start_at"] * rate)) * ch
        st = stems[p["speaker"]]
        for k, s in enumerate(buf):
            j = off + k
            if j >= nframes * ch:
                break
            v = st[j] + s
            st[j] = 32767 if v > 32767 else (-32768 if v < -32768 else v)
            v = mix[j] + s
            mix[j] = 32767 if v > 32767 else (-32768 if v < -32768 else v)
    os.makedirs(os.path.join(a.output, "stems"), exist_ok=True)
    write_wav(os.path.join(a.output, "dub.wav"), params, mix)
    stem_files = {}
    for k, r in enumerate(roles):
        fn = "stems/%02d_%s.wav" % (k + 1, re.sub(r"[^\w\u4e00-\u9fff-]+", "_", r))
        write_wav(os.path.join(a.output, fn), params, stems[r])
        stem_files[r] = fn

    cues = []
    for p in placed:
        chunks = split_caption(p["text"], a.max_chars)
        tot, s0 = sum(len(c) for c in chunks) or 1, p["start_at"]
        for c in chunks:
            d = p["dur"] * len(c) / tot
            cues.append((s0, s0 + d, p["speaker"], c))
            s0 += d
    for name, labelled in (("dub.srt", False), ("dub_roles.srt", True)):
        with open(os.path.join(a.output, name), "w", encoding="utf-8") as f:
            for k, (s, e, who, c) in enumerate(cues, 1):
                f.write("%d\n%s --> %s\n%s\n\n" % (k, ts(s), ts(e), ("%s：%s" % (who, c)) if labelled else c))
    with open(os.path.join(a.output, "cues.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["序号", "镜号", "角色", "情绪", "台词", "开始", "结束", "时长", "可用时长", "超出", "推后", "音频文件"])
        for p in placed:
            ov = round(p["dur"] - p["slot"], 2) if p["slot"] else ""
            w.writerow([p["_n"], p.get("shot", ""), p["speaker"], p.get("emotion", ""), p["text"], ts(p["start_at"]), ts(p["end_at"]),
                        p["dur"], round(p["slot"], 2) if p["slot"] else "", ov if (ov != "" and ov > 0.05) else "",
                        p["shift"] if p["shift"] > 0.001 else "", p["file"] and os.path.relpath(p["file"], a.output)])
    over = [p for p in placed if p["slot"] and p["dur"] > p["slot"] + 0.05]
    manifest = {"version": VERSION, "dry_run": a.dry_run, "mode": "locked" if locked else "sequential", "duration": round(total, 3),
                "stems": stem_files, "roles": roles_of(lines),
                "lines": [{k: p.get(k) for k in ("_n", "shot", "speaker", "emotion", "text", "start_at", "end_at", "dur", "slot", "shift")}
                          | {"file": p["file"] and os.path.relpath(p["file"], a.output)} for p in placed]}
    with open(os.path.join(a.output, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    rep = ["# 配音报告", "", "- 模式：%s%s" % ("对轨（按时间码落位）" if locked else "顺排（按句间停顿依次排列）",
                                            "，--dry-run 占位音，时长为估算" if a.dry_run else ""),
           "- 总时长：%.1f 秒，台词 %d 句，角色 %d 个" % (total, len(placed), len(roles)), "", "| 角色 | 句数 | 分轨 |", "|---|---|---|"]
    rep += ["| %s | %d | `%s` |" % (r, sum(1 for p in placed if p["speaker"] == r), stem_files[r]) for r in roles]
    if locked:
        rep += ["", "## 超出可用时长的句子", ""]
        if over:
            rep += ["| 序号 | 角色 | 台词 | 实际 | 可用 | 建议语速 |", "|---|---|---|---|---|---|"]
            for p in over:
                base = p.get("speed") or voices.get(p["speaker"], {}).get("speed") or 1.0
                rep.append("| %d | %s | %s | %.2fs | %.2fs | %.2f |" % (p["_n"], p["speaker"], p["text"][:24], p["dur"], p["slot"],
                                                                         min(4.0, base * p["dur"] / max(p["slot"] - 0.05, 0.1))))
            rep += ["", "处理：删减台词、在稿件里给这句加 `语速`/角色 `speed=`，或加 `--fit` 自动按建议语速重配这些句子（会产生新的生成任务）。"]
        else:
            rep.append("无，所有台词都落在各自的时间段内。")
        if a.fit_speed:
            rep += ["", "已按 --fit 改用新语速重配：" + "、".join("第%d句→%.2f" % kv for kv in sorted(a.fit_speed.items())),
                    "建议语速明显高于 1.3 时，听感会偏赶，优先删减台词。"]
    with open(os.path.join(a.output, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep) + "\n")
    print("wrote %s/dub.wav (%.1fs, %d lines, %d roles, %s) + stems/ + dub.srt + dub_roles.srt + cues.csv + report.md%s%s"
          % (a.output, total, len(placed), len(roles), "locked" if locked else "sequential",
             ("  | %d line(s) overrun their slot, see report.md" % len(over)) if over else "",
             "  [dry-run: placeholder tones, no API call]" if a.dry_run else ""))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="drama_dub.py", description="Multi-role dialogue dubbing: script/storyboard/SRT -> dub.wav + per-role stems + SRT")
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cast", help="list roles and write a casting sheet")
    c.add_argument("file")
    c.add_argument("--cast")
    c.add_argument("-o", "--output")
    c.add_argument("--force", action="store_true")
    c.set_defaults(fn=cmd_cast)
    k = sub.add_parser("check", help="offline: show how every line is parsed")
    k.add_argument("file")
    k.add_argument("--cast")
    k.set_defaults(fn=cmd_check)
    b = sub.add_parser("build", help="render the dialogue")
    b.add_argument("file")
    b.add_argument("-o", "--output", default="dub_out")
    b.add_argument("--cast", help="casting sheet with the voices (front matter format)")
    b.add_argument("--gap", type=float, default=0.25, help="silence between lines in sequential mode")
    b.add_argument("--shot-gap", type=float, default=0.6, help="silence when the shot changes in sequential mode")
    b.add_argument("--sequential", action="store_true", help="ignore time codes and lay lines end to end")
    b.add_argument("--allow-overlap", action="store_true", help="locked mode: keep time codes even if voices overlap")
    b.add_argument("--fit", action="store_true", help="locked mode: re-render overrunning lines once at a faster speed")
    b.add_argument("--max-chars", type=int, default=16, help="max characters per subtitle cue")
    b.add_argument("--model", choices=("expressive", "standard"))
    b.add_argument("--no-emotion", action="store_true", help="do not send emotions as tags")
    b.add_argument("--retake", help="line numbers to render again as a new take, e.g. 3,7")
    b.add_argument("--fresh", action="store_true", help="new takes for every line")
    b.add_argument("--wait-timeout", type=float, default=600)
    b.add_argument("--dry-run", action="store_true", help="offline: placeholder tones, no key, no API call")
    b.set_defaults(fn=cmd_build)
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        return a.fn(a)
    except ScriptError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    except (OSError, ValueError) as e:
        print("error: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
