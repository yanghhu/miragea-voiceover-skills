#!/usr/bin/env python3
"""Miragea AI Voiceover MCP (Text to Speech, Podcast Generator, Subtitles) - MCP server (stdio, JSON-RPC 2.0, Python 3.9+ standard library only).

AI voiceover / text-to-speech / multi-speaker dialogue (two-host podcast, multi-character dubbing)
-> WAV + SRT, and audio/video -> SRT subtitles, through the official Miragea open API
(https://miragea.ai). Every API call is one of the documented endpoints:
  GET  /capabilities   GET /actors   POST /audio/generations   POST /subtitles/recognitions   GET /tasks/{id}

Run:   python3 server.py                 (stdio MCP server)
       python3 server.py --dry-run       (offline: no key, no network, silent placeholder audio)
       python3 server.py --self-test     (offline smoke test, prints the files it wrote)
Env:   MIRAGEA_API_KEY (required for real calls), MIRAGEA_BASE_URL (default https://miragea.ai),
       MIRAGEA_OUTPUT_DIR (where audio/subtitles are written), MIRAGEA_DRY_RUN=1 (same as --dry-run)
"""
import hashlib
import io
import json
import mimetypes
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import wave

NAME = "miragea-voiceover-mcp"
VERSION = "1.0.0"
TITLE = "Miragea AI Voiceover MCP (Text to Speech, Podcast Generator, Subtitles)"
DEFAULT_BASE = "https://miragea.ai"
ENV_KEY, ENV_BASE, ENV_OUT, ENV_DRY = "MIRAGEA_API_KEY", "MIRAGEA_BASE_URL", "MIRAGEA_OUTPUT_DIR", "MIRAGEA_DRY_RUN"
FALLBACK_KEY = ""  # older skills of this family read this variable
PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")
DRY_RATE = 24000
DRY_RUN = False


# ----------------------------------------------------------------------------- errors / helpers
class ToolError(Exception):
    def __init__(self, payload):
        super().__init__(json.dumps(payload, ensure_ascii=False))
        self.payload = payload if isinstance(payload, dict) else {"error": {"message": str(payload)}}


def err(code, message, **extra):
    return ToolError({"error": dict(code=code, message=message, **extra)})


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def api_root():
    base = (os.environ.get(ENV_BASE) or DEFAULT_BASE).rstrip("/")
    parts = urllib.parse.urlsplit(base)
    if parts.scheme not in ("http", "https") or not parts.netloc or parts.username or parts.password \
            or parts.query or parts.fragment:
        raise err("invalid_base_url", "%s must be an http(s) site root without credentials, query or fragment." % ENV_BASE)
    # The open API lives under /v1 of the service site; a bare site root gets /v1 appended.
    return base + "/v1" if parts.path in ("", "/") else base


def api_key():
    key = os.environ.get(ENV_KEY) or (os.environ.get(FALLBACK_KEY) if FALLBACK_KEY else "")
    if not key:
        raise err("missing_api_key", "Set %s (create one at https://miragea.ai/workspace/api), or start the server with --dry-run." % ENV_KEY)
    return key


def out_dir(sub=None):
    base = os.environ.get(ENV_OUT) or os.path.join(os.path.expanduser("~"), "miragea-voiceover")
    d = os.path.join(base, sub) if sub else base
    os.makedirs(d, exist_ok=True)
    return d


