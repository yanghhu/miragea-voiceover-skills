---
name: "video-script-extract"
description: "视频文案提取、视频转文字、音频转文案技能：把本地视频或音频文件交给它，调用 Miragea 开放 API 的语音识别，提取口播文案，输出 transcript.txt 文字稿、带时间轴的 transcript.srt 字幕，并生成按句拆好的改写表 rewrite.md；你（或 Agent）把每句改写成自己的原创文案后，用你自己克隆或授权的音色一键重新配音，得到新的配音 WAV 和 SRT 字幕。适用于整理自己的口播稿、课程和访谈录音、会议纪要初稿、素材复盘与二次创作；只处理本地文件，不抓取链接，不照搬他人文案。需要 API Key，本地只需 Python 3.9+ 标准库、无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。Video script extraction, speech to text, audio to transcript, SRT subtitles, rewrite and re-voice."
version: "1.1.0"
display_name: "视频文案提取｜视频转文字·音频转文案·改写重配音"
display_name_en: "Video Script Extract · Speech to Text · Rewrite and Re-voice"
description_zh: "视频文案提取：上传本地视频或音频，自动识别语音提取口播文案，导出TXT文字稿和带时间轴SRT字幕；改写成自己的原创文案后，用声音克隆一键重新配音，适合口播、课程、访谈整理，无需显卡。"
description_en: "Extract the spoken script from a local video or audio file as a TXT transcript and timed SRT subtitles, rewrite it in your own words, then re-voice it with your own cloned voice. For talking-head videos, courses and interviews. No GPU."
metadata:
  version: "1.1.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["视频文案提取", "视频转文字", "音频转文字", "音频转文案", "口播文案提取", "语音识别", "字幕提取", "文字稿", "视频文案改写", "改写重配音", "声音克隆", "AI配音", "SRT字幕", "课程整理", "访谈整理", "会议记录", "video script extraction", "video to text", "speech to text", "audio transcript", "SRT", "voice cloning"]
---

# 视频文案提取

「视频文案提取」是一个把本地视频或音频里的口播变成可编辑文稿的 Agent 技能：识别语音，输出 TXT 文字稿、SRT 字幕和按句拆好的改写表；你改写成原创文案后，再用自己克隆的音色重新配音，本地无需显卡。

## 一句话定义

视频文案提取 = 本地视频 / 音频 → `video_copy.py extract` 识别语音 → `transcript.txt`（文字稿）+ `transcript.srt`（时间轴字幕）+ `rewrite.md`（按句拆好的改写表）→ 你把每句改成自己的原创表达 → `video_copy.py revoice rewrite.md` 用自己克隆的音色重新配音 → `voiceover.wav` + `voiceover.srt`。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 口播博主 | 自己拍的口播视频只剩成片，想把口播稿还原出来改版、做系列或换一种说法重发 |
| 课程 / 培训讲师 | 录好的讲课音频整理成文字讲义，再把讲稿修订后重新配音 |
| 采访 / 播客作者 | 访谈录音转文字稿，摘出金句和要点 |
| 会议组织者 | 会议录音转成文字，作为纪要初稿再人工整理 |
| 短视频运营 | 复盘自己账号里表现好的视频，提取文案结构，写出新选题的原创脚本 |
| 字幕制作 | 已有视频只缺字幕，直接要 SRT |

本技能只处理你本人拥有或已获授权的本地音视频文件，不抓取平台链接，不照搬他人文案。和本系列其他技能的分工：字幕生成只管识别出 SRT；AI配音只管文稿转语音；**视频文案提取把两头接起来**：识别 → 按句改写表 → 重新配音。

## 能力一览

| 项目 | 说明 |
|---|---|
| 输入 | 本地视频或音频文件（`recognize` 接口接受的格式、大小以 `capabilities` 实时返回为准） |
| 识别 | 调用客户端 `recognize`，分别取 `srt` 和 `txt` 两种结果 |
| 输出 | `transcript.txt`、`transcript.srt`、`rewrite.md` |
| 改写表 | 文字稿按句拆开，每句原文放在 HTML 注释里，下面一行 `[主播] ` 留给你写改写后的句子 |
| 重新配音 | `revoice` 把填好的 `rewrite.md` 交给 `scripts/voiceover.py`，用账号角色（`voice=角色名称` 或 `actor_id`）逐句配音，拼成 `voiceover.wav` 并输出 `voiceover.srt`、`manifest.json` |
| 本地依赖 | Python 3.9+ 标准库，无需显卡；`--dry-run` 用内置示例文稿，不需要 Key、不调用接口 |

