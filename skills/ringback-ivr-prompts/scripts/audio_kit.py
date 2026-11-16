#!/usr/bin/env python3
"""Small shared audio toolkit for the skill scripts in this folder.

* voices: an existing role in your account, by exact name (`--voice 名称`, resolved by the official
  client with --actor-name) or by ID (`--actor-id ID`). The open API only accepts role IDs; it no longer
  takes a reference-audio URL, so create a private role from your own recording first
  (`miragea_audio.py create-actor`).
* generate(): one official-client `generate` call per sentence, WAV output, cached by content hash, the
  same idempotency key for the same input (re-running resumes instead of creating duplicate tasks).
* WAV helpers: read any PCM WAV, convert to mono 16-bit at one sample rate, silence, tones, peak
  normalise, mix, write; SRT / LRC writers. --dry-run uses quiet placeholder tones of estimated length
  and never needs a key or the network.

Python 3.9+ standard library only. MIT licence (see LICENSE.txt).
"""
import array
import hashlib
import io
import json
import math
import os
import re
import subprocess
import sys
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.join(HERE, "miragea_audio.py")
RATE = 24000                 # working sample rate for everything we join
CHARS_PER_SEC = 4.2          # rough Chinese reading speed, only for estimates and --dry-run
WORDS_PER_SEC = 2.4          # rough English reading speed, same use
PLACEHOLDER_RE = re.compile(r"^(YOUR_|你的|ACTOR_ID$|.*_ID$)")


class KitError(Exception):
    """Expected, user-facing problem: printed in Chinese, exit code 2."""


# ------------------------------------------------------------------ environment

def require_key(dry_run):
    if dry_run:
        return
    if not os.environ.get("MIRAGEA_API_KEY"):
        raise KitError("未设置环境变量 MIRAGEA_API_KEY，没有调用任何接口。请先在服务网站的「工作台 → 开放 API」生成 Key，"
                       "执行 export MIRAGEA_API_KEY=你的key；或者加 --dry-run 离线试跑（不需要 Key，不联网）。")


def voice_args(voice, actor_id):
    """-> client arguments for the voice; raises when nothing usable was given."""
    if actor_id and not PLACEHOLDER_RE.match(actor_id):
        return ["--actor-id", actor_id]
    if voice and not PLACEHOLDER_RE.match(voice):
        return ["--actor-name", voice]
    raise KitError("还没有指定音色：用 --voice 账号里的角色名称，或 --actor-id 角色ID（python3 scripts/miragea_audio.py actors 查看）。"
                   "还没有自己的角色时，先用本人或已获授权的 3–60 秒录音创建：python3 scripts/miragea_audio.py create-actor "
                   "--file 我的录音.wav --name 我的声音 --language zh")


def estimate_seconds(text):
    latin = len(re.findall(r"[A-Za-z]+", text))
    han = len(re.findall(r"[\u4e00-\u9fff0-9]", text))
    return max(0.6, han / CHARS_PER_SEC + latin / WORDS_PER_SEC)


# ------------------------------------------------------------------ PCM helpers (mono, 16-bit, RATE)

def silence(seconds, rate=RATE):
    return array.array("h", bytes(2 * max(0, int(round(seconds * rate)))))


def tone(freq, seconds, level=0.25, rate=RATE, fade=0.02):
    n = int(seconds * rate)
    f = max(1, int(fade * rate))
    out = array.array("h", bytes(2 * n))
    for i in range(n):
        env = min(1.0, i / f, (n - 1 - i) / f) if n > 2 * f else 1.0
        out[i] = int(32767 * level * env * math.sin(2 * math.pi * freq * i / rate))
    return out


def placeholder(text, rate=RATE):
    """Quiet low tone as long as the estimated speech: audible in a player, obviously not speech."""
    return tone(180, estimate_seconds(text), level=0.05, rate=rate)


def chime(rate=RATE):
    """Two-note 'ding-dong' (synthesised here, no sample file) used before shop announcements."""
    a = tone(784, 0.45, level=0.35, rate=rate, fade=0.08)
    b = tone(523, 0.65, level=0.35, rate=rate, fade=0.12)
    return a + silence(0.05, rate) + b


def to_mono16(data, rate=RATE):
    """bytes of any PCM WAV -> array('h') mono 16-bit at `rate` (linear interpolation)."""
    try:
        with wave.open(io.BytesIO(data)) as w:
            ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
            raw = w.readframes(n)
    except (wave.Error, EOFError) as e:
        raise KitError("返回的音频不是标准库能读取的 PCM WAV（%s）。单句文件保留在缓存目录，可用剪辑软件或 ffmpeg 手动拼接。" % e)
    if sw == 2:
        s = array.array("h", raw)
    elif sw == 1:
        s = array.array("h", ((b - 128) << 8 for b in raw))
    elif sw == 3:
        s = array.array("h", (int.from_bytes(raw[i + 1:i + 3], "little", signed=True) for i in range(0, len(raw), 3)))
    elif sw == 4:
        s = array.array("h", (v >> 16 for v in array.array("i", raw)))
    else:
        raise KitError("不支持的 WAV 位深：%d 字节" % sw)
    if sys.byteorder == "big":
        s.byteswap()
    if ch > 1:
        s = array.array("h", (int(sum(s[i:i + ch]) / ch) for i in range(0, len(s), ch)))
    if sr != rate and len(s) > 1:
        ratio = sr / float(rate)
        m = int(len(s) / ratio)
        out = array.array("h", bytes(2 * m))
        last = len(s) - 1
        for i in range(m):
            x = i * ratio
            j = int(x)
            k = j + 1 if j < last else last
            out[i] = int(s[j] + (s[k] - s[j]) * (x - j))
        s = out
    return s