def fresh_path(path):
    """Never overwrite: add -2, -3 ... before the extension when the file exists."""
    path = os.path.abspath(os.path.expanduser(path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    n = 2
    while os.path.exists("%s-%d%s" % (stem, n, ext)):
        n += 1
    return "%s-%d%s" % (stem, n, ext)


def slug(text, n=24):
    s = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text).strip("-")[:n]
    return s or "audio"


# ----------------------------------------------------------------------------- official API client
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Api:
    def __init__(self, timeout=30):
        self.root = api_root()
        self.key = api_key()
        self.timeout = timeout
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, method, path, payload=None, content_type=None, idem=None, timeout=None):
        headers = {"Authorization": "Bearer " + self.key, "Accept": "application/json",
                   "User-Agent": "%s/%s" % (NAME, VERSION)}
        if content_type:
            headers["Content-Type"] = content_type
        if idem:
            headers["Idempotency-Key"] = idem
        req = urllib.request.Request(self.root + path, data=payload, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=timeout or self.timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            try:
                body = json.load(e)
            except (ValueError, UnicodeError):
                body = {"error": {"code": "http_error", "message": "API returned HTTP %s" % e.code}}
            raise ToolError(dict({"http_status": e.code}, **body)) from None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise err("request_failed", "API request failed; the submission outcome may be unknown. Retry with the "
                                        "same idempotency_key and identical input.", idempotency_key=idem) from None

    def capabilities(self):
        return self.request("GET", "/capabilities")

    def actors(self, limit, offset):
        return self.request("GET", "/actors?" + urllib.parse.urlencode({"limit": limit, "offset": offset}))

    def task(self, task_id, timeout=None):
        return self.request("GET", "/tasks/" + urllib.parse.quote(task_id, safe=""), timeout=timeout)

    def wait(self, task_id, deadline_s, tick=None):
        deadline = time.monotonic() + deadline_s
        while True:
            left = deadline - time.monotonic()
            if left <= 0:
                raise err("wait_timeout", "Task still pending. Call get_task with this task_id later; do not submit "
                                          "a new task.", task_id=task_id)
            t = self.task(task_id, timeout=min(self.timeout, left))
            if t.get("status") in ("succeeded", "failed"):
                return t
            if tick:
                tick()
            pause = t.get("poll_after_seconds", 3)
            pause = pause if isinstance(pause, (int, float)) and pause > 0 else 3
            time.sleep(min(pause, max(0, deadline - time.monotonic())))

    def generate(self, payload, idem):
        return self.request("POST", "/audio/generations", json.dumps(payload).encode(), "application/json", idem)

    def recognize(self, path, rate, idem):
        boundary = "mcp-" + uuid.uuid4().hex
        fn = os.path.basename(path).replace('"', "_").replace("\r", "_").replace("\n", "_")
        mime = mimetypes.guess_type(fn)[0] or "application/octet-stream"
        head = ('--%s\r\nContent-Disposition: form-data; name="expected_rate"\r\n\r\n%s\r\n'
                '--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\nContent-Type: %s\r\n\r\n'
                % (boundary, rate, boundary, fn, mime)).encode("utf-8")
        with open(path, "rb") as f:
            body = head + f.read() + ("\r\n--%s--\r\n" % boundary).encode()
        return self.request("POST", "/subtitles/recognitions", body, "multipart/form-data; boundary=" + boundary,
                            idem, timeout=max(self.timeout, 300))


def download(url, path):
    if urllib.parse.urlsplit(url or "").scheme not in ("http", "https"):
        raise err("invalid_audio_url", "Task result has no downloadable audio_url.")
    path = fresh_path(path)
    try:
        with urllib.request.urlopen(url, timeout=120) as src, open(path, "xb") as dst:
            while True:
                chunk = src.read(1 << 20)
                if not chunk:
                    break
                dst.write(chunk)
    except Exception:
        if os.path.exists(path):
            os.unlink(path)
        raise
    return path


# ----------------------------------------------------------------------------- WAV / SRT helpers
def silence(params, seconds):
    ch, sw, sr = params
    return b"\x00" * int(sr * max(seconds, 0)) * ch * sw


def placeholder_wav(text):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(DRY_RATE)
        w.writeframes(silence((1, 2, DRY_RATE), max(0.6, len(text) / 15.0)))
    return buf.getvalue()


def read_wav(data, where):
    try:
        with wave.open(io.BytesIO(data)) as w:
            return (w.getnchannels(), w.getsampwidth(), w.getframerate()), w.readframes(w.getnframes())
    except (wave.Error, EOFError) as e:
        raise err("wav_join_failed", "%s is not a PCM WAV the standard library can join (%s). Per-line files are "
                                     "kept in lines/; join them with ffmpeg or an audio editor." % (where, e))


def ts(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def split_caption(text, limit):
    parts = [p for p in re.split(r"(?<=[。！？!?；;，,])\s*", text) if p.strip()]
    out, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) > limit:
            out.append(cur.strip())
            cur = p
        else:
            cur += (" " if cur and re.match(r"[A-Za-z0-9]", p[:1]) else "") + p
    if cur.strip():
        out.append(cur.strip())
    return out or [text]


def split_long(text, limit):
    """Split long text into chunks <= limit characters at sentence ends (for long-form TTS)."""
    sents = [s for s in re.split(r"(?<=[。！？!?；;.\n])\s*", text) if s.strip()]
    out, cur = [], ""
    for s in sents:
        while len(s) > limit:
            if cur:
                out.append(cur)
                cur = ""
            out.append(s[:limit])
            s = s[limit:]
        if cur and len(cur) + len(s) > limit:
            out.append(cur)
            cur = s
        else:
            cur += (" " if cur and re.match(r"[A-Za-z0-9]", s[:1]) else "") + s
    if cur.strip():
        out.append(cur)
    return [c.strip() for c in out if c.strip()]


# ----------------------------------------------------------------------------- script parsing
VOICE_KEYS = ("actor_id", "reference_audio_url", "reference_text", "model", "speed", "tags", "language")
ALIASES = {"ref": "reference_audio_url", "ref_text": "reference_text", "actor": "actor_id"}
LINE_RE = re.compile(r"^\s*\[(?P<who>[^\]]+)\]\s*[:：]?\s*(?P<text>.*)$")
COLON_RE = re.compile(r"^\s*(?P<who>[^\s:：\[\]]{1,20})\s*[:：]\s*(?P<text>.+)$")
PAUSE_RE = re.compile(r"^\s*\[(?:pause|停顿)\s*(?P<s>[\d.]+)\s*s?\]\s*$", re.I)


def clean_voice(name, v):
    out = {}
    for k, val in (v or {}).items():
        k = ALIASES.get(k, k)
        if k not in VOICE_KEYS:
            raise err("invalid_speaker", "Unknown option %s for speaker %s." % (k, name))
        if val in (None, "", []):
            continue
        if k == "speed":
            val = float(val)
            if not 0.25 <= val <= 4:
                raise err("invalid_speed", "speed must be 0.25-4 (speaker %s)." % name)
        if k == "tags" and isinstance(val, str):
            val = [t for t in val.split(",") if t]
        if k == "actor_id":
            val = str(val)
        out[k] = val
    if out.get("actor_id") and out.get("reference_text"):
        raise err("invalid_speaker", "reference_text only goes with reference_audio_url (speaker %s)." % name)
    if out.get("actor_id") and out.get("reference_audio_url"):
        raise err("invalid_speaker", "Use actor_id or reference_audio_url, not both (speaker %s)." % name)
    return out


def parse_script(text, speakers):
    """Markdown script: optional front matter `Name: actor_id=... speed=1.1`, body `[Name] line`,
    `Name: line`, `[pause 0.8]`; untagged lines continue the previous speaker."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    m = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n", text, re.S)
    body = text
    if m:
        body = text[m.end():]
        for raw in m.group(1).splitlines():
            if ":" not in raw:
                continue
            name, rest = raw.split(":", 1)
            opts = {k: v.strip('"') for k, v in re.findall(r'(\w+)=("[^"]*"|\S+)', rest)}
            speakers.setdefault(name.strip(), {}).update(opts)
    lines, current = [], next(iter(speakers), None)
    for raw in body.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        pm = PAUSE_RE.match(s)
        if pm:
            lines.append({"pause": float(pm.group("s"))})
            continue
        lm = LINE_RE.match(s) or (COLON_RE.match(s) if COLON_RE.match(s) and COLON_RE.match(s).group("who") in speakers else None)
        if lm:
            current, s = lm.group("who").strip(), lm.group("text").strip()
            if not s:
                continue
        current = current or "narrator"
        lines.append({"speaker": current, "text": s})
    return lines


# ----------------------------------------------------------------------------- core: multi-line voiceover
def payload_for(text, voice, model, fmt="wav"):
    p = {"text": text, "format": fmt}
    for k in ("actor_id", "reference_audio_url", "reference_text", "speed", "tags", "language"):
        if voice.get(k) not in (None, "", []):
            p[k] = voice[k]
    if voice.get("model") or model:
        p["model"] = voice.get("model") or model
    return p


def render_lines(speakers, lines, out, gap=0.25, max_chars=18, labels=False, model=None, dry=False,
                 fresh=False, wait_timeout=600, progress=None, basename="voiceover"):
    if not any("text" in l for l in lines):
        raise err("empty_script", "The script has no spoken lines.")
    voices = {}
    for l in lines:
        if "speaker" in l:
            voices.setdefault(l["speaker"], clean_voice(l["speaker"], speakers.get(l["speaker"], {})))
    if not dry:
        missing = [s for s, v in voices.items() if not (v.get("actor_id") or v.get("reference_audio_url"))]
        if missing:
            raise err("speaker_without_voice", "Speakers without a voice: %s. Give each an actor_id (from list_voices) "
                                               "or a reference_audio_url." % ", ".join(missing))
        api = Api()
    os.makedirs(out, exist_ok=True)
    cache = os.path.join(out, "lines")
    os.makedirs(cache, exist_ok=True)
    salt = uuid.uuid4().hex if fresh else ""
    spoken = [i for i, l in enumerate(lines) if "text" in l]
    params, pcm, cues, manifest, t, lead, tasks = None, [], [], [], 0.0, 0.0, []
    for i, l in enumerate(lines):
        if "pause" in l:
            if params:
                pcm.append(silence(params, l["pause"]))
            else:
                lead += l["pause"]
            t += l["pause"]
            continue
        if dry:
            data, src = placeholder_wav(l["text"]), None
        else:
            p = payload_for(l["text"], voices[l["speaker"]], model)
            digest = hashlib.sha256((json.dumps(p, sort_keys=True, ensure_ascii=False) + salt).encode()).hexdigest()
            src = os.path.join(cache, digest[:24] + ".wav")
            if not os.path.exists(src):
                key = "mcp-" + digest[:40]
                task = api.generate(p, key)
                if task.get("status") not in ("succeeded", "failed"):
                    task = api.wait(task["task_id"], wait_timeout, tick=progress and (lambda: progress(None, None)))
                if task.get("status") != "succeeded":
                    raise ToolError({"error": task.get("error") or {"code": "task_failed"}, "task_id": task.get("task_id"),
                                     "line": i + 1, "hint": "Fix the line and call again; finished lines are reused."})
                tmp = download((task.get("result") or {}).get("audio_url"), src + ".part")
                os.replace(tmp, src)
                tasks.append(task.get("task_id"))
            with open(src, "rb") as f:
                data = f.read()
        prm, frames = read_wav(data, src or "placeholder")
        if params and prm != params:
            raise err("wav_format_mismatch", "Line %d WAV format %s differs from %s." % (i + 1, prm, params))
        if params is None:
            params = prm
            if lead:
                pcm.append(silence(params, lead))
        dur = len(frames) / float(prm[0] * prm[1] * prm[2])
        pcm.append(frames)
        chunks = split_caption(l["text"], max_chars)
        total, start = sum(len(c) for c in chunks) or 1, t
        for c in chunks:
            d = dur * len(c) / total
            cues.append((start, start + d, ("%s: " % l["speaker"] if labels else "") + c))
            start += d
        manifest.append({"line": i + 1, "speaker": l["speaker"], "text": l["text"], "start": round(t, 3),
                         "end": round(t + dur, 3), "file": os.path.relpath(src, out) if src else None})
        t += dur
        if gap > 0 and i + 1 < len(lines) and "pause" not in lines[i + 1]:
            pcm.append(silence(params, gap))
            t += gap
        if progress:
            progress(spoken.index(i) + 1, len(spoken))
    wav_path = fresh_path(os.path.join(out, basename + ".wav"))
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(params[0])
        w.setsampwidth(params[1])
        w.setframerate(params[2])
        w.writeframes(b"".join(pcm))
    srt_path = fresh_path(os.path.join(out, basename + ".srt"))
    with open(srt_path, "w", encoding="utf-8") as f:
        for n, (s, e, c) in enumerate(cues, 1):
            f.write("%d\n%s --> %s\n%s\n\n" % (n, ts(s), ts(e), c))
    man_path = fresh_path(os.path.join(out, basename + ".manifest.json"))
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump({"duration_seconds": round(t, 3), "dry_run": dry, "speakers": sorted(voices), "lines": manifest},
                  f, ensure_ascii=False, indent=2)
    return {"audio_wav": wav_path, "subtitles_srt": srt_path, "manifest_json": man_path,
            "duration_seconds": round(t, 3), "spoken_lines": len(manifest), "speakers": sorted(voices),
            "new_api_tasks": tasks, "dry_run": dry,
            "note": "dry run: silent placeholder audio, no API call" if dry else "AI-generated speech; label it as AI-generated where you publish it."}


# ----------------------------------------------------------------------------- tools
def t_get_capabilities(a, ctx):
    if is_dry(a):
        return {"dry_run": True, "message": "Offline mode: live models, tags, formats, text limits and subtitle limits "
                                            "come from GET /capabilities once %s is set." % ENV_KEY}
    return Api().capabilities()


def t_list_voices(a, ctx):
    limit, offset = int(a.get("limit", 20)), int(a.get("offset", 0))
    if not 1 <= limit <= 100 or offset < 0:
        raise err("invalid_paging", "limit must be 1-100 and offset >= 0.")
    if is_dry(a):
        return {"dry_run": True, "items": [{"actor_id": "DRY_ACTOR_A", "name": "sample voice A", "language": "zh"},
                                           {"actor_id": "DRY_ACTOR_B", "name": "sample voice B", "language": "en"}],
                "has_more": False}
    return Api().actors(limit, offset)


def t_text_to_speech(a, ctx):
    text = (a.get("text") or "").strip()
    if not text:
        raise err("missing_text", "text is required.")
    voice = clean_voice("voice", {k: a.get(k) for k in VOICE_KEYS})
    dry = is_dry(a)
    if not dry and not (voice.get("actor_id") or voice.get("reference_audio_url")):
        raise err("missing_voice", "Give actor_id (from list_voices) or reference_audio_url (+ reference_text).")
    if a.get("subtitles"):
        limit = int(a.get("max_chunk_chars") or 0)
        if not limit and not dry:
            try:
                limit = int(Api().capabilities().get("audio", {}).get("max_text_length") or 0)
            except ToolError:
                limit = 0
        chunks = split_long(text, min(limit or 300, 300))
        out = a.get("output_dir") or out_dir("tts-" + time.strftime("%Y%m%d-%H%M%S") + "-" + slug(text, 12))
        return render_lines({"voice": voice}, [{"speaker": "voice", "text": c} for c in chunks], out,
                            gap=float(a.get("gap", 0.15)), max_chars=int(a.get("max_chars", 18)), dry=dry,
                            fresh=bool(a.get("fresh")), wait_timeout=float(a.get("wait_timeout", 600)),
                            progress=ctx.get("progress"), basename="speech")
    fmt = a.get("format") or "mp3"
    default_name = "speech-%s-%s.%s" % (time.strftime("%Y%m%d-%H%M%S"), slug(text, 12), fmt)
    path = a.get("output_path") or os.path.join(out_dir(), default_name)
    if dry:
        path = fresh_path(os.path.splitext(path)[0] + ".wav")
        with open(path, "wb") as f:
            f.write(placeholder_wav(text))
        return {"dry_run": True, "saved_to": path, "note": "silent placeholder WAV, no API call"}
    p = payload_for(text, voice, None, fmt)
    key = a.get("idempotency_key") or "mcp-tts-" + hashlib.sha256(
        (json.dumps(p, sort_keys=True, ensure_ascii=False) + (uuid.uuid4().hex if a.get("fresh") else "")).encode()).hexdigest()[:40]
    api = Api()
    task = api.generate(p, key)
    task["idempotency_key"] = key
    if a.get("wait", True) and task.get("status") not in ("succeeded", "failed"):
        task = api.wait(task["task_id"], float(a.get("wait_timeout", 600)))
        task["idempotency_key"] = key
    if task.get("status") == "succeeded":
        task["saved_to"] = download((task.get("result") or {}).get("audio_url"), path)
        task["note"] = "AI-generated speech; label it as AI-generated where you publish it."
    return task


def t_dialogue_voiceover(a, ctx):
    speakers = {}
    for name, v in (a.get("speakers") or {}).items():
        speakers[name] = dict(v or {})
    if a.get("script"):
        lines = parse_script(a["script"], speakers)
    else:
        lines = []
        for l in a.get("lines") or []:
            if "pause" in l:
                lines.append({"pause": float(l["pause"])})
            elif (l.get("text") or "").strip():
                lines.append({"speaker": l.get("speaker") or "narrator", "text": l["text"].strip()})
    if not lines:
        raise err("missing_script", "Give script (markdown, `[Name] line`) or lines ([{speaker, text}]).")
    style = a.get("style") or "podcast"
    gap_default, chars_default = {"podcast": (0.35, 18), "dubbing": (0.15, 16), "audiobook": (0.5, 20)}.get(style, (0.25, 18))
    title = a.get("title") or style
    out = a.get("output_dir") or out_dir("%s-%s" % (time.strftime("%Y%m%d-%H%M%S"), slug(title)))
    return render_lines(speakers, lines, out, gap=float(a.get("gap", gap_default)),
                        max_chars=int(a.get("max_chars", chars_default)),
                        labels=bool(a.get("speaker_labels", style != "dubbing")), model=a.get("model"),
                        dry=is_dry(a), fresh=bool(a.get("fresh")), wait_timeout=float(a.get("wait_timeout", 600)),
                        progress=ctx.get("progress"), basename=a.get("basename") or "voiceover")


def t_generate_subtitles(a, ctx):
    path = os.path.abspath(os.path.expanduser(a.get("file_path") or ""))
    if not os.path.isfile(path):
        raise err("file_not_found", "file_path must be a local audio or video file: %s" % path)
    fmt = a.get("format") or "srt"
    if fmt not in ("srt", "txt", "json"):
        raise err("invalid_format", "format must be srt, txt or json.")
    target = a.get("output_path") or os.path.splitext(path)[0] + "." + fmt
    if is_dry(a):
        target = fresh_path(os.path.splitext(target)[0] + ".dryrun." + fmt)
        sample = {"srt": "1\n00:00:00,000 --> 00:00:02,000\n[dry run] subtitles appear here\n\n",
                  "txt": "[dry run] transcript appears here\n",
                  "json": json.dumps({"dry_run": True, "segments": []}, indent=2)}[fmt]
        with open(target, "w", encoding="utf-8") as f:
            f.write(sample)
        return {"dry_run": True, "saved_to": target, "note": "no upload, no API call"}
    api = Api()
    caps = api.capabilities().get("subtitles", {})
    rate = a.get("expected_rate", caps.get("points_per_second"))
    if rate is None:
        raise err("rate_unknown", "capabilities.subtitles.points_per_second missing; pass expected_rate.")
    max_mb = caps.get("max_upload_mb")
    if max_mb and os.path.getsize(path) > float(max_mb) * 1024 * 1024:
        raise err("file_too_large", "File exceeds capabilities.subtitles.max_upload_mb (%s MB)." % max_mb)
    key = a.get("idempotency_key") or "mcp-sub-" + hashlib.sha256(
        ("%s|%s|%s|%s" % (path, os.path.getsize(path), os.path.getmtime(path), rate)).encode()).hexdigest()[:40]
    task = api.recognize(path, rate, key)
    if a.get("wait", True) and task.get("status") not in ("succeeded", "failed"):
        task = api.wait(task["task_id"], float(a.get("wait_timeout", 1800)))
    task["idempotency_key"] = key
    if task.get("status") == "succeeded":
        res = task.get("result") or {}
        value = json.dumps(res, ensure_ascii=False, indent=2) if fmt == "json" else res.get(fmt, "")
        target = fresh_path(target)
        with open(target, "w", encoding="utf-8") as f:
            f.write(value)
        task["saved_to"] = target
        preview = res.get("txt") or res.get("text") or ""
        task["result"] = {"language": res.get("language"), "segments": len(res.get("segments") or []),
                          "preview": preview[:400]}
    return task


def t_get_task(a, ctx):
    tid = a.get("task_id")
    if not tid:
        raise err("missing_task_id", "task_id is required.")
    api = Api()
    task = api.wait(tid, float(a.get("wait_timeout", 600))) if a.get("wait") else api.task(tid)
    if a.get("output_path") and task.get("status") == "succeeded":
        res = task.get("result") or {}
        if task.get("kind") == "audio_generation":
            task["saved_to"] = download(res.get("audio_url"), a["output_path"])
        else:
            fmt = a.get("subtitle_format") or "srt"
            p = fresh_path(a["output_path"])
            with open(p, "w", encoding="utf-8") as f:
                f.write(json.dumps(res, ensure_ascii=False, indent=2) if fmt == "json" else res.get(fmt, ""))
            task["saved_to"] = p
    return task


def is_dry(a):
    return DRY_RUN or bool(a.get("dry_run"))


VOICE_PROPS = {
    "actor_id": {"type": "string", "description": "Saved voice/character id from list_voices."},
    "reference_audio_url": {"type": "string", "description": "Public http(s) URL of a reference clip for voice cloning (only with the speaker's consent)."},
    "reference_text": {"type": "string", "description": "Exact words spoken in the reference clip (only with reference_audio_url)."},
    "model": {"type": "string", "description": "Generation mode id from get_capabilities audio.models (e.g. expressive or standard)."},
    "speed": {"type": "number", "minimum": 0.25, "maximum": 4},
    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tone/emotion tag labels offered by the chosen mode (see get_capabilities)."},
    "language": {"type": "string", "description": "Language hint for the reference clip."},
}
DRY = {"dry_run": {"type": "boolean", "description": "Offline test: silent placeholder output, no key, no API call."}}
OUT = {"output_dir": {"type": "string", "description": "Folder for the WAV/SRT/manifest (default: %s or ~/miragea-voiceover)." % ENV_OUT}}

TOOLS = [
    dict(name="get_capabilities", fn=t_get_capabilities,
         title="List voiceover capabilities",
         description="Read the live voiceover & subtitle capabilities of this account: AI voiceover / text-to-speech generation modes (model), tone tags, audio formats, speed range, per-request text limit, and subtitle upload/duration limits and current rate. Read-only, creates no task.",
         annotations={"readOnlyHint": True, "openWorldHint": True},
         inputSchema={"type": "object", "properties": dict(DRY)}),
    dict(name="list_voices", fn=t_list_voices,
         title="List saved voices",
         description="List the saved voices/characters in the account (including cloned voices) with actor_id, name and language, to pick voices for text_to_speech and dialogue_voiceover. Read-only.",
         annotations={"readOnlyHint": True, "openWorldHint": True},
         inputSchema={"type": "object", "properties": dict({"limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                                                             "offset": {"type": "integer", "minimum": 0, "default": 0}}, **DRY)}),
    dict(name="text_to_speech", fn=t_text_to_speech,
         title="Text to speech (AI voiceover)",
         description="Text to speech (TTS / AI voiceover): speak a text with a saved voice (actor_id) or clone a voice from a reference clip (reference_audio_url + reference_text; only with the speaker's consent). Output mp3/wav/flac/opus/aac/pcm, optional speed 0.25-4 and tone tags. With subtitles=true (long-form mode) the text is split into sentences, joined into one WAV, and an SRT file plus per-line timing manifest are written too. Creates generation tasks and uses account credits.",
         annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
         inputSchema={"type": "object", "required": ["text"], "properties": dict(
             {"text": {"type": "string", "description": "Text to speak."}},
             **VOICE_PROPS,
             format={"type": "string", "enum": ["mp3", "wav", "flac", "opus", "aac", "pcm"], "default": "mp3"},
             output_path={"type": "string", "description": "File to write (never overwritten; a -2 suffix is added)."},
             subtitles={"type": "boolean", "default": False, "description": "Long-form mode: split into sentences, join into one WAV and also write an SRT + timing manifest."},
             output_dir=OUT["output_dir"],
             max_chars={"type": "integer", "default": 18, "description": "Max characters per subtitle cue (subtitles mode)."},
             wait={"type": "boolean", "default": True},
             wait_timeout={"type": "number", "default": 600},
             idempotency_key={"type": "string", "description": "Reuse to resume an uncertain submission."},
             fresh={"type": "boolean", "description": "New take instead of returning the earlier identical task."},
             **DRY)}),
    dict(name="dialogue_voiceover", fn=t_dialogue_voiceover,
         title="Multi-speaker dialogue voiceover (podcast / dubbing)",
         description="Multi-speaker dialogue voiceover / two-host podcast generator: a dialogue script (`[Host A] line` or `Host A: line`, `[pause 0.8]` for silence) where every speaker has its own voice is voiced line by line, joined into one WAV, with SRT subtitles (optionally speaker-labelled) and a per-line timing manifest.json. For two-host podcasts, AI podcasts, multi-character video dubbing, drama/animation dialogue and multi-voice audiobooks. Finished lines are cached: call again with the same arguments to resume after a timeout, and editing one line regenerates only that line. One generation task per line; uses account credits.",
         annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
         inputSchema={"type": "object", "properties": dict(
             speakers={"type": "object", "description": "Map speaker name -> voice, e.g. {\"Host A\": {\"actor_id\": \"...\"}, \"Host B\": {\"reference_audio_url\": \"https://...\", \"reference_text\": \"...\"}}.",
                       "additionalProperties": {"type": "object", "properties": VOICE_PROPS}},
             script={"type": "string", "description": "Markdown script. Lines `[Name] text` or `Name: text`, `[pause 0.8]` for silence, `#` comments. Optional front matter `Name: actor_id=... speed=1.1`."},
             lines={"type": "array", "description": "Alternative to script: [{speaker, text}] or [{pause: seconds}].",
                    "items": {"type": "object", "properties": {"speaker": {"type": "string"}, "text": {"type": "string"}, "pause": {"type": "number"}}}},
             style={"type": "string", "enum": ["podcast", "dubbing", "audiobook"], "default": "podcast", "description": "Sets default gap between lines, subtitle cue length and speaker labels."},
             title={"type": "string", "description": "Used in the output folder name."},
             model={"type": "string", "description": "Default generation mode for speakers without model."},
             gap={"type": "number", "description": "Seconds of silence between lines."},
             max_chars={"type": "integer", "description": "Max characters per subtitle cue."},
             speaker_labels={"type": "boolean", "description": "Prefix subtitle cues with the speaker name."},
             fresh={"type": "boolean", "description": "Regenerate every line instead of reusing finished lines."},
             wait_timeout={"type": "number", "default": 600, "description": "Seconds to wait per line."},
             basename={"type": "string", "default": "voiceover"},
             output_dir=OUT["output_dir"], **DRY)}),
    dict(name="generate_subtitles", fn=t_generate_subtitles,
         title="Generate subtitles (SRT) from audio or video",
         description="Subtitle generator: upload a local audio or video file and get timed SRT subtitles, or a TXT transcript / JSON segments (auto subtitles for video, audio to SRT, speech to text). The current rate is sent as expected_rate and the server rejects the job if the rate changed. Creates a recognition task and uses account credits.",
         annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
         inputSchema={"type": "object", "required": ["file_path"], "properties": dict(
             file_path={"type": "string", "description": "Local audio or video file."},
             format={"type": "string", "enum": ["srt", "txt", "json"], "default": "srt"},
             output_path={"type": "string", "description": "Default: next to the media file (never overwritten)."},
             expected_rate={"type": "number", "description": "Lock the subtitle rate you confirmed (capabilities.subtitles.points_per_second)."},
             wait={"type": "boolean", "default": True}, wait_timeout={"type": "number", "default": 1800},
             idempotency_key={"type": "string"}, **DRY)}),
    dict(name="get_task", fn=t_get_task,
         title="Check or resume a task",
         description="Check or keep waiting for an existing task (voice generation or subtitle recognition) and save its audio or subtitles to a file. Use it after a wait timeout or network error instead of submitting a new task.",
         annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
         inputSchema={"type": "object", "required": ["task_id"], "properties": dict(
             task_id={"type": "string"}, wait={"type": "boolean", "default": False},
             wait_timeout={"type": "number", "default": 600},
             output_path={"type": "string", "description": "Save the audio or subtitles of a succeeded task here."},
             subtitle_format={"type": "string", "enum": ["srt", "txt", "json"], "default": "srt"})}),
]
TOOL_MAP = {t["name"]: t for t in TOOLS}

PROMPTS = [
    dict(name="two_host_podcast", title="Two-host podcast script",
         description="Write a two-host podcast script in the format dialogue_voiceover expects (alternating hosts, chapters, pauses).",
         arguments=[{"name": "topic", "description": "Topic or source text", "required": True},
                    {"name": "minutes", "description": "Target length in minutes", "required": False}]),
    dict(name="multi_character_dubbing", title="Multi-character dubbing script",
         description="Turn dialogue, subtitles or a story into a multi-character dubbing script for dialogue_voiceover.",
         arguments=[{"name": "source", "description": "Dialogue, subtitles or story text to turn into a dubbing script", "required": True}]),
]


def prompt_text(name, args):
    if name == "two_host_podcast":
        return ("Write a two-host podcast script of about {minutes} minutes on the topic below, to be voiced with the dialogue_voiceover tool.\nFormat: one line per utterance, written as `[Host A] text` or `[Host B] text`; put a line `[pause 0.8]` between chapters; `# Chapter title` lines are comments and are not spoken. Conversational, short sentences, real back-and-forth, no stage directions. Afterwards list the two speaker names and remind me to pick an actor_id with list_voices or give a reference clip for each, then call dialogue_voiceover (style=podcast).\nTopic / source: {topic}").replace("{topic}", args.get("topic", "")).replace("{minutes}", str(args.get("minutes") or "5"))
    return ("Rewrite the material below as a multi-character dubbing script for the dialogue_voiceover tool.\nFormat: one line per utterance as `[Character] text`, narration as `[Narrator]`, a line `[pause 0.5]` where a pause is needed; drop stage directions, split long sentences. Finally list every character name and remind me to choose a voice for each (list_voices actor_id or a reference clip), then call dialogue_voiceover (style=dubbing).\nMaterial: {source}").replace("{source}", args.get("source", ""))


# ----------------------------------------------------------------------------- JSON-RPC over stdio
def send(msg):
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def public_tool(t):
    return {k: v for k, v in t.items() if k != "fn"}


def handle(msg):
    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
    if method == "initialize":
        want = params.get("protocolVersion")
        return {"protocolVersion": want if want in PROTOCOLS else PROTOCOLS[0],
                "capabilities": {"tools": {"listChanged": False}, "prompts": {"listChanged": False}},
                "serverInfo": {"name": NAME, "title": TITLE, "version": VERSION},
                "instructions": "AI voiceover / text to speech / multi-speaker dialogue voiceover (two-host podcast, multi-character dubbing) / subtitle generation. Start with get_capabilities and list_voices; use text_to_speech for a single text, dialogue_voiceover for scripts (WAV + SRT + manifest.json), generate_subtitles for audio/video to SRT. Generation tools use account credits, so confirm the script and voices with the user first. Clone a voice only with the speaker's consent, and label AI-generated audio where it is published."}
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": [public_tool(t) for t in TOOLS]}
    if method == "prompts/list":
        return {"prompts": PROMPTS}
    if method == "prompts/get":
        name = params.get("name")
        if name not in {p["name"] for p in PROMPTS}:
            raise KeyError(name)
        return {"messages": [{"role": "user", "content": {"type": "text", "text": prompt_text(name, params.get("arguments") or {})}}]}
    if method == "tools/call":
        tool = TOOL_MAP.get(params.get("name"))
        if not tool:
            return {"content": [{"type": "text", "text": "Unknown tool %s" % params.get("name")}], "isError": True}
        token = (params.get("_meta") or {}).get("progressToken")
        state = {"n": 0}

        def progress(done, total):
            if token is None:
                return
            state["n"] = done if done is not None else state["n"]
            note = {"progressToken": token, "progress": state["n"] if done is not None else state["n"] + 0.5}
            if total:
                note["total"] = total
            send({"jsonrpc": "2.0", "method": "notifications/progress", "params": note})

        try:
            result = tool["fn"](params.get("arguments") or {}, {"progress": progress})
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}], "isError": False}
        except ToolError as e:
            return {"content": [{"type": "text", "text": json.dumps(e.payload, ensure_ascii=False, indent=2)}], "isError": True}
        except Exception as e:  # report, keep serving
            return {"content": [{"type": "text", "text": json.dumps({"error": {"code": type(e).__name__, "message": str(e)}}, ensure_ascii=False)}], "isError": True}
    raise LookupError(method)


def serve():
    log("%s %s on stdio%s; API root %s" % (NAME, VERSION, " [dry-run]" if DRY_RUN else "", safe_root()))
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
        except ValueError:
            send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}})
            continue
        for m in (msg if isinstance(msg, list) else [msg]):
            if "method" not in m:
                continue  # responses to our (none) requests
            if "id" not in m:
                continue  # notifications: initialized, cancelled ...
            try:
                send({"jsonrpc": "2.0", "id": m["id"], "result": handle(m)})
            except LookupError as e:
                send({"jsonrpc": "2.0", "id": m["id"], "error": {"code": -32601, "message": "Method not found: %s" % e}})
            except KeyError as e:
                send({"jsonrpc": "2.0", "id": m["id"], "error": {"code": -32602, "message": "Unknown prompt %s" % e}})
            except Exception as e:
                send({"jsonrpc": "2.0", "id": m["id"], "error": {"code": -32603, "message": str(e)}})


def safe_root():
    try:
        return api_root()
    except ToolError:
        return "invalid"


def self_test():
    d = tempfile.mkdtemp(prefix=NAME + "-")
    script = "---\nA: actor_id=DRY_A\nB: actor_id=DRY_B\n---\n[A] 大家好，欢迎收听。\n[B] Hi, welcome back!\n[pause 0.5]\nA: 今天聊聊 AI 配音。\n"
    r1 = t_dialogue_voiceover({"script": script, "dry_run": True, "output_dir": d, "title": "selftest"}, {})
    r2 = t_text_to_speech({"text": "第一句。第二句！Third sentence.", "subtitles": True, "dry_run": True,
                           "output_dir": os.path.join(d, "tts")}, {})
    print(json.dumps({"ok": True, "dialogue": r1, "tts": r2}, ensure_ascii=False, indent=2))
    return 0


def main(argv=None):
    global DRY_RUN
    argv = sys.argv[1:] if argv is None else argv
    if "--version" in argv:
        print(VERSION)
        return 0
    DRY_RUN = "--dry-run" in argv or os.environ.get(ENV_DRY, "") not in ("", "0", "false")
    if "--self-test" in argv:
        return self_test()
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    serve()
    return 0


if __name__ == "__main__":
    sys.exit(main())