## 快速开始

识别和配音都调用 Miragea 开放 API，需要一个 API Key（https://miragea.ai/workspace/api 生成，只放环境变量，不要贴进聊天）。重新配音还需要你在 https://miragea.ai 用本人录音克隆好的音色。

```bash
python3 scripts/video_copy.py selftest                         # 离线自检
python3 scripts/video_copy.py extract -o out --dry-run         # 不用 Key，用示例文稿跑通流程

export MIRAGEA_API_KEY=你的key
python3 scripts/video_copy.py extract 我的口播.mp4 -o out      # 提取文案
python3 scripts/miragea_audio.py actors --limit 50             # 找到自己克隆的角色名称
python3 scripts/miragea_audio.py create-actor --file 我的录音.wav --name 我的声音 --language zh   # 还没有角色：用本人或已获授权的录音创建私有角色（按账号规则计费）
# 编辑 out/rewrite.md：把每句改写成自己的原创表达
python3 scripts/video_copy.py revoice out/rewrite.md -o out_voice --voice 我的声音
```

Default API root is `https://miragea.ai/v1`; set `MIRAGEA_BASE_URL` (including `/v1`) only for a private deployment.

- 接口只按账号里的角色配音（官方客户端 1.3.0）：稿件里给每个角色写 `voice=角色名称` 或 `actor_id=角色ID`，也可以命令行加 `--voice 角色名称` 统一指定。旧版用音频链接直接克隆的写法服务端已停用，旧稿件改成角色写法即可。

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “把这个视频的口播提取成文字” | `extract 视频文件`，把 `transcript.txt` 给你 |
| “要字幕” | 直接给 `transcript.srt` |
| “照这个思路写一篇新的，别和原文一样” | 读取文字稿，由 Agent 另行原创写作，写进 `rewrite.md` 的 `[主播]` 行 |
| “用我的声音重新配” | `actors` 查角色名称 → `revoice rewrite.md --voice 角色名称`（或写进 `rewrite.md` 头部） |
| “先别调用接口” | 加 `--dry-run` |

## 工作流建议

1. 先 `extract`，通读 `transcript.txt`，识别错字（人名、专有名词）人工校对一遍。
2. 改写不是换几个词：保留你想沿用的信息点，用自己的结构、例子和口吻重写；他人的视频只作为参考，不要复述其原文。
3. 每句尽量短、口语化，一行一句，便于配音和字幕。
4. 先给一两句单句试听音色，再整篇 `revoice`。
5. 成片按平台要求标注 AI 生成内容。

## --dry-run 示例输出

```text
$ python3 scripts/video_copy.py extract -o out --dry-run
wrote out/transcript.txt, transcript.srt, rewrite.md (5 sentences)  [dry-run: sample transcript, no API call]
```

## 示例改写表（examples/rewrite_example.md）

```markdown
---
# 主播的音色：账号里的角色名称（miragea_audio.py actors 查），也可写 actor_id=角色ID
主播: voice=我的声音
---
# 原文1: 大家好，今天讲三个提升睡眠质量的小习惯。
[主播] 睡不好的朋友看过来，三个小习惯帮你把觉睡踏实。
# 原文2: 第一，睡前一小时放下手机。
[主播] 先从睡前一小时不看手机开始。
# 原文3: 第二，固定每天起床的时间。
[主播] 再把起床时间固定下来，周末也别例外。
```

同目录还有 `examples/sample_transcript.txt`，是 dry-run 使用的示例文稿。

## 和常见做法的区别

| 对比项 | 手动听写 | 只做语音转文字的工具 | 本技能 |
|---|---|---|---|
| 文字稿 | 慢、易漏 | 有 | 有，同时给 TXT 和 SRT |
| 后续改写 | 另开文档 | 自己处理 | 自动拆成按句改写表 |
| 重新配音 | 另找工具 | 无 | 同一流程直接用自己克隆的音色配音并出字幕 |
| 改稿 | 全部重来 | — | 配音按句缓存，改哪句重配哪句 |

## 常见问题（FAQ）

