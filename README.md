# Miragea Voiceover Skills · AI 视频配音技能合集

Open-source Agent Skills (`SKILL.md`) that turn a script into **AI voiceover (WAV) + timed SRT subtitles** in one command. Works with Claude Code, Codex, OpenClaw, Cursor, WorkBuddy and any agent that can run Python. Voice generation is powered by the [Miragea](https://miragea.ai) API — 5–10 s voice cloning, 10 languages, no local GPU.

开源 Agent 技能合集：一份文字稿，一条命令生成 **AI 配音 WAV + 带时间轴 SRT 字幕**。支持 5–10 秒声音克隆、中英日韩德法俄葡西意 10 种语言，本地无需显卡，仅需 Python 3.9+ 标准库。

| Skill | 场景 | Use case |
|---|---|---|
| [视频配音神器](skills/miragea-video-voiceover) | 通用视频配音与字幕 | General video voiceover & subtitles |
| [口播配音神器](skills/koubo-ai-voiceover) | 知识/财经/情感口播 | Talking-head videos |
| [电影解说配音](skills/movie-recap-ai-voiceover) | 电影、短剧解说，多角色 | Movie & drama recaps |
| [带货视频配音](skills/daihuo-ai-voiceover) | 抖音/快手/TikTok 带货 | E-commerce product videos |
| [数字人配音](skills/shuziren-ai-voiceover) | 数字人驱动音频 + 时间轴 | Digital human / AI avatar audio |
| [广告片配音](skills/guanggao-ai-voiceover) | 广告片、宣传片、产品视频 | Ads, promo & demo videos |
| [有声书配音](skills/youshengshu-ai-voiceover) | 小说多角色朗读、广播剧 | Audiobooks & audio dramas |

## Install

```bash
npx skills add yanghhu/miragea-voiceover-skills
```

Or copy any folder under `skills/` into your agent's skills directory (e.g. `~/.claude/skills/`).

## Quick start

```bash
export MIRAGEA_API_KEY=your_key            # create at https://miragea.ai/workspace/api
python3 skills/koubo-ai-voiceover/scripts/voiceover.py script skills/koubo-ai-voiceover/examples/example.md -o out --preset koubo
# try offline first, no key needed:
python3 skills/koubo-ai-voiceover/scripts/voiceover.py script skills/koubo-ai-voiceover/examples/example.md -o out --preset koubo --dry-run
```

Outputs `out/voiceover.wav`, `out/voiceover.srt`, `out/manifest.json` — drop them into CapCut/剪映, Premiere or ffmpeg.

## Responsible use · 合规

Only clone your own voice or voices you are authorized to use. Label AI-generated content per platform rules. 只克隆本人或已授权的声音，按平台规则标注 AI 生成内容。

MIT License. Built by the Miragea team.