def peak(s):
    return max((abs(v) for v in s), default=0)


def normalize(s, target_dbfs=-1.0):
    p = peak(s)
    if not p:
        return s
    g = (32767 * 10 ** (target_dbfs / 20.0)) / p
    return array.array("h", (max(-32768, min(32767, int(v * g))) for v in s))


def gain(s, db):
    g = 10 ** (db / 20.0)
    return array.array("h", (max(-32768, min(32767, int(v * g))) for v in s))


def duration(s, rate=RATE):
    return len(s) / float(rate)


def write_wav(path, s, rate=RATE):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    data = array.array("h", s)
    if sys.byteorder == "big":
        data.byteswap()
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())


def read_wav_file(path, rate=RATE):
    with open(path, "rb") as f:
        return to_mono16(f.read(), rate)


# ------------------------------------------------------------------ text helpers

def ts(sec, sep=","):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d%s%03d" % (h, m, s, sep, ms)


def write_srt(path, cues):
    with open(path, "w", encoding="utf-8") as f:
        for n, (a, b, text) in enumerate(cues, 1):
            f.write("%d\n%s --> %s\n%s\n\n" % (n, ts(a), ts(b), text))


def write_lrc(path, cues, title=""):
    with open(path, "w", encoding="utf-8") as f:
        if title:
            f.write("[ti:%s]\n" % title)
        for a, _, text in cues:
            m, s = divmod(a, 60)
            f.write("[%02d:%05.2f]%s\n" % (int(m), s, text.replace("\n", " ")))


SENT_RE = re.compile(r"(?<=[。！？!?；;…])(?![”’」』\"'）)])|(?<=[。！？!?；;…][”’」』\"'）)])")


def sentences(text, limit=120):
    """Split into sentences; very long ones are cut again at commas so every request stays short."""
    out = []
    for para in re.split(r"\n+", text.replace("\r", "")):
        para = para.strip()
        if not para:
            continue
        for s in SENT_RE.split(para):
            s = s.strip()
            while len(s) > limit:
                cut = max(s.rfind(c, 0, limit) for c in "，,、：: ")
                cut = cut + 1 if cut > limit // 3 else limit
                out.append(s[:cut].strip())
                s = s[cut:].strip()
            if s:
                out.append(s)
    return out


# ------------------------------------------------------------------ generation

def line_key(text, vargs, opts):
    blob = json.dumps({"t": text, "v": vargs, "o": opts}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def generate(text, vargs, cache_dir, dry_run, model=None, speed=None, tags=None, language=None,
             wait_timeout=600, label=""):
    """-> array('h') at RATE. Cached in cache_dir/<hash>.wav; the hash is also the idempotency key."""
    opts = {"model": model, "speed": speed, "tags": tags or [], "language": language}
    if dry_run:
        return placeholder(text)
    os.makedirs(cache_dir, exist_ok=True)
    key = line_key(text, vargs, opts)
    path = os.path.join(cache_dir, key[:24] + ".wav")
    if not os.path.exists(path):
        if label:
            print(label, file=sys.stderr)
        cmd = [sys.executable, CLIENT, "generate", "--text=" + text, "--format", "wav", "--wait",
               "--wait-timeout", str(wait_timeout), "--output", path, "--idempotency-key", "kit-" + key[:40]] + vargs
        if model:
            cmd += ["--model", model]
        if speed is not None:
            cmd += ["--speed", str(speed)]
        if language:
            cmd += ["--language", language]
        for t in tags or []:
            cmd += ["--tag=" + t]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            sys.stderr.write((r.stdout + r.stderr)[-1500:] + "\n")
            raise KitError("这一句生成失败：%s……  直接重跑同一条命令即可续跑：已完成的句子会复用，同一句使用同一个幂等键，"
                           "服务端返回原任务，不会重复创建。" % text[:24])
    return read_wav_file(path)


def check_speed(v):
    if v is not None and not 0.25 <= v <= 4:
        raise KitError("--speed 必须在 0.25–4 之间")
    return v


def run(main):
    """Wrap a main() so expected problems print a Chinese message and exit 2."""
    try:
        sys.exit(main() or 0)
    except KitError as e:
        print("错误：%s" % e, file=sys.stderr)
        sys.exit(2)
    except (FileNotFoundError, IsADirectoryError) as e:
        print("错误：找不到文件 %s，请检查路径（示例文件在 examples/ 目录）。" % (e.filename or e), file=sys.stderr)
        sys.exit(2)
    except UnicodeDecodeError:
        print("错误：文本文件不是 UTF-8 编码，请另存为 UTF-8 后重试。", file=sys.stderr)
        sys.exit(2)