**能直接输入抖音、B站视频链接吗？**
不能。本技能只处理本地文件，不抓取链接。请使用你自己拥有或已授权的视频和音频。

**识别结果准吗？**
识别质量取决于录音清晰度；人名、专有名词请人工校对。支持的语言和格式以 `capabilities` 实时返回为准，本技能不做质量承诺。

**可以直接拿别人的视频文案当自己的吗？**
不可以。他人文案受著作权保护，只可作为参考，请写原创表达；需要转录他人内容时应取得授权。

**去哪里获取 API Key 和克隆音色？**
在 https://miragea.ai 注册，Key 在 https://miragea.ai/workspace/api 生成。没有 Key 时先用 `--dry-run`。

**改了一句要全部重配吗？**
不用，`voiceover.py` 按句缓存，重跑只配改动的句子。

**需要显卡吗？哪些 Agent 能用？**
不需要显卡，只跑 Python 标准库。Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 等能运行 Python 的 Agent 都能用。

## 出问题了？

| 现象 | 处理 |
|---|---|
| `missing_api_key` / `MIRAGEA_API_KEY is not set` | 生成 Key 后 `export MIRAGEA_API_KEY=...`；或先加 `--dry-run` |
| `speakers without a voice` | 给该角色补 `voice=角色名称` 或 `actor_id=`，或加 `--voice 角色名称`；还没有角色先 `create-actor` |
| `actor_not_found` / `ambiguous_actor_name` | `voice=` 的名称要和 `actors` 列表完全一致；同名角色改用 `actor_id=` |
| `no longer supported` | 旧稿件用了已停用的音频链接克隆写法：把录音 `create-actor` 建成角色，再改成 `voice=` 或 `actor_id=` |
| 401 | 检查 Key；不要把 Key 写进日志 |
| 403 | 检查账号的 API 访问权限 |
| 400 / 413 | 修正参数：模式、标签、语速、单句字数；或减小上传文件、缩短媒体 |
| 409 | 幂等键被用于不同输入，或字幕费率已变化：重新确认后再提交 |
| 429 | 额度不足或限流，等待或补充额度 |
| 等待超时 / 网络中断 | 任务可能仍在运行：直接重跑同一条命令（同一幂等键会取回原任务），或用 `miragea_audio.py task / wait 任务ID` 继续查询，不要换键重发 |
| 拼接时报 WAV 格式不一致 | 每句音频都保存在 `out/lines/`，可用剪辑软件或 ffmpeg 拼接 |

官方客户端退出码：0 请求成功（没有 `--wait` 时可能仍在排队），1 任务失败，2 客户端或接口错误。

## 限制与注意事项

- 只处理本地文件，不抓取链接，不做视频下载。
- 文字稿是一次性识别结果，不做说话人区分；多人录音请人工标注。
- 改写由使用者或 Agent 完成，脚本不会自动改写文案。
- 单句字数上限、文件大小以 `capabilities` 为准；`--dry-run` 只用于检查流程。

## 合规与 AI 生成内容标识

- 只处理你本人拥有或已获授权的音视频；不照搬他人文案，不侵犯著作权和隐私，涉及他人声音须取得同意。
- 只用你本人或已获书面授权的声音做克隆和配音。
- 按《人工智能生成合成内容标识办法》和各平台规则，发布时标注 AI 生成内容。
- `scripts/miragea_audio.py` is the official client 1.3.0, shipped unchanged；`scripts/voiceover.py`、`scripts/video_copy.py` 为原创，MIT 许可（见 `LICENSE.txt`）。

## English Summary

- **Video script extraction**: `video_copy.py extract MEDIA` runs the official `recognize` endpoint on a local file and writes `transcript.txt`, `transcript.srt` and a per-sentence `rewrite.md`.
- Rewrite each sentence in your own words, then `video_copy.py revoice rewrite.md` voices it with your own cloned or authorised voice into `voiceover.wav` + `voiceover.srt`.
- Local files only (no link scraping). Python 3.9+ stdlib, no GPU, `--dry-run` works without a key.

**关键词**：视频文案提取、视频转文字、音频转文字、音频转文案、口播文案提取、语音识别、字幕提取、文字稿、视频文案改写、改写重配音、声音克隆、AI配音、SRT字幕、video script extraction、video to text、speech to text
