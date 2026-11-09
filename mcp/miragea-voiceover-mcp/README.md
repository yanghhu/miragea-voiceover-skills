# AI Voiceover MCP · Text to Speech MCP · Podcast Generator MCP · Subtitle Generator MCP (Miragea)

**miragea-voiceover-mcp** is an open-source MCP server (Model Context Protocol, stdio) that turns the official Miragea API (https://miragea.ai) into tools for Claude Desktop, Cursor, WorkBuddy, Cherry Studio and any MCP client: **AI voiceover, text to speech (TTS), voice cloning, multi-speaker dialogue voiceover (two-host podcast generator, multi-character dubbing) and subtitle generation**. A dialogue script goes in; a joined **WAV + timed SRT subtitles + per-line timing manifest.json** come out. Existing audio or video can be transcribed to SRT / TXT / JSON. Pure Python 3.9+ standard library, no GPU, no third-party dependencies.

> 中文：AI配音 MCP / 文字转语音 MCP / 播客生成 MCP / 字幕生成 MCP（Miragea 海外版）。双人播客、多人视频配音一次输出 WAV + SRT。见文末[中文说明](#中文说明)。国内用户请用 [quips-voiceover-mcp](../quips-voiceover-mcp)。

- Service: Miragea, https://miragea.ai (create an API key at https://miragea.ai/workspace/api)
- Version 1.0.0 · MIT · Repo: [yanghhu/miragea-voiceover-skills](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/mcp/miragea-voiceover-mcp)
- Keywords: AI voiceover MCP, text to speech MCP, TTS MCP server, AI podcast generator, two-host podcast, multi-speaker TTS, dialogue dubbing, voice cloning, subtitle generator MCP, SRT, speech to text

## Contents
[What it does](#what-it-does) · [Who it is for](#who-it-is-for) · [Quick start](#quick-start) · [Client configs](#client-configs) · [Tools](#tools) · [Script format](#script-format-two-host-podcast--multi-speaker-dubbing) · [Inputs and outputs](#inputs-and-outputs) · [Offline dry run](#offline-dry-run-no-key) · [FAQ](#faq) · [Comparison](#how-it-differs) · [Limits](#limits-and-responsible-use)

## What it does

1. **Text to speech / AI voiceover** — text to mp3 / wav / flac / opus / aac / pcm with a saved voice (`actor_id`) or a voice cloned from a reference clip (`reference_audio_url` + `reference_text`); speed 0.25-4x; tone tags offered by the chosen mode.
2. **Long-form narration with subtitles** — `text_to_speech` with `subtitles=true` splits the text into sentences, voices each, joins one WAV and writes an SRT plus per-line timings.
3. **Two-host podcast generator** — a script for two hosts becomes a full episode WAV with speaker-labelled SRT.
4. **Multi-speaker dialogue voiceover / multi-character dubbing** — narrator, character A, character B... each with its own voice, one call for the whole track and its subtitles (drama, animation, story videos, multi-voice audiobooks).
5. **Subtitle generator** — local audio or video to SRT subtitles, a TXT transcript or JSON segments.
6. **Resumable** — lines are cached; call again with the same arguments to continue after a timeout, and editing one line regenerates only that line.

## Who it is for

| Who | Typical use |
|---|---|
| Podcasters, newsletter writers | Turn an article into a two-host conversation and get the episode audio plus subtitles |
| Video creators | Narration, recaps, story videos and dialogue dubbing with SRT ready for the editor |
| Educators and trainers | Lesson narration, slide voiceover, conversational courses with several presenters |
| Product and marketing teams | Demo and promo narration; translated scripts voiced separately (your AI client translates) |
| Developers and agent builders | Chain "write script -> voice -> subtitles" inside any MCP client or custom agent |
| Editors and subtitlers | Batch SRT / TXT from interviews, meetings and existing videos |

## Quick start

1. Create an API key at https://miragea.ai/workspace/api.
2. Have Python 3.9+ (`python3 --version`); optionally install [uv](https://docs.astral.sh/uv/) to run with `uvx`.
3. Add one of the configs below to your MCP client, replace `your-api-key`, restart the client.
4. Ask: "List my voices", then "Make examples/two-host-podcast.md into a two-host podcast".

## Client configs

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "miragea-voiceover": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yanghhu/miragea-voiceover-skills#subdirectory=mcp/miragea-voiceover-mcp",
        "miragea-voiceover-mcp"
      ],
      "env": {
        "MIRAGEA_API_KEY": "your-api-key"
      }
    }
  }
}
```
Or download [`mcp/dist/miragea-voiceover-mcp-1.0.0.mcpb`](https://github.com/yanghhu/miragea-voiceover-skills/raw/main/mcp/dist/miragea-voiceover-mcp-1.0.0.mcpb) and open it to install as a Claude Desktop extension (it asks for the API key; needs Python 3.9+).

### Cursor (`~/.cursor/mcp.json` or `.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "miragea-voiceover": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yanghhu/miragea-voiceover-skills#subdirectory=mcp/miragea-voiceover-mcp",
        "miragea-voiceover-mcp"
      ],
      "env": {
        "MIRAGEA_API_KEY": "your-api-key"
      }
    }
  }
}
```

### WorkBuddy (`~/.workbuddy/mcp.json`, or Plugins -> MCP servers -> Configure MCP)
```json
{
  "mcpServers": {
    "miragea-voiceover": {
      "type": "stdio",
      "command": "python3",
      "args": [
        "/absolute/path/miragea-voiceover-skills/mcp/miragea-voiceover-mcp/miragea_voiceover_mcp/server.py"
      ],
      "env": {
        "MIRAGEA_API_KEY": "your-api-key"
      }
    }
  }
}
```
Then click "Trust" in the connector / MCP manager. WorkBuddy and CodeBuddy users can also add this repository as a plugin marketplace: `/plugin marketplace add yanghhu/miragea-voiceover-skills` and install the `miragea-voiceover-mcp` plugin (MCP config + usage skill included).

### Cherry Studio (Settings -> MCP Servers -> Add -> Import from JSON)
```json
{
  "mcpServers": {
    "miragea-voiceover": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yanghhu/miragea-voiceover-skills#subdirectory=mcp/miragea-voiceover-mcp",
        "miragea-voiceover-mcp"
      ],
      "env": {
        "MIRAGEA_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Plain Python (Cline, Windsurf, Continue, Claude Code and any stdio client)
```json
{
  "mcpServers": {
    "miragea-voiceover": {
      "command": "python3",
      "args": [
        "/absolute/path/miragea-voiceover-skills/mcp/miragea-voiceover-mcp/miragea_voiceover_mcp/server.py"
      ],
      "env": {
        "MIRAGEA_API_KEY": "your-api-key"
      }
    }
  }
}
```
On Windows use `python` or `py` as the command.

Optional env: `MIRAGEA_OUTPUT_DIR` (output folder, default `~/miragea-voiceover`), `MIRAGEA_BASE_URL` (service root, default `https://miragea.ai`; `/v1` is added automatically, a root that already ends in `/v1` is used as is), `MIRAGEA_DRY_RUN=1` (offline).

## Tools

| Tool | What it does | Main input | Output |
|---|---|---|---|
| `get_capabilities` | Live generation modes, tone tags, audio formats, speed range, per-request text limit, subtitle limits and current rate | none | capabilities JSON |
| `list_voices` | Saved voices/characters in the account, including cloned voices | `limit` 1-100, `offset` | `actor_id`, `name`, `language` |
| `text_to_speech` | Text to speech / AI voiceover | `text`; `actor_id` or `reference_audio_url` (+`reference_text`); optional `model`, `format`, `speed`, `tags`, `subtitles` | audio file path; with `subtitles=true`: WAV + SRT + manifest |
| `dialogue_voiceover` | Multi-speaker dialogue voiceover / two-host podcast generator | `script` or `lines`; `speakers` (name -> voice); `style` podcast/dubbing/audiobook | `voiceover.wav` + `voiceover.srt` + `voiceover.manifest.json` |
| `generate_subtitles` | Subtitle generator: audio/video to SRT / TXT / JSON | `file_path`, `format` | subtitle file path + language, segment count, preview |
| `get_task` | Check or resume a task and save its result | `task_id`, `wait`, `output_path` | task JSON (with saved path) |

Two prompt templates are included: `two_host_podcast` (write a two-host podcast script on a topic) and `multi_character_dubbing` (turn dialogue or a story into a multi-character dubbing script).

Start with `get_capabilities` and `list_voices`. Generation tools use account credits, so have your assistant confirm the script and voices with you first.

## Script format (two-host podcast / multi-speaker dubbing)

```markdown
---
Host A: actor_id=REPLACE_WITH_ACTOR_ID
Host B: actor_id=REPLACE_WITH_ANOTHER_ACTOR_ID
---
# Intro
[Host A] Welcome back to the show. Today: how to make a podcast with AI.
[Host B] Short answer: once the script is ready, the voices and the subtitles come out in one step.
[pause 0.8]
# Part one: the script
[Host A] So how do you write something that sounds good out loud?
[Host B] Short sentences, plain words, and real back-and-forth between the two of us.
[pause 0.8]
# Outro
[Host A] That's it for today. See you next time.
[Host B] See you!
```

- The optional block between `---` maps speakers to voices: `Name: actor_id=...` or `ref=<clip URL> ref_text="exact words"`, plus optional `speed=1.1`, `model=...`, `tags=a,b`, `language=en`.
- One utterance per line: `[Name] text`; speakers already declared can also be written `Name: text`. Untagged lines continue the previous speaker.
- `[pause 0.8]` inserts 0.8 s of silence; lines starting with `#` are comments.
- Or skip the block and pass `speakers` as a tool argument: `{"Host A": {"actor_id": "..."}, "Host B": {"reference_audio_url": "https://...", "reference_text": "..."}}`.
- Examples: [examples/two-host-podcast.md](examples/two-host-podcast.md), [examples/multi-character-dubbing.md](examples/multi-character-dubbing.md).

`style` presets: `podcast` (0.35 s between lines, speaker-labelled subtitles), `dubbing` (0.15 s, no labels, easier to sync to picture), `audiobook` (0.5 s). Override with `gap`, `max_chars`, `speaker_labels`.

## Inputs and outputs

| Tool | Location | Files |
|---|---|---|
| `dialogue_voiceover` | `output_dir`, default `~/miragea-voiceover/<time>-<title>/` | `voiceover.wav`, `voiceover.srt`, `voiceover.manifest.json` (speaker, text, start/end seconds per line), `lines/` cache |
| `text_to_speech` | `output_path`, default `~/miragea-voiceover/speech-<time>-<text>.<format>` | audio file; with `subtitles=true` the same set as dialogue_voiceover |
| `generate_subtitles` | `output_path`, default next to the media file | `.srt` / `.txt` / `.json` |

Nothing is overwritten (a `-2` suffix is added). Tool results are JSON with absolute paths, duration, task IDs and idempotency keys.

## Offline dry run (no key)

```bash
git clone https://github.com/yanghhu/miragea-voiceover-skills.git && cd miragea-voiceover-skills/mcp/miragea-voiceover-mcp
python3 miragea_voiceover_mcp/server.py --self-test   # silent placeholder WAV + real SRT/timings, prints the paths
python3 miragea_voiceover_mcp/server.py --dry-run     # start the MCP server offline and try the whole flow in your client
```

## FAQ

**What is miragea-voiceover-mcp?**
An MCP server. Added to Claude Desktop, Cursor, WorkBuddy, Cherry Studio or another MCP client, it lets the AI call Miragea's voiceover and subtitle API: text to speech, voice cloning, multi-speaker dialogue voiceover (two-host podcasts, multi-character dubbing) and audio/video to SRT.

**Can it generate a two-host podcast?**
Yes. Write the conversation as `[Host A] ...` / `[Host B] ...` and call `dialogue_voiceover` (style=podcast). Each host gets its own voice; you get one episode WAV and a speaker-labelled SRT. No script yet? Use the `two_host_podcast` prompt to have the assistant draft one.

**How many speakers can a dubbing script have?**
The server sets no speaker limit; every speaker needs a voice (`actor_id` or a reference clip). Each line is one generation request, and the per-request text limit is `audio.max_text_length` from `get_capabilities`.

**How do I use my own voice?**
Use a saved voice from your Miragea account (`actor_id`), or give a publicly reachable reference clip URL (`reference_audio_url`) with the exact words spoken in it (`reference_text`). Only clone your own voice or one you have permission to use.

**Do the SRT files work in video editors?**
They are standard SRT (index, `00:00:01,000 --> 00:00:03,000`, text) and can be imported by editors that accept SRT. Timings follow the real audio length of each line; long lines are split at punctuation.

**Can I try it without an API key?**
Yes: start with `--dry-run` or pass `dry_run: true`. You get silent placeholder audio with real-format subtitles and timings, no network calls, no credits used.

**My client timed out on a long script. What now?**
Finished lines are cached in `lines/` inside the output folder. Call again with the same arguments (same `output_dir`) and only the missing lines are generated. A task that outlives its wait returns a `task_id`; fetch it with `get_task` instead of resubmitting. Progress notifications are sent when the client provides a progressToken.

**How is it billed?**
Generation and recognition use your Miragea account credits; current rules come from `get_capabilities` and the Miragea site. This open-source server adds no charge.

**Where does my data go?**
Only to the official Miragea API (default `https://miragea.ai`). The key is read from the environment and never written to files or logs; audio and subtitles are saved on your machine.

**Can it translate or pick an output language?**
The API has no output-language parameter: speech is in the language of the text you send. For a dub in another language, have your AI client translate the script first. `language` is only a hint for the reference clip.

**How is this different from the Agent Skills in the same repository?**
The skills are workflows plus scripts for agents that can run Python; the MCP server exposes the same official API as standard tools any MCP client can call directly.

## How it differs

| | This MCP server | Typical TTS MCP / TTS tools | Manual recording + hand-made subtitles |
|---|---|---|---|
| Multi-speaker / two-host podcast | One script, many voices, one joined track | Usually one clip, one voice at a time | Record each part, then edit |
| Subtitles | SRT aligned to real audio length | Usually audio only | Transcribe and time by hand |
| Timing data | Per-line start/end manifest.json | None | Manual markers |
| Edits | Only the changed line is regenerated | Regenerate everything | Re-record |
| Audio/video to subtitles | Built in (`generate_subtitles`) | Separate tool | Manual |
| Requirements | Python 3.9+ standard library, no GPU | Varies | Mic and editing software |

## Limits and responsible use

- **Credits and limits**: generation and recognition use account credits; text limit, modes, tags and subtitle size/duration limits come live from `get_capabilities`.
- **Reference clips** must be http(s) URLs the service can fetch; upload local files somewhere reachable first.
- **Joining** expects standard PCM WAV per line (the tool requests wav); if a format cannot be joined, per-line files stay in `lines/` for ffmpeg.
- **Client timeouts**: some clients cap a single tool call; split long scripts or rely on resume.
- **Consent**: clone only your own voice or one you are authorised to use; never impersonate.
- **AI-generated content**: label synthetic audio as AI-generated where you publish it, following platform rules and local law; do not use it to mislead or infringe.

## Files

```
mcp/miragea-voiceover-mcp/
├── miragea_voiceover_mcp/server.py        # the MCP server (single file, stdlib)
├── pyproject.toml              # uvx / pip entry point
├── server.json                 # official MCP Registry metadata
├── smithery.yaml               # Smithery config
├── manifest.json               # MCPB (Claude Desktop extension) manifest
├── .codebuddy-plugin/ .claude-plugin/   # WorkBuddy·CodeBuddy / Claude Code plugin
├── skills/miragea-voiceover-mcp/SKILL.md          # usage skill for agents
├── workbuddy-connector/         # WorkBuddy connector package
└── examples/                    # two-host podcast and dubbing scripts
```

---

## 中文说明

**miragea-voiceover-mcp** 是 Miragea 海外版 AI配音 MCP 服务器：文字转语音（TTS）、声音克隆、多角色对话配音（双人播客、多人视频配音，一次输出 WAV + SRT 字幕 + 逐句时间轴）、音视频字幕生成（SRT / TXT / JSON）。支持 Claude Desktop、Cursor、WorkBuddy、Cherry Studio 等任何 MCP 客户端；纯 Python 标准库，无需显卡。环境变量 `MIRAGEA_API_KEY`（在 https://miragea.ai/workspace/api 生成）。生成会消耗账号额度；声音克隆须本人授权；发布时请标注 AI 生成内容。国内用户请使用灵声妙语版 [quips-voiceover-mcp](../quips-voiceover-mcp)。

MIT License. Voiceover and subtitles are provided by the Miragea API.
