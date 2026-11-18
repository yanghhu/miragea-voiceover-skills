# Miragea AI配音 · 文字转语音 · 声音克隆 · 字幕生成 Agent Skills & MCP Servers

**AI Voiceover · Text to Speech (TTS) · Voice Cloning · Subtitle Generator — open-source Agent Skills (`SKILL.md`) powered by the official [Miragea](https://miragea.ai) API.**

开源 Agent 技能合集（SKILL.md 格式）：一份文字稿，一条命令生成 **AI配音 WAV + 带时间轴的 SRT 字幕 + 逐句时间 manifest.json**。音色用 Miragea 账号里的角色（可用本人或已获授权的 3–60 秒录音创建私有角色，即声音克隆）；已有的视频或音频也能自动识别生成 SRT / TXT / JSON 字幕。所有技能都随附 Miragea 官方客户端 `miragea_audio.py`，本地只需 Python 3.9+ 标准库，无需显卡。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 等任何能运行 Python 的 Agent。

Script in, multi-voice voiceover WAV + timed SRT subtitles + per-line timing JSON out. Use roles in your Miragea account (create a private role from your own 3–60 s recording to clone your voice), and turn existing video/audio into SRT, TXT or JSON subtitles. Every skill ships the official Miragea client (`miragea_audio.py`) and needs only the Python 3.9+ standard library — no GPU. Works with Claude Code, Codex, OpenClaw, Cursor, WorkBuddy and any agent that can run Python.

## 技能列表 · Skills

| 技能 Skill | English | 适用场景 · Use case | 路径 Path |
|---|---|---|---|
| [AI配音｜视频配音·声音克隆·字幕生成](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/miragea-video-voiceover) | AI Voiceover for Videos · Voice Cloning · Subtitles | 通用视频配音：口播稿、解说稿、小说推文、广告脚本 · General multi-voice video voiceover | `skills/miragea-video-voiceover` |
| [口播配音｜口播视频·声音克隆·AI配音](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/koubo-ai-voiceover) | Talking-Head Voiceover · Voice Cloning · Subtitles | 知识/财经/情感口播，竖屏字幕 · Talking-head videos, vertical subtitles | `skills/koubo-ai-voiceover` |
| [电影解说配音｜短剧解说·影视解说·AI配音](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/movie-recap-ai-voiceover) | Movie Recap Voiceover · Multi-Voice · Subtitles | 电影、短剧解说，旁白与角色分音色 · Movie & drama recaps | `skills/movie-recap-ai-voiceover` |
| [文字转语音｜文本转语音·语音合成·TTS](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/text-to-speech-voiceover) | Text to Speech (TTS) · Speech Synthesis | 文字或整篇文稿转语音（mp3 / wav） · Text or long documents to speech | `skills/text-to-speech-voiceover` |
| [声音克隆｜克隆声音·声音复刻·AI配音](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/voice-cloning-voiceover) | Voice Cloning Voiceover · Clone Your Voice | 用本人参考音频克隆声音配音（须本人授权） · Voiceover in your own cloned voice (consent required) | `skills/voice-cloning-voiceover` |
| [字幕生成｜视频自动加字幕·音频转字幕·SRT](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/ai-subtitle-generator) | AI Subtitle Generator · Audio/Video to SRT | 视频自动加字幕、音频转字幕/文字 · Auto subtitles & transcripts from video/audio | `skills/ai-subtitle-generator` |
| [小说推文配音｜有声书配音·多角色配音·字幕](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/novel-video-voiceover) | Novel Video & Audiobook Multi-Voice Voiceover | 小说推文、有声书、多角色朗读 · Novel videos, audiobooks, multi-voice reading | `skills/novel-video-voiceover` |
| [PPT配音｜课件配音·PPT转视频·AI旁白](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/ppt-voiceover-narration) | PPT Voiceover · Slide Narration with Subtitles | 课件/PPT逐页配音、整段旁白、每页时长、幻灯片视频 · Per-slide narration, timings, slideshow video | `skills/ppt-voiceover-narration` |
| [AI播客｜播客配音·双人对谈·节目章节](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/ai-podcast-voiceover) | AI Podcast · Solo or Two-Host Episode Voiceover | 文章转播客、双人对谈、章节时间轴和文字稿 · Article-to-podcast, two hosts, chapters & transcript | `skills/ai-podcast-voiceover` |
| [漫剧配音｜AI短剧配音·动画配音·多人配音](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/ai-drama-dubbing) | AI Comic & Short Drama Dubbing · Multi-Voice · Stems + SRT | AI漫剧、短剧、动画对白：选角表、逐句情绪、按分镜/SRT 时间码对轨、每角色分轨 · Role casting, per-line emotion, time-code locking, per-role stems | `skills/ai-drama-dubbing` |
| [视频文案提取｜视频转文字·音频转文案·改写重配音](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/video-script-extract) | Video Script Extract · Speech to Text · Rewrite and Re-voice | 视频转文字、文案提取、改写后重配音 · Video/audio to script, rewrite and re-voice | `skills/video-script-extract` |
| [AI有声书｜有声书制作·小说转有声书·分章节配音](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/ai-audiobook-maker) | AI Audiobook Maker · Novel to Audiobook · Chapter Audio | 整本小说转有声书：章节识别、逐章文件、播放列表、断点续跑 · Chapter-by-chapter audiobooks | `skills/ai-audiobook-maker` |
| [叫卖录音｜地摊叫卖·喊话录音·店铺促销广播](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/jiaomai-shout-recording) | Hawker Shout Recording · Stall Calls · Shop Announcements | 地摊叫卖、店铺促销广播，循环到指定分钟 · Looping stall calls and shop announcements | `skills/jiaomai-shout-recording` |
| [彩铃制作｜企业彩铃·IVR语音导航·电话提示音](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/ringback-ivr-prompts) | Ringback Tone Maker · IVR Phone Menu · Call Prompts | 企业彩铃、IVR 语音导航，电话格式导出 · Ringback tones and IVR prompts in phone formats | `skills/ringback-ivr-prompts` |
| [听写音频｜单词听写·英语单词朗读·词语听写](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/dictation-audio) | Dictation Audio · English Words · Chinese Words | 单词 / 词语听写：编号、重复、书写停顿、答案 · Dictation audio with numbering, repeats and pauses | `skills/dictation-audio` |
| [游戏配音｜批量配音·NPC台词语音包·游戏语音](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/game-voice-pack) | Game Voice Pack · Batch Voiceover · NPC Lines | 游戏台词 CSV → 按 id 命名的分角色语音包 · Game line CSV to per-id voice files | `skills/game-voice-pack` |
| [冥想引导｜助眠音频·睡前放松·引导语配音](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/meditation-sleep-guide) | Meditation Guide · Sleep Audio · Relaxation | 冥想 / 助眠引导语，按目标分钟数排布长停顿 · Guided meditation timed to N minutes | `skills/meditation-sleep-guide` |
| [广告配音｜宣传片配音·配音加背景音乐·AI配音](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/ad-voiceover) | Ad Voiceover · Promo Video Voice · Music Ducking | 广告、宣传片配音：按 15/30/60 秒卡时长、背景音乐自动压低、A/B 多版本 · Timed ad voiceover with music ducking | `skills/ad-voiceover` |
| [视频翻译｜双语字幕·英文配音·字幕翻译](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/skills/video-translation-dubbing) | Video Translation · Bilingual Subtitles · AI Dubbing | 视频翻译：识别字幕 → Agent 翻译对照表 → 中英双语字幕 → 按原时间码配外语 · Bilingual subtitles and AI dubbing | `skills/video-translation-dubbing` |

每个技能文件夹都包含 `SKILL.md`（完整用法、写稿方法、FAQ）、`README.md`、`examples/` 示例和 `scripts/`（技能主脚本 + `miragea_audio.py` 官方客户端）；新技能还带 `assets/` 封面和流程图。

Each folder contains `SKILL.md` (full usage, scripting guide, FAQ), `README.md`, an example script under `examples/`, and `scripts/` (`voiceover.py` + the official `miragea_audio.py` client).

## 安装 · Install

```bash
npx skills add yanghhu/miragea-voiceover-skills
```

或者把 `skills/` 下任意文件夹复制到 Agent 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`）。

Or copy any folder under `skills/` into your agent's skills directory (e.g. `~/.claude/skills/`, `~/.codex/skills/`).

```bash
git clone https://github.com/yanghhu/miragea-voiceover-skills.git
cp -r miragea-voiceover-skills/skills/koubo-ai-voiceover ~/.claude/skills/
```

## API Key

在 Miragea 工作台生成 API Key：<https://miragea.ai/workspace/api>，然后设置环境变量 `MIRAGEA_API_KEY`。没有 Key 时可以先加 `--dry-run` 离线试跑（生成静音占位音频，不调用接口）。

Create an API key at <https://miragea.ai/workspace/api> and export it as `MIRAGEA_API_KEY`. Without a key, add `--dry-run` to try everything offline (silent placeholder audio, no API call).

```bash
export MIRAGEA_API_KEY=your_key
```

## 快速开始 · Quick start

```bash
cd skills/miragea-video-voiceover

# 离线检查环境 · offline environment check
python3 scripts/voiceover.py check

# 离线试跑，无需 Key · offline dry run, no key needed
python3 scripts/voiceover.py script examples/movie-recap.md -o out --preset jieshuo --dry-run

# 正式生成：out/voiceover.wav + voiceover.srt + manifest.json
python3 scripts/voiceover.py script examples/movie-recap.md -o out --preset jieshuo

# 查看账号已有角色 · list saved voices in your account
python3 scripts/miragea_audio.py actors --limit 20

# 文字转语音单句 · single-line text to speech
python3 scripts/miragea_audio.py generate --text '你好，欢迎回来。' --actor-id ACTOR_ID --wait --output hello.mp3

# 视频自动加字幕 · video to SRT subtitles
python3 scripts/miragea_audio.py recognize --file video.mp4 --wait --output video.srt
```

生成模式、语气标签、单句字数上限和计费以 `python3 scripts/miragea_audio.py capabilities` 的实时返回为准。

Generation modes, emotion tags, per-line limits and billing are whatever `python3 scripts/miragea_audio.py capabilities` returns live.

## MCP 服务器 · MCP Servers（AI配音 MCP / 文字转语音 MCP / 播客生成 MCP / 字幕生成 MCP）

除了技能，本仓库还提供两个 **MCP 服务器**（Model Context Protocol，stdio，Python 3.9+ 标准库）：在 Claude Desktop、Cursor、WorkBuddy、Cherry Studio 等任何 MCP 客户端里直接调用 **文字转语音、声音克隆、多角色对话配音（双人播客 / 多人视频配音，一次输出 WAV + SRT + 逐句时间轴）和音视频字幕生成**。

Besides the skills, the repo ships two **MCP servers** (stdio, Python 3.9+ stdlib) for any MCP client: text to speech, voice cloning, multi-speaker dialogue voiceover (two-host podcast generator, multi-character dubbing → WAV + SRT + per-line timings) and audio/video to SRT subtitles.

| MCP 服务器 | 服务 | 环境变量 | 文档 |
|---|---|---|---|
| [quips-voiceover-mcp](mcp/quips-voiceover-mcp) | 灵声妙语 Quips（国内） | `QUIPS_API_KEY` | 中文 |
| [miragea-voiceover-mcp](mcp/miragea-voiceover-mcp) | Miragea（海外） | `MIRAGEA_API_KEY` | English |

工具 Tools：`get_capabilities` · `list_voices` · `text_to_speech` · `dialogue_voiceover` · `generate_subtitles` · `get_task`；提示词 Prompts：`two_host_podcast` · `multi_character_dubbing`。

```json
{
  "mcpServers": {
    "miragea-voiceover": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/yanghhu/miragea-voiceover-skills#subdirectory=mcp/miragea-voiceover-mcp", "miragea-voiceover-mcp"],
      "env": { "MIRAGEA_API_KEY": "your-api-key" }
    }
  }
}
```

- 国内版把 `miragea` 换成 `quips`、环境变量换成 `QUIPS_API_KEY`。离线试跑：`python3 mcp/<名称>/<包名>/server.py --self-test`（无需 Key，不联网）。
- Claude Desktop 扩展包（`.mcpb`）在 `mcp/dist/`；WorkBuddy / CodeBuddy / Claude Code 可把本仓库添加为插件市场：`/plugin marketplace add yanghhu/miragea-voiceover-skills`，安装 `quips-voiceover-mcp` 或 `miragea-voiceover-mcp` 插件。
- WorkBuddy 手动配置：写入 `~/.workbuddy/mcp.json`（格式同上），在连接器管理里点“信任”。

## 合规 · Responsible use

声音克隆只能使用本人或已获得明确授权的声音。请遵守所在平台关于 AI 生成内容的标注要求。

Only clone voices you own or have explicit permission to use, and follow your platform's rules on labeling AI-generated content.

## 链接 · Links

- Miragea: <https://miragea.ai>
- API Key: <https://miragea.ai/workspace/api>
- `llms.txt`: [llms.txt](llms.txt)

## License

MIT © 2026 Miragea
