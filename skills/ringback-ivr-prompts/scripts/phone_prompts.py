#!/usr/bin/env python3
"""Company ringback tones and phone-menu (IVR) prompts (彩铃制作 / IVR语音导航 / 电话提示音).

  python3 scripts/phone_prompts.py selftest                        offline self test (no key, no network)
  python3 scripts/phone_prompts.py check PROMPTS.txt               offline: ids, text, estimated seconds
  python3 scripts/phone_prompts.py build PROMPTS.txt -o OUT --voice 角色名 [--rate 8000] [--codec pcm|alaw|ulaw]
                                     [--ringback welcome,slogan --ringback-seconds 30] [--dry-run]
  python3 scripts/phone_prompts.py inspect FILE.wav                show sample rate / codec / length of a WAV

PROMPTS.txt: one prompt per line as `id: 文本` (id = letters, digits, _ or -, used as the file name), e.g.
    welcome: 您好，欢迎致电某某公司。
    menu: 业务咨询请按1，售后服务请按2，人工服务请按0。
CSV with columns id,text also works. `#` lines are comments.

Outputs in OUT/: phone/<id>.wav in the telephone format you choose (8000 or 16000 Hz, mono, 16-bit PCM or
8-bit G.711 A-law / mu-law), hq/<id>.wav (24 kHz master), prompts.csv (id, text, seconds, file),
ringback.wav (selected prompts joined, repeated to --ringback-seconds), cache/.
Check the exact format your phone system or carrier asks for before uploading; this tool only makes files.
Python 3.9+ standard library only. MIT licence (see LICENSE.txt).
"""
import argparse
import array
import csv
import io
import math
import os
import re
import struct
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_kit as K  # noqa: E402

VERSION = "1.0.0"
ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
LINE_RE = re.compile(r"^\s*([A-Za-z0-9_-]{1,40})\s*[:：]\s*(.+)$")


# ------------------------------------------------------------------ input

