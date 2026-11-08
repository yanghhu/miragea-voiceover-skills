#!/usr/bin/env python3
"""Video voiceover helper for AI agents (Codex / Claude Code / WorkBuddy / Cursor).

Turns a script into a finished voiceover track (WAV) plus SRT subtitles, with
multi-speaker lines, pauses and per-line speed, using the Miragea Agent API
(voice cloning + TTS in 10 languages). Python 3.9+ standard library only.

Commands
  doctor                      check Python, API key presence, API reachability
  voices                      list voices (actors) saved in your Miragea account
  say    TEXT  -o out.wav     one line of speech
  script FILE  -o out_dir     multi-speaker script -> voiceover.wav + voiceover.srt + manifest.json
  subtitles MEDIA -o out.srt  speech-to-text subtitles with timestamps

Add --dry-run to any generating command to test the whole pipeline offline
(silent placeholder audio, no API key, no credits used).

Env: MIRAGEA_API_KEY (required for real calls), MIRAGEA_BASE_URL (default https://miragea.ai/v1).
The key is only sent in the Authorization header to the API host and never printed.
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import wave
from typing import Any, Dict, List, Optional, Tuple

VERSION = "1.0.0"
# scene presets: gap between lines (s), max subtitle chars, speaker labels in SRT
PRESETS = {
    "koubo":       {"gap": 0.15, "max_chars": 14, "speaker_labels": False},  # 口播 / 知识博主
    "jieshuo":     {"gap": 0.30, "max_chars": 16, "speaker_labels": False},  # 电影解说 / 影视解说
    "daihuo":      {"gap": 0.10, "max_chars": 12, "speaker_labels": False},  # 带货短视频
    "shuziren":    {"gap": 0.20, "max_chars": 16, "speaker_labels": False},  # 数字人口播
    "guanggao":    {"gap": 0.40, "max_chars": 14, "speaker_labels": False},  # 广告片 / 宣传片
    "youshengshu": {"gap": 0.50, "max_chars": 20, "speaker_labels": True},   # 有声书 / 广播剧
}
DEFAULT_BASE_URL = "https://miragea.ai/v1"
UA = "Mozilla/5.0 (compatible) miragea-video-voiceover-skill/" + VERSION
SAMPLE_RATE = 24000


class SkillError(Exception):
    pass


# ---------------------------------------------------------------- API client
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):  # never forward the key to another host
        return None


class Miragea:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: float = 60):
        self.key = api_key if api_key is not None else os.environ.get("MIRAGEA_API_KEY", "")
        self.base = (base_url or os.environ.get("MIRAGEA_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        p = urllib.parse.urlsplit(self.base)
        if p.scheme not in ("http", "https") or not p.netloc or p.username or p.password:
            raise SkillError("MIRAGEA_BASE_URL must look like %s" % DEFAULT_BASE_URL)
        self.timeout = timeout
        self._caps: Optional[Dict[str, Any]] = None

    def _need_key(self):
        if not self.key:
            raise SkillError("MIRAGEA_API_KEY is not set. Create one at https://miragea.ai/workspace/api, "
                             "then export MIRAGEA_API_KEY=... (or use --dry-run to test offline).")

    def request(self, method: str, path: str, body: Optional[bytes] = None,
                ctype: Optional[str] = None, idem: Optional[str] = None) -> Any:
        self._need_key()
        headers = {"Authorization": "Bearer " + self.key, "Accept": "application/json", "User-Agent": UA}
        if ctype:
            headers["Content-Type"] = ctype
        if idem:
            headers["Idempotency-Key"] = idem
        tries = 3 if (idem or method == "GET") else 1
        last = "unknown error"
        for i in range(tries):
            req = urllib.request.Request(self.base + path, data=body, headers=headers, method=method)
            try:
                with urllib.request.build_opener(_NoRedirect()).open(req, timeout=self.timeout) as r:
                    raw = r.read()
                    return json.loads(raw.decode("utf-8")) if raw else {}
            except urllib.error.HTTPError as e:
                try:
                    err = (json.loads(e.read().decode("utf-8")) or {}).get("error") or {}
                except Exception:
                    err = {}
                msg = (err.get("message") if isinstance(err, dict) else str(err)) or "HTTP %s" % e.code
                last = "Miragea API %s: %s" % (e.code, msg)
                if e.code not in (429, 502, 503) and not (isinstance(err, dict) and err.get("retryable")):
                    raise SkillError(last)
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last = "network error: %s" % getattr(e, "reason", e)
            time.sleep(min(2 ** i, 20))
        raise SkillError(last)

    def capabilities(self) -> Dict[str, Any]:
        if self._caps is None:
            self._caps = self.request("GET", "/capabilities")
        return self._caps

    def actors(self, limit=20, offset=0) -> Dict[str, Any]:
        return self.request("GET", "/actors?" + urllib.parse.urlencode({"limit": limit, "offset": offset}))

    def wait(self, task: Dict[str, Any], max_wait: float = 600) -> Dict[str, Any]:
        tid, end = task.get("task_id"), time.time() + max_wait
        while task.get("status") not in ("succeeded", "failed"):
            if not tid or time.time() > end:
                raise SkillError("task %s did not finish in time; it keeps running server-side, "
                                 "re-run the same command (same idempotency key) to pick it up" % tid)
            time.sleep(min(float(task.get("poll_after_seconds") or 3), 30))
            task = self.request("GET", "/tasks/" + urllib.parse.quote(str(tid), safe=""))
        if task.get("status") == "failed":
            err = task.get("error") or {}
            raise SkillError("Miragea task failed: %s" % (err.get("message") or err.get("code") or "unknown"))
        return task

    def download(self, url: str) -> bytes:
        if urllib.parse.urlsplit(url).scheme not in ("http", "https"):
            raise SkillError("invalid audio_url")
        req = urllib.request.Request(url, headers={"User-Agent": UA})  # no key to CDN
        with urllib.request.urlopen(req, timeout=max(self.timeout, 120)) as r:
            return r.read()

    def tts(self, text: str, voice: Dict[str, Any], fresh=False) -> bytes:
        payload = {"text": text, "format": "wav"}
        payload.update({k: v for k, v in voice.items() if v not in (None, "", [])})
        if bool(payload.get("actor_id")) == bool(payload.get("reference_audio_url")):
            raise SkillError("each speaker needs exactly one of actor_id or reference_audio_url")
        idem = str(uuid.uuid4()) if fresh else "mvv-" + hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:40]
        task = self.wait(self.request("POST", "/audio/generations",
                                      json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                                      "application/json", idem))
        url = (task.get("result") or {}).get("audio_url")
        if not url:
            raise SkillError("task succeeded without audio_url")
        return self.download(url)

    def subtitles(self, path: str) -> Dict[str, Any]:
        rate = (self.capabilities().get("subtitles") or {}).get("points_per_second")
        if rate is None:
            raise SkillError("capabilities missing subtitles.points_per_second")
        data = open(path, "rb").read()
        b = "mvv-" + uuid.uuid4().hex
        name = os.path.basename(path).replace('"', "_")
        body = ("--%s\r\nContent-Disposition: form-data; name=\"expected_rate\"\r\n\r\n%s\r\n"
                "--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n"
                "Content-Type: application/octet-stream\r\n\r\n" % (b, rate, b, name)).encode() + data + \
               ("\r\n--%s--\r\n" % b).encode()
        idem = "mvv-sub-" + hashlib.sha256(data).hexdigest()[:32]
        task = self.wait(self.request("POST", "/subtitles/recognitions", body,
                                      "multipart/form-data; boundary=" + b, idem))
        return task.get("result") or {}


# ---------------------------------------------------------------- script parsing
LINE_RE = re.compile(r"^\s*\[(?P<who>[^\]]+)\]\s*[:：]?\s*(?P<text>.*)$")
PAUSE_RE = re.compile(r"^\s*\[(?:pause|停顿)\s*(?P<s>[\d.]+)\s*s?\]\s*$", re.I)


def parse_script(text: str) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """Script format (UTF-8 text / Markdown):

    ---                       optional front matter: one speaker per line
    narrator: actor_id=123 speed=1.05 language=en
    hero: ref=https://example.com/me.wav ref_text="sample words"
    ---
    [narrator] Opening line.
    [pause 0.6]
    [hero]: A reply.
    A line with no tag uses the previous speaker (or the first one).
    # Markdown headings, blank lines and <!-- comments --> are ignored.
    """
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    speakers: Dict[str, Dict[str, Any]] = {}
    body = text
    m = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n", text, re.S)
    if m:
        body = text[m.end():]
        for raw in m.group(1).splitlines():
            if not raw.strip() or ":" not in raw:
                continue
            name, rest = raw.split(":", 1)
            v: Dict[str, Any] = {}
            for k, val in re.findall(r'(\w+)=("[^"]*"|\S+)', rest):
                val = val.strip('"')
                k = {"ref": "reference_audio_url", "ref_text": "reference_text", "actor": "actor_id"}.get(k, k)
                if k == "speed":
                    s = float(val)
                    if not 0.25 <= s <= 4:
                        raise SkillError("speed must be 0.25-4 (speaker %s)" % name.strip())
                    v[k] = s
                elif k == "tags":
                    v[k] = [t for t in val.split(",") if t]
                else:
                    v[k] = val
            speakers[name.strip()] = v
    lines: List[Dict[str, Any]] = []
    current = next(iter(speakers), None)
    for raw in body.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        pm = PAUSE_RE.match(s)
        if pm:
            lines.append({"pause": float(pm.group("s"))})
            continue
        lm = LINE_RE.match(s)
        if lm:
            current = lm.group("who").strip()
            s = lm.group("text").strip()
            if not s:
                continue
        if current is None:
            current = "narrator"
        speakers.setdefault(current, {})
        lines.append({"speaker": current, "text": s})
    if not any("text" in l for l in lines):
        raise SkillError("script has no spoken lines")
    return speakers, lines


# ---------------------------------------------------------------- audio helpers
def wav_frames(data: bytes) -> Tuple[Tuple[int, int, int], bytes]:
    with wave.open(io.BytesIO(data)) as w:
        return (w.getnchannels(), w.getsampwidth(), w.getframerate()), w.readframes(w.getnframes())


def silence(params: Tuple[int, int, int], seconds: float) -> bytes:
    ch, sw, sr = params
    return b"\x00" * int(sr * max(seconds, 0)) * ch * sw


def placeholder_wav(text: str) -> bytes:
    """Dry-run audio: silent WAV sized like real speech (~14 chars/s CJK, ~15 chars/s Latin)."""
    secs = max(0.6, len(text) / 15.0)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SAMPLE_RATE)
        w.writeframes(silence((1, 2, SAMPLE_RATE), secs))
    return buf.getvalue()


def ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def split_caption(text: str, limit: int) -> List[str]:
    parts = [p for p in re.split(r"(?<=[。！？!?；;，,])\s*", text) if p.strip()]
    out, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) > limit:
            out.append(cur.strip()); cur = p
        else:
            cur += (" " if cur and re.match(r"[A-Za-z0-9]", p[:1]) else "") + p
    if cur.strip():
        out.append(cur.strip())
    return out or [text]


# ---------------------------------------------------------------- commands
def cmd_doctor(a) -> int:
    ok = True
    print("python      %s  %s" % (sys.version.split()[0], "OK" if sys.version_info >= (3, 9) else "NEED 3.9+"))
    ok &= sys.version_info >= (3, 9)
    key = bool(os.environ.get("MIRAGEA_API_KEY"))
    print("api key     %s" % ("set" if key else "NOT SET -> https://miragea.ai/workspace/api (use --dry-run meanwhile)"))
    if key:
        try:
            caps = Miragea(a.base_url).capabilities()
            print("api         reachable; audio max_text_length=%s" % (caps.get("audio") or {}).get("max_text_length"))
        except SkillError as e:
            ok = False; print("api         ERROR %s" % e)
    return 0 if ok else 1


def cmd_voices(a) -> int:
    data = Miragea(a.base_url).actors(a.limit, a.offset)
    items = data.get("items", [])
    if a.json:
        print(json.dumps(data, ensure_ascii=False, indent=2)); return 0
    if not items:
        print("No saved voices yet. Clone one at https://miragea.ai (5-10 s sample) or pass ref=<audio url>.")
    for it in items:
        print("%-12s %-24s %s" % (it.get("actor_id"), it.get("name", ""), it.get("language", "")))
    return 0


def _voice_from_args(a) -> Dict[str, Any]:
    v = {"actor_id": a.actor, "reference_audio_url": a.ref, "reference_text": a.ref_text,
         "speed": a.speed, "language": a.language, "model": a.model}
    return {k: x for k, x in v.items() if x not in (None, "")}


def cmd_say(a) -> int:
    audio = placeholder_wav(a.text) if a.dry_run else Miragea(a.base_url).tts(a.text, _voice_from_args(a), a.fresh)
    with open(a.output, "wb") as f:
        f.write(audio)
    print("wrote %s" % a.output)
    return 0


def cmd_script(a) -> int:
    if a.preset:
        for k, v in PRESETS[a.preset].items():
            if getattr(a, k) is None or (k == "speaker_labels" and not a.speaker_labels):
                setattr(a, k, v)
    a.gap = 0.25 if a.gap is None else a.gap
    a.max_chars = 18 if a.max_chars is None else a.max_chars
    speakers, lines = parse_script(open(a.file, encoding="utf-8").read())
    os.makedirs(a.output, exist_ok=True)
    api = None if a.dry_run else Miragea(a.base_url)
    if api:
        maxlen = (api.capabilities().get("audio") or {}).get("max_text_length")
        for l in lines:
            if "text" in l and maxlen and len(l["text"]) > int(maxlen):
                raise SkillError("line too long (%d > %s chars): %s..." % (len(l["text"]), maxlen, l["text"][:30]))
        missing = [s for s, v in speakers.items() if not (v.get("actor_id") or v.get("reference_audio_url"))]
        if missing:
            raise SkillError("speakers without a voice: %s. Add actor_id=... (see `voices`) or ref=<url> "
                             "in the front matter." % ", ".join(missing))
    params, pcm, cues, manifest, t, lead = None, [], [], [], 0.0, 0.0
    for i, l in enumerate(lines):
        if "pause" in l:
            if params:
                pcm.append(silence(params, l["pause"]))
            else:
                lead += l["pause"]  # pause before the first line: written once the WAV format is known
            t += l["pause"]; continue
        audio = placeholder_wav(l["text"]) if a.dry_run else api.tts(l["text"], speakers[l["speaker"]], a.fresh)
        p, frames = wav_frames(audio)
        if params and p != params:
            raise SkillError("line %d returned a different WAV format %s vs %s" % (i + 1, p, params))
        if params is None:
            params = p
            if lead:
                pcm.append(silence(params, lead))
        dur = len(frames) / float(p[0] * p[1] * p[2])
        pcm.append(frames)
        chunks = split_caption(l["text"], a.max_chars)
        total = sum(len(c) for c in chunks) or 1
        start = t
        for c in chunks:
            d = dur * len(c) / total
            cues.append((start, start + d, ("%s: " % l["speaker"] if a.speaker_labels else "") + c))
            start += d
        manifest.append({"line": i + 1, "speaker": l["speaker"], "text": l["text"],
                         "start": round(t, 3), "end": round(t + dur, 3)})
        t += dur
        if a.gap > 0 and i + 1 < len(lines) and "pause" not in lines[i + 1]:
            pcm.append(silence(params, a.gap)); t += a.gap
    wav_path = os.path.join(a.output, "voiceover.wav")
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(params[0]); w.setsampwidth(params[1]); w.setframerate(params[2])
        w.writeframes(b"".join(pcm))
    with open(os.path.join(a.output, "voiceover.srt"), "w", encoding="utf-8") as f:
        for n, (s, e, c) in enumerate(cues, 1):
            f.write("%d\n%s --> %s\n%s\n\n" % (n, ts(s), ts(e), c))
    with open(os.path.join(a.output, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"duration": round(t, 3), "dry_run": a.dry_run, "lines": manifest}, f, ensure_ascii=False, indent=2)
    print("wrote %s (%.1fs, %d lines) + voiceover.srt + manifest.json%s"
          % (wav_path, t, len(manifest), "  [dry-run: silent placeholder audio]" if a.dry_run else ""))
    return 0


def cmd_subtitles(a) -> int:
    res = Miragea(a.base_url).subtitles(a.media)
    srt = res.get("srt")
    if not srt:
        srt = "".join("%d\n%s --> %s\n%s\n\n" % (i, ts(float(s["start"])), ts(float(s["end"])), s.get("text", "").strip())
                      for i, s in enumerate(res.get("segments") or [], 1))
    with open(a.output, "w", encoding="utf-8") as f:
        f.write(srt)
    print("wrote %s" % a.output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="voiceover.py", description="AI video voiceover + subtitles via Miragea")
    p.add_argument("--base-url", default=None)
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    v = sub.add_parser("voices"); v.add_argument("--limit", type=int, default=20)
    v.add_argument("--offset", type=int, default=0); v.add_argument("--json", action="store_true"); v.set_defaults(fn=cmd_voices)
    s = sub.add_parser("say"); s.add_argument("text"); s.add_argument("-o", "--output", default="line.wav")
    for flag in ("--actor", "--ref", "--ref-text", "--language", "--model"):
        s.add_argument(flag)
    s.add_argument("--speed", type=float); s.add_argument("--dry-run", action="store_true")
    s.add_argument("--fresh", action="store_true"); s.set_defaults(fn=cmd_say)
    c = sub.add_parser("script"); c.add_argument("file"); c.add_argument("-o", "--output", default="voiceover_out")
    c.add_argument("--preset", choices=sorted(PRESETS), help="scene preset (koubo/jieshuo/daihuo/shuziren/guanggao/youshengshu)")
    c.add_argument("--gap", type=float, default=None, help="seconds of silence between lines (default 0.25)")
    c.add_argument("--max-chars", type=int, default=None, help="max characters per subtitle cue (default 18)")
    c.add_argument("--speaker-labels", action="store_true"); c.add_argument("--dry-run", action="store_true")
    c.add_argument("--fresh", action="store_true"); c.set_defaults(fn=cmd_script)
    t = sub.add_parser("subtitles"); t.add_argument("media"); t.add_argument("-o", "--output", default="subtitles.srt")
    t.set_defaults(fn=cmd_subtitles)
    return p


def main(argv=None) -> int:
    a = build_parser().parse_args(argv)
    try:
        return a.fn(a)
    except SkillError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    except FileNotFoundError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
