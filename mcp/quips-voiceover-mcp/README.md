# AI配音 MCP｜文字转语音 MCP · 播客生成 MCP · 字幕生成 MCP（灵声妙语 Quips）

**quips-voiceover-mcp** 是一个开源的 MCP 服务器（Model Context Protocol，stdio），把灵声妙语（Quips）官方开放 API（https://www.quips.cn）的 **AI配音、文字转语音（TTS）、声音克隆、多角色对话配音（双人播客 / 多人视频配音）和字幕生成** 变成 Claude Desktop、Cursor、WorkBuddy、Cherry Studio 等 AI 客户端可直接调用的工具。一份对话稿进去，出来的是整段 **WAV 音频 + 带时间轴的 SRT 字幕 + 逐句时间轴 manifest.json**；已有的音频或视频也能识别成 SRT / TXT / JSON 字幕。纯 Python 3.9+ 标准库实现，无需显卡，无第三方依赖。

> English: Quips AI Voiceover MCP server — text to speech, two-host podcast generator, multi-speaker dialogue dubbing to WAV + SRT, and audio/video to SRT subtitles, via the official Quips (灵声妙语) API. Python standard library only. See the [English section](#english).

- 服务：灵声妙语（Quips），https://www.quips.cn（API Key 在 https://www.quips.cn/workspace/api 生成）
- 版本：1.0.0 · 许可证：MIT · 仓库：[yanghhu/miragea-voiceover-skills](https://github.com/yanghhu/miragea-voiceover-skills/tree/main/mcp/quips-voiceover-mcp)
- 关键词：AI配音 MCP、文字转语音 MCP、TTS MCP、播客生成 MCP、AI播客、双人播客、多角色配音、多人视频配音、对话配音、字幕生成 MCP、SRT 字幕、音频转字幕、声音克隆、MCP Server

## 目录
- [能做什么](#能做什么) · [适用人群与场景](#适用人群与场景) · [快速开始](#快速开始) · [客户端配置示例](#客户端配置示例)
- [工具说明](#工具说明) · [对话稿格式](#对话稿格式双人播客--多人配音) · [输入与输出](#输入与输出) · [离线试跑](#离线试跑无需-key)
- [常见问题 FAQ](#常见问题-faq) · [与同类做法的区别](#与同类做法的区别) · [限制与注意事项](#限制与注意事项) · [English](#english)

## 能做什么

1. **文字转语音 / AI配音**：一段文字 → mp3 / wav / flac / opus / aac / pcm；音色用账号已有角色（`actor_id`），或用一段参考音频做声音克隆（`reference_audio_url` + `reference_text`）；可调语速 0.25–4 倍，可加所选模式提供的语气标签。
2. **长文配音 + 字幕**：`text_to_speech` 打开 `subtitles=true`，长文自动分句、逐句生成、拼成一条 WAV，同时写出 SRT 字幕和逐句时间轴。
3. **双人播客 / AI播客生成**：两位主持人的对话稿 → 整期播客 WAV + 带说话人的 SRT 字幕。
4. **多角色对话配音 / 多人视频配音**：旁白、角色 A、角色 B……每个角色一个音色，一次调用出整段配音和字幕，可用于短剧、动画、小说推文、有声书多角色朗读。
5. **字幕生成**：本地音频或视频 → SRT 字幕 / TXT 文字稿 / JSON 分段（视频自动加字幕、音频转字幕、音频转文字）。
6. **断点续跑**：多句配音逐句缓存；超时或中断后用相同参数再调用，只补没完成的句子；改一句只重配一句。

## 适用人群与场景

| 人群 | 典型场景 |
|---|---|
| 播客主、公众号/知识博主 | 文章改写成双人对谈稿后直接出整期音频和字幕；做“音频版” |
| 短视频创作者 | 口播、解说、小说推文、短剧对白的多角色配音，SRT 直接导入剪辑软件 |
| 课程与培训 | 讲稿配音、课件旁白，多讲师对话式课程 |
| 产品与市场 | 产品演示、宣传片旁白，多语言稿件分别配音（翻译由你的 AI 客户端完成） |
| 开发者 / Agent 搭建者 | 在 MCP 客户端或自建 Agent 里把“写稿 → 配音 → 字幕”串成一条工作流 |
| 剪辑与字幕组 | 已有视频、采访、会议录音批量识别 SRT / TXT |

## 快速开始

1. 在 https://www.quips.cn/workspace/api 生成 API Key。
2. 准备 Python 3.9+（`python3 --version`）。可选安装 [uv](https://docs.astral.sh/uv/) 以便用 `uvx` 一行运行。
3. 把下方任一配置写进你的 MCP 客户端，把 `your-api-key` 换成你的 Key，重启客户端。
4. 对 AI 说：“列出我能用的音色”，再说“把 examples/two-host-podcast.md 做成双人播客”。

不想装 uv：`git clone https://github.com/yanghhu/miragea-voiceover-skills.git`，然后用 `python3 mcp/quips-voiceover-mcp/quips_voiceover_mcp/server.py` 作为启动命令（见下方 “直接用 Python 运行”）。

## 客户端配置示例

### Claude Desktop（`claude_desktop_config.json`）
用 uvx 从 GitHub 运行（无需 PyPI，自动拉取本目录）：
```json
{
  "mcpServers": {
    "quips-voiceover": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yanghhu/miragea-voiceover-skills#subdirectory=mcp/quips-voiceover-mcp",
        "quips-voiceover-mcp"
      ],
      "env": {
        "QUIPS_API_KEY": "your-api-key"
      }
    }
  }
}
```
也可以下载 Releases 里的 `quips-voiceover-mcp-1.0.0.mcpb` 包双击安装（Claude Desktop 扩展，会提示填写 API Key）。

### Cursor（`~/.cursor/mcp.json` 或项目 `.cursor/mcp.json`）
```json
{
  "mcpServers": {
    "quips-voiceover": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yanghhu/miragea-voiceover-skills#subdirectory=mcp/quips-voiceover-mcp",
        "quips-voiceover-mcp"
      ],
      "env": {
        "QUIPS_API_KEY": "your-api-key"
      }
    }
  }
}
```

### WorkBuddy（`~/.workbuddy/mcp.json`，或 侧边栏 插件 → MCP 服务器 → 配置 MCP）
```json
{
  "mcpServers": {
    "quips-voiceover": {
      "type": "stdio",
      "command": "python3",
      "args": [
        "/absolute/path/miragea-voiceover-skills/mcp/quips-voiceover-mcp/quips_voiceover_mcp/server.py"
      ],
      "env": {
        "QUIPS_API_KEY": "your-api-key"
      }
    }
  }
}
```
保存后在连接器 / MCP 管理里点“信任”启用。WorkBuddy、CodeBuddy 用户也可以把本仓库添加为插件市场：`/plugin marketplace add yanghhu/miragea-voiceover-skills`，然后安装插件 `quips-voiceover-mcp`（插件自带 MCP 配置和使用技能）。

### Cherry Studio（设置 → MCP 服务器 → 添加 → 从 JSON 导入）
```json
{
  "mcpServers": {
    "quips-voiceover": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yanghhu/miragea-voiceover-skills#subdirectory=mcp/quips-voiceover-mcp",
        "quips-voiceover-mcp"
      ],
      "env": {
        "QUIPS_API_KEY": "your-api-key"
      }
    }
  }
}
```
类型选 STDIO；若用 Python 直接运行，命令填 `python3`，参数填 server.py 的绝对路径，环境变量填 `QUIPS_API_KEY=你的Key`。

### 直接用 Python 运行（任何支持 stdio 的客户端：Cline、Windsurf、Continue、Claude Code 等）
```json
{
  "mcpServers": {
    "quips-voiceover": {
      "command": "python3",
      "args": [
        "/absolute/path/miragea-voiceover-skills/mcp/quips-voiceover-mcp/quips_voiceover_mcp/server.py"
      ],
      "env": {
        "QUIPS_API_KEY": "your-api-key"
      }
    }
  }
}
```
Windows 上 `command` 用 `python` 或 `py`，路径用 `C:\\...\\server.py`。

可选环境变量：`QUIPS_OUTPUT_DIR`（输出目录，默认 `~/quips-voiceover`）、`QUIPS_BASE_URL`（服务地址，默认 `https://www.quips.cn`，接口路径自动拼 `/v1/...`）、`QUIPS_DRY_RUN=1`（离线试跑）。兼容旧技能的 `MIRAGEA_API_KEY`（未设置 `QUIPS_API_KEY` 时读取）。

## 工具说明

| 工具 | 作用 | 主要输入 | 输出 |
|---|---|---|---|
| `get_capabilities` | 查询可用合成模式、语气标签、音频格式、语速范围、单次字数上限、字幕限额与当前费率 | 无 | 实时能力 JSON |
| `list_voices` | 列出账号里的配音角色/音色（含已复刻的声音） | `limit` 1–100、`offset` | `actor_id`、`name`、`language` 列表 |
| `text_to_speech` | 文字转语音 / AI配音 | `text`；`actor_id` 或 `reference_audio_url`(+`reference_text`)；可选 `model`、`format`、`speed`、`tags`、`subtitles` | 音频文件路径；`subtitles=true` 时为 WAV + SRT + manifest |
| `dialogue_voiceover` | 多角色对话配音 / 双人播客生成 | `script`（对话稿）或 `lines`；`speakers`（角色→音色）；`style` podcast/dubbing/audiobook | `voiceover.wav` + `voiceover.srt` + `voiceover.manifest.json` |
| `generate_subtitles` | 字幕生成：音视频转 SRT / TXT / JSON | `file_path`、`format` | 字幕文件路径 + 语言、分段数、预览 |
| `get_task` | 查询或继续等待任务，保存结果 | `task_id`、`wait`、`output_path` | 任务 JSON（含保存路径） |

另带两个提示词模板（prompts）：`two_host_podcast`（按主题写双人播客稿）和 `multi_character_dubbing`（把对白/故事整理成多角色配音稿）。

调用建议：先 `get_capabilities` + `list_voices`；生成类工具会消耗账号额度，调用前让 AI 把稿子和音色给你确认一遍。

## 对话稿格式（双人播客 / 多人配音）

```markdown
---
主持人A: actor_id=替换为你的角色ID
主持人B: actor_id=替换为另一个角色ID
---
# 开场
[主持人A] 欢迎收听本期节目，今天我们聊一个很多人都在问的话题：怎么用 AI 做播客。
[主持人B] 对，我先说结论：稿子写好，配音和字幕其实可以一步出来。
[pause 0.8]
# 第一部分：写稿
[主持人A] 那稿子要怎么写才适合听？
[主持人B] 句子短一点，多用口语，一个人别连着说太久，两个人有来有回。
[pause 0.8]
# 结尾
[主持人A] 好，今天就聊到这里，我们下期见。
[主持人B] 下期见！
```

- 开头 `---` 之间是角色表（可选）：`角色名: actor_id=...`，或 `ref=参考音频URL ref_text="参考音频原文"`，还可加 `speed=1.1`、`model=...`、`tags=标签1,标签2`、`language=zh`。
- 正文每行一句：`[角色名] 台词`；已在角色表里的角色也可写成 `角色名：台词`。没有标记的行沿用上一个角色。
- `[pause 0.8]`（或 `[停顿 0.8]`）插入 0.8 秒静音；`#` 开头的行是注释，不会读出。
- 也可以不写角色表，改用工具参数 `speakers`：`{"主持人A": {"actor_id": "..."}, "主持人B": {"reference_audio_url": "https://...", "reference_text": "..."}}`。
- 更多示例：[examples/two-host-podcast.md](examples/two-host-podcast.md)、[examples/multi-character-dubbing.md](examples/multi-character-dubbing.md)。

`style` 预设：`podcast`（句间 0.35 秒、字幕带说话人）、`dubbing`（句间 0.15 秒、字幕不带说话人，便于对画面）、`audiobook`（句间 0.5 秒）。`gap`、`max_chars`、`speaker_labels` 可单独覆盖。

## 输入与输出

| 工具 | 输出位置 | 文件 |
|---|---|---|
| `dialogue_voiceover` | `output_dir`，默认 `~/quips-voiceover/<时间>-<标题>/` | `voiceover.wav`、`voiceover.srt`、`voiceover.manifest.json`（每句说话人、文本、起止秒）、`lines/`（每句缓存） |
| `text_to_speech` | `output_path`，默认 `~/quips-voiceover/speech-<时间>-<开头文字>.<格式>` | 音频文件；`subtitles=true` 时同 dialogue_voiceover |
| `generate_subtitles` | `output_path`，默认与媒体文件同目录同名 | `.srt` / `.txt` / `.json` |

所有写文件操作都不覆盖已有文件（重名自动加 `-2`）。工具返回 JSON，包含文件绝对路径、时长、任务 ID 和幂等键。

## 离线试跑（无需 Key）

```bash
git clone https://github.com/yanghhu/miragea-voiceover-skills.git && cd miragea-voiceover-skills/mcp/quips-voiceover-mcp
python3 quips_voiceover_mcp/server.py --self-test      # 生成静音占位 WAV + SRT，打印输出路径
python3 quips_voiceover_mcp/server.py --dry-run        # 以离线模式启动 MCP 服务器，可在客户端里走通全流程
```
离线模式不联网、不调用接口、不消耗额度，音频是静音占位，用来检查稿件格式、字幕切分和时间轴。

## 常见问题 FAQ

**问：quips-voiceover-mcp 是什么？**
答：一个 MCP 服务器。装进 Claude Desktop、Cursor、WorkBuddy、Cherry Studio 等客户端后，AI 可以直接调用 灵声妙语（Quips） 的配音和字幕接口：文字转语音、声音克隆、多角色对话配音（双人播客、多人视频配音）、音视频转 SRT 字幕。

**问：能用它生成双人播客吗？**
答：能。把两位主持人的对话写成 `[主持人A] ...` / `[主持人B] ...`，调用 `dialogue_voiceover`（style=podcast），每位主持人用各自的音色，输出整期 WAV 和带说话人的 SRT。没有稿子时，可以先用提示词模板 `two_host_podcast` 让 AI 按主题写稿。

**问：多人视频配音 / 多角色配音最多支持几个角色？**
答：工具本身不限制角色数，每个角色需要一个音色（`actor_id` 或参考音频）。每一句是一次生成请求，单句字数上限以 `get_capabilities` 返回的 `audio.max_text_length` 为准。

**问：怎么用自己的声音（声音克隆）？**
答：两种方式：在 灵声妙语（Quips） 账号里已有的角色直接用 `actor_id`；或者提供一段服务端可以访问的公网参考音频 URL（`reference_audio_url`）和音频里实际说的文字（`reference_text`）。只能克隆你本人或已获授权的声音。

**问：输出的 SRT 字幕能导入剪辑软件吗？**
答：输出是标准 SRT（序号、`00:00:01,000 --> 00:00:03,000` 时间轴、文本），可以在支持 SRT 导入的剪辑软件里使用。时间轴按每句实际音频时长计算，长句按标点切成多条字幕。

**问：没有 API Key 可以先试吗？**
答：可以。用 `--dry-run` 启动或在工具参数里传 `dry_run: true`，会生成静音占位音频和真实格式的字幕、时间轴，不联网、不消耗额度。

**问：对话很长，客户端超时了怎么办？**
答：已完成的句子都缓存在输出目录的 `lines/` 里。用同样的参数（同一个 `output_dir`）再调用一次，会跳过已完成的句子继续生成。单个任务等待超时会返回 `task_id`，用 `get_task` 继续取结果，不要重新提交。服务器在客户端提供 progressToken 时会发送进度通知。

**问：怎么收费？**
答：配音和字幕识别都按 灵声妙语（Quips） 账号的额度计费，具体规则以 `get_capabilities` 实时返回和官网为准。本项目只是调用官方 API 的开源客户端，不另外收费。

**问：我的文字和文件会发到哪里？**
答：只发到 灵声妙语（Quips） 官方 API（默认 `https://www.quips.cn`）。API Key 只从环境变量读取，不写入文件或日志；生成的音频和字幕保存在你本机。

**问：支持选择输出语言或翻译吗？**
答：接口没有“输出语言”参数，读出的语言就是你给的文字的语言。需要外语配音时，先让 AI 客户端翻译稿子，再交给本工具配音。`language` 参数只是参考音频的语言提示。

**问：和同仓库的“AI配音技能（SKILL.md）”有什么区别？**
答：技能是给能运行 Python 脚本的 Agent 用的工作流说明 + 脚本；MCP 服务器是标准工具接口，任何 MCP 客户端都能直接调用，不需要 Agent 自己跑命令。两者调用的是同一套官方接口，按你用的客户端选择。

## 与同类做法的区别

| 对比项 | 本 MCP 服务器 | 一般 TTS MCP / 文字转语音工具 | 手工配音 + 手打字幕 |
|---|---|---|---|
| 多角色 / 双人播客 | 一份稿子多个音色，一次出整段 | 多为一次一段、一个音色，需要自己拼接 | 逐个录制再剪辑 |
| 字幕 | 同时输出按真实时长对齐的 SRT | 通常只有音频 | 另外听写、对轴 |
| 时间轴 | 每句起止秒 manifest.json，方便对画面 | 无 | 手工标记 |
| 改稿 | 改一句只重配一句（逐句缓存） | 整段重生成 | 重新录制 |
| 音视频转字幕 | 同一服务器内 `generate_subtitles` | 需要另一个工具 | 手工听写 |
| 依赖 | Python 3.9+ 标准库，无显卡 | 视实现而定 | 录音设备、剪辑软件 |

## 限制与注意事项

- **额度**：生成和识别会消耗 灵声妙语（Quips） 账号额度；单次字数上限、可用模式、标签、字幕文件大小与时长上限都以 `get_capabilities` 实时返回为准。
- **参考音频**：`reference_audio_url` 必须是服务端能直接访问的 http(s) 地址；本地文件需要先上传到可访问的位置。
- **拼接格式**：多句拼接要求接口返回标准 PCM WAV（工具内部固定用 wav 生成每句）；若遇到无法拼接的格式，每句文件保留在 `lines/`，可用 ffmpeg 自行合并。
- **客户端超时**：部分客户端单次工具调用有超时，长稿可分段调用或依赖断点续跑。
- **声音授权**：只克隆你本人或已获得明确授权的声音，不得冒充他人。
- **AI 生成内容标识**：生成的音频属于 AI 合成内容。发布到平台时请按平台规则和相关法规（如《人工智能生成合成内容标识办法》）添加 AI 生成标识，不要用于误导、诈骗或侵权。
- **服务地址**：默认 `https://www.quips.cn`；私有部署可设置 `QUIPS_BASE_URL`。

## 文件结构

```
mcp/quips-voiceover-mcp/
├── quips_voiceover_mcp/server.py        # MCP 服务器（单文件，标准库）
├── pyproject.toml              # uvx / pip 安装入口
├── server.json                 # 官方 MCP Registry 元数据
├── smithery.yaml               # Smithery 配置
├── manifest.json               # MCPB（Claude Desktop 扩展）清单
├── .codebuddy-plugin/ .claude-plugin/   # WorkBuddy·CodeBuddy / Claude Code 插件
├── skills/quips-voiceover-mcp/SKILL.md          # 给 Agent 的使用技能
├── workbuddy-connector/         # WorkBuddy 连接器包（connector-meta.json、mcp.json、token-schema.json）
└── examples/                    # 双人播客、多角色配音示例稿
```

---

## English

**quips-voiceover-mcp** is an open-source MCP server (stdio) for the official Quips (灵声妙语) API (https://www.quips.cn): **AI voiceover, text to speech, voice cloning, multi-speaker dialogue voiceover (two-host podcast generator, multi-character dubbing) and subtitle generation** for Claude Desktop, Cursor, WorkBuddy, Cherry Studio and any MCP client. A dialogue script goes in; a joined **WAV + timed SRT subtitles + per-line timing JSON** come out. Existing audio/video can be turned into SRT / TXT / JSON subtitles. Python 3.9+ standard library only, no GPU.

Tools: `get_capabilities`, `list_voices`, `text_to_speech`, `dialogue_voiceover`, `generate_subtitles`, `get_task`; prompts `two_host_podcast`, `multi_character_dubbing`. Env: `QUIPS_API_KEY` (required), `QUIPS_OUTPUT_DIR`, `QUIPS_BASE_URL`, `QUIPS_DRY_RUN`. Offline test: `python3 quips_voiceover_mcp/server.py --self-test`.

```json
{
  "mcpServers": {
    "quips-voiceover": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yanghhu/miragea-voiceover-skills#subdirectory=mcp/quips-voiceover-mcp",
        "quips-voiceover-mcp"
      ],
      "env": {
        "QUIPS_API_KEY": "your-api-key"
      }
    }
  }
}
```

Generation uses account credits (limits come from `get_capabilities`). Clone a voice only with the speaker's consent, and label AI-generated audio where you publish it.

许可证 MIT。配音与字幕能力由 灵声妙语（Quips） 开放 API 提供。