def parse(path):
    text = open(path, encoding="utf-8-sig").read()
    items = []
    if path.lower().endswith(".csv"):
        for row in csv.DictReader(io.StringIO(text)):
            pid, body = (row.get("id") or "").strip(), (row.get("text") or row.get("文本") or "").strip()
            if pid and body:
                items.append((pid, body))
    else:
        for n, raw in enumerate(text.splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m = LINE_RE.match(line)
            if not m:
                raise K.KitError("第 %d 行格式应为 `id: 文本`（id 只用字母、数字、_、-）：%s" % (n, line[:40]))
            items.append((m.group(1), m.group(2).strip()))
    if not items:
        raise K.KitError("没有读到任何提示音：每行写 `id: 文本`")
    seen = set()
    for pid, _ in items:
        if pid in seen:
            raise K.KitError("id 重复：%s（每个 id 对应一个文件名，必须唯一）" % pid)
        seen.add(pid)
    return items


# ------------------------------------------------------------------ telephone formats

def lowpass_resample(s, src, dst):
    """Windowed-sinc low-pass then resample (keeps 8 kHz phone audio free of aliasing)."""
    if src == dst:
        return array.array("h", s)
    cutoff = 0.45 * min(src, dst) / src
    taps = 31
    mid = taps // 2
    h = []
    for i in range(taps):
        x = i - mid
        sinc = 2 * cutoff if x == 0 else math.sin(2 * math.pi * cutoff * x) / (math.pi * x)
        h.append(sinc * (0.54 - 0.46 * math.cos(2 * math.pi * i / (taps - 1))))
    norm = sum(h)
    h = [v / norm for v in h]
    n = len(s)
    ratio = src / float(dst)
    m = int(n / ratio)
    out = array.array("h", bytes(2 * m))
    for i in range(m):
        c = int(i * ratio)
        acc = 0.0
        for k in range(taps):
            j = c + k - mid
            if 0 <= j < n:
                acc += s[j] * h[k]
        out[i] = max(-32768, min(32767, int(acc)))
    return out


def ulaw(v):
    BIAS, CLIP = 0x84, 32635
    sign = 0x80 if v < 0 else 0
    v = min(abs(v), CLIP) + BIAS
    exp, mask = 7, 0x4000
    while exp > 0 and not v & mask:
        exp -= 1
        mask >>= 1
    mant = (v >> (exp + 3)) & 0x0F
    return ~(sign | (exp << 4) | mant) & 0xFF


def alaw(v):
    sign = 0x00 if v < 0 else 0x80
    v = min(abs(v), 32767) >> 3
    if v < 32:
        enc = v >> 1
    else:
        exp = 1
        while v >= 64 and exp < 7:
            v >>= 1
            exp += 1
        enc = (exp << 4) | ((v >> 1) & 0x0F)
    return (enc | sign) ^ 0x55


def write_phone_wav(path, s, rate, codec):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if codec == "pcm":
        K.write_wav(path, s, rate)
        return
    fn = alaw if codec == "alaw" else ulaw
    data = bytes(fn(v) for v in s)
    fmt_tag = 6 if codec == "alaw" else 7
    fmt = struct.pack("<HHIIHHH", fmt_tag, 1, rate, rate, 1, 8, 0)
    body = b"WAVE" + b"fmt " + struct.pack("<I", len(fmt)) + fmt + b"fact" + struct.pack("<II", 4, len(data)) + \
        b"data" + struct.pack("<I", len(data)) + data + (b"\x00" if len(data) % 2 else b"")
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", len(body)) + body)


def inspect(path):
    with open(path, "rb") as f:
        head = f.read(12)
        if head[:4] != b"RIFF" or head[8:12] != b"WAVE":
            raise K.KitError("不是 WAV 文件：%s" % path)
        info, size = {}, None
        while True:
            ch = f.read(8)
            if len(ch) < 8:
                break
            cid, ln = ch[:4], struct.unpack("<I", ch[4:])[0]
            if cid == b"fmt ":
                tag, chans, rate, _, _, bits = struct.unpack("<HHIIHH", f.read(16))
                f.seek(ln - 16 + (ln % 2), 1)
                info = {"codec": {1: "pcm", 6: "alaw", 7: "ulaw"}.get(tag, "tag%d" % tag), "channels": chans, "rate": rate, "bits": bits}
            elif cid == b"data":
                size = ln
                break
            else:
                f.seek(ln + (ln % 2), 1)
    if not info or size is None:
        raise K.KitError("WAV 结构不完整：%s" % path)
    info["seconds"] = round(size / float(info["rate"] * info["channels"] * info["bits"] // 8), 2)
    return info


# ------------------------------------------------------------------ commands

def cmd_check(a):
    items = parse(a.prompts)
    total = 0.0
    for pid, text in items:
        est = K.estimate_seconds(text)
        total += est
        print("  %-14s 约 %4.1f 秒  %s" % (pid, est, text))
    print("%d 条提示音，合计约 %.1f 秒（粗估，实际以生成为准）" % (len(items), total))
    return 0


def cmd_build(a):
    K.check_speed(a.speed)
    items = parse(a.prompts)
    ids = [x for x in (a.ringback or "").split(",") if x]
    missing = [x for x in ids if x not in dict(items)]
    if missing:
        raise K.KitError("--ringback 里的 id 不存在：%s" % ", ".join(missing))
    K.require_key(a.dry_run)
    v = ["--dry-run"] if a.dry_run else K.voice_args(a.voice, a.actor_id)
    out = a.output
    masters, rows = {}, []
    for n, (pid, text) in enumerate(items, 1):
        audio = K.generate(text, v, os.path.join(out, "cache"), a.dry_run, model=a.model, speed=a.speed, tags=a.tag,
                           label="%d/%d  %s" % (n, len(items), pid))
        audio = K.normalize(K.silence(a.lead) + audio + K.silence(a.tail), a.peak)
        masters[pid] = audio
        K.write_wav(os.path.join(out, "hq", pid + ".wav"), audio)
        phone = lowpass_resample(audio, K.RATE, a.rate)
        write_phone_wav(os.path.join(out, "phone", pid + ".wav"), phone, a.rate, a.codec)
        rows.append({"id": pid, "text": text, "seconds": round(K.duration(audio), 2), "file": "phone/%s.wav" % pid})
    with open(os.path.join(out, "prompts.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "text", "seconds", "file"])
        w.writeheader()
        w.writerows(rows)
    msg = "%d 条提示音 → %s/phone/（%d Hz，%s）+ hq/ + prompts.csv" % (len(rows), out, a.rate, a.codec)
    if ids:
        one = K.silence(0)
        for pid in ids:
            one += masters[pid] + K.silence(a.ringback_gap)
        rb = K.silence(0)
        while K.duration(rb) + K.duration(one) <= a.ringback_seconds + 0.01 or not len(rb):
            rb += one
        rb = lowpass_resample(rb, K.RATE, a.rate)
        write_phone_wav(os.path.join(out, "ringback.wav"), rb, a.rate, a.codec)
        msg += "；彩铃 ringback.wav %.1f 秒" % (len(rb) / float(a.rate))
    print(msg + ("  [dry-run：占位提示音，未调用接口]" if a.dry_run else ""))
    return 0


def cmd_inspect(a):
    i = inspect(a.file)
    print("%s  %s  %d Hz  %d 声道  %d bit  %.2f 秒" % (a.file, i["codec"], i["rate"], i["channels"], i["bits"], i["seconds"]))
    return 0


def cmd_selftest(a):
    assert ulaw(0) == 0xFF and alaw(0) == 0xD5
    assert ulaw(-32768) == 0x00 or ulaw(-32768) == 0x01 or ulaw(-32768) < 0x10
    d = tempfile.mkdtemp()
    p = os.path.join(d, "p.txt")
    open(p, "w", encoding="utf-8").write("# demo\nwelcome: 您好，欢迎致电。\nmenu: 咨询请按1，人工服务请按0。\n")
    assert parse(p) == [("welcome", "您好，欢迎致电。"), ("menu", "咨询请按1，人工服务请按0。")]
    class A: pass
    x = A(); x.prompts = p; x.output = d + "/o"; x.voice = x.actor_id = x.model = x.speed = None; x.tag = []
    x.dry_run, x.rate, x.codec, x.lead, x.tail, x.peak = True, 8000, "alaw", 0.2, 0.3, -3.0
    x.ringback, x.ringback_seconds, x.ringback_gap = "welcome,menu", 12, 1.0
    cmd_build(x)
    i = inspect(d + "/o/phone/menu.wav")
    assert i["codec"] == "alaw" and i["rate"] == 8000 and i["bits"] == 8 and i["seconds"] > 1, i
    assert inspect(d + "/o/ringback.wav")["seconds"] >= 6
    print("selftest ok")
    return 0


def main():
    p = argparse.ArgumentParser(prog="phone_prompts.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("selftest").set_defaults(fn=cmd_selftest)
    c = s.add_parser("check"); c.add_argument("prompts"); c.set_defaults(fn=cmd_check)
    i = s.add_parser("inspect"); i.add_argument("file"); i.set_defaults(fn=cmd_inspect)
    b = s.add_parser("build")
    b.add_argument("prompts")
    b.add_argument("-o", "--output", default="phone_out")
    b.add_argument("--voice", help="exact role name in your account")
    b.add_argument("--actor-id")
    b.add_argument("--rate", type=int, choices=(8000, 16000), default=8000)
    b.add_argument("--codec", choices=("pcm", "alaw", "ulaw"), default="pcm", help="pcm = 16-bit; alaw/ulaw = 8-bit G.711")
    b.add_argument("--speed", type=float)
    b.add_argument("--model", choices=("expressive", "standard"))
    b.add_argument("--tag", action="append", default=[])
    b.add_argument("--lead", type=float, default=0.2, help="silence before each prompt (s)")
    b.add_argument("--tail", type=float, default=0.3, help="silence after each prompt (s)")
    b.add_argument("--peak", type=float, default=-3.0, help="peak level dBFS")
    b.add_argument("--ringback", help="ids joined into ringback.wav, e.g. welcome,slogan")
    b.add_argument("--ringback-seconds", type=float, default=30)
    b.add_argument("--ringback-gap", type=float, default=1.0)
    b.add_argument("--dry-run", action="store_true", help="offline: placeholder tones, no key, no API call")
    b.set_defaults(fn=cmd_build)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    K.run(main)
