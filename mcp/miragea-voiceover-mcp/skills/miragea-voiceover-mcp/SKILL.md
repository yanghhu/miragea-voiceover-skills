---
name: miragea-voiceover-mcp
description: How to use the miragea-voiceover-mcp MCP tools for text to speech, two-host podcast and multi-speaker dialogue voiceover (WAV+SRT+timings) and audio/video subtitles, including picking voices, script format, resuming and confirming credit use.
version: "1.0.0"
author: Miragea
---

# Miragea AI Voiceover MCP (Text to Speech, Podcast Generator, Subtitles) usage guide

Tools come from the MCP server `miragea-voiceover-mcp` (official Miragea API). Generation tools use account credits.

## Steps
1. `get_capabilities`: check modes (model), tone tags and the per-request text limit.
2. `list_voices`: find each speaker's `actor_id` by name; ask the user when names clash. For the user's own voice, ask for a publicly reachable reference clip URL plus its exact words, and confirm consent.
3. Script: one line per utterance `[Name] text`, `[pause 0.8]` between chapters; the `two_host_podcast` / `multi_character_dubbing` prompts help.
4. Confirm the script and the speaker-to-voice mapping with the user before generating.
5. Call `text_to_speech` for a single text (`subtitles: true` for long-form), `dialogue_voiceover` for scripts (style: podcast / dubbing / audiobook), `generate_subtitles` for audio/video.
6. Report the absolute paths of `audio_wav`, `subtitles_srt`, `manifest_json` and the duration; remind the user to label AI-generated audio when publishing.

## Errors
- `missing_api_key`: ask the user to set `MIRAGEA_API_KEY`, or try offline with `dry_run: true`.
- `speaker_without_voice`: add an `actor_id` or reference clip for that speaker.
- `wait_timeout` / client timeout: call `dialogue_voiceover` again with the same arguments to resume; use `get_task` for a single task, never resubmit.
- 400 fix input (length, tags, speed); 401 check the key; 403 check API access; 429 wait or add credits.
