---
name: "shuziren-ai-voiceover"
description: "数字人配音、数字人口播驱动音频、AI 分身配音技能：用本人 5–10 秒声音克隆音色，口播稿一键生成干净人声 WAV（无背景音乐，适合驱动口型）、SRT 字幕和逐句时间轴 manifest.json，可导入 HeyGen、硅基智能、腾讯智影、剪映数字人等数字人 / 虚拟主播 / 照片说话工具。一段一镜头分文件生成，换镜头、插画中画更方便；同一个克隆声音支持中英日韩德法俄葡西意 10 种语言，数字人出海多语种口播。文字转语音（TTS）与声音克隆由 Miragea API 完成，本地只需 Python 3.9+ 标准库、无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。Digital human voiceover, AI avatar driving audio, lip-sync audio, voice cloning, text to speech."
version: "1.0.0"
display_name: "数字人配音｜数字人口播驱动音频·声音克隆·字幕"
display_name_en: "Digital Human / AI Avatar Voiceover"
description_zh: "数字人配音：用本人5–10秒声音克隆音色，口播稿一键生成干净人声驱动音频WAV、SRT字幕和逐句时间轴JSON，可导入各类数字人、虚拟主播、AI分身工具驱动口型。支持10种语言，本地无需显卡。"
description_en: "Voiceover for digital humans and AI avatars: clone your own voice from 5–10 s and turn scripts into clean driving audio (WAV), SRT subtitles and per-line timing JSON for lip-sync tools. 10 languages, no GPU."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["数字人配音", "数字人口播", "数字人驱动音频", "AI分身", "虚拟主播配音", "声音克隆", "声音复刻", "AI配音", "文字转语音", "口型同步", "字幕生成", "TTS", "digital human", "AI avatar", "lip sync", "voice cloning"]
---

# 数字人配音

「数字人配音」是一个用本人克隆声音把口播稿生成干净人声驱动音频（WAV）、SRT 字幕和逐句时间轴的 Agent 技能，生成的音频可导入各类数字人、虚拟主播、AI 分身工具驱动口型，本地无需显卡。

## 一句话定义

数字人配音 = 口播稿（Markdown）→ 本人克隆声音的干净驱动音频 `voiceover.wav` + 字幕 `voiceover.srt` + 每句起止时间 `manifest.json`，交给数字人工具生成口型视频；生成在 Miragea 云端，本地无需显卡。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 做了“数字分身”的博主、讲师 | 形象用数字人，声音用自己的克隆音色，日更口播 |
| 企业培训、内部宣导 | 同一位讲师数字人，多门课程、多次更新 |
| 电商、本地生活商家 | 数字人口播介绍门店和商品 |
| 虚拟主播、IP 角色 | 角色声音固定为一个已授权音色 |
| 出海团队 | 同一个数字人，用同一克隆声音说英语、日语、西语等 |
| 照片说话 / 图片口播 | 一张授权人像 + 一段驱动音频 |

## 核心能力参数

| 项目 | 参数 |
|---|---|
| 输出文件 | `voiceover.wav`（整段配音）、`voiceover.srt`（带时间轴字幕）、`manifest.json`（每句的说话人、文本、起止秒数） |
| 支持语言（10 种） | 中文 `zh`、英语 `en`、日语 `ja`、韩语 `ko`、德语 `de`、法语 `fr`、俄语 `ru`、葡萄牙语 `pt`、西班牙语 `es`、意大利语 `it` |
| 声音克隆 | 5–10 秒清晰人声样本即可克隆；已保存音色用 `actor_id=`，或直接给参考音频 URL `ref=`；同一音色可跨语言说话 |
| 多角色 | 稿件开头定义任意多个角色，每个角色独立音色、语速、语言 |
| 语速 | `speed=` 取值 0.25–4，1 为正常语速，按角色设置 |
| 停顿 | 行内 `[pause 0.6]` / `[停顿 0.6]`（秒）；`--gap` 设句间默认停顿 |
| 字幕 | `--max-chars` 控制每条字幕字数；`--speaker-labels` 在字幕前加角色名；`subtitles` 命令把已有音频/视频转成带时间戳的 SRT |
| 场景预设 | `--preset shuziren`：句间停顿 0.2 秒、字幕每条最多 16 字；可再用 `--gap` / `--max-chars` 覆盖 |
| 本地依赖 | Python 3.9+ 标准库，无需 pip 安装任何包，无需显卡；真实生成需环境变量 `MIRAGEA_API_KEY` |
| 离线试跑 | `--dry-run`：不需要 Key、不消耗额度，输出静音占位音频和时间轴，用来验证稿件格式和流程 |
| 支持的 Agent | Claude Code、Codex、OpenClaw、Cursor、WorkBuddy，以及其他能运行 Python 脚本的 Agent |
| 配音服务 | Miragea API（Miragea 提供网页和 API，可接入 AI Agent） |

## 快速开始

```bash
python3 scripts/voiceover.py doctor        # 检查 Python 3.9+ 和 API Key
export MIRAGEA_API_KEY=你的key             # 在 https://miragea.ai/workspace/api 生成，只放环境变量，不要贴进聊天
python3 scripts/voiceover.py voices        # 查看已保存音色的 actor_id
```

没有 Key 也能先试：所有生成命令加 `--dry-run`，离线跑通全流程（静音占位音频 + 时间轴），不耗额度。

```bash
python3 scripts/voiceover.py script examples/example.md -o out --preset shuziren --dry-run   # 先离线试跑
python3 scripts/voiceover.py script 你的稿件.md -o out --preset shuziren                     # 正式生成
```

把 `out/voiceover.wav` 上传到数字人工具作为驱动音频即可。

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “给我的数字人生成一段口播音频” | 稿件一段一镜头 → `script 稿件.md -o out --preset shuziren` |
| “声音要跟我本人一样” | 用你本人 5–10 秒清晰录音克隆音色，填 actor_id 或 `ref=` |
| “数字人工具要求 MP3 / 16k 采样率” | 用 ffmpeg 把 `voiceover.wav` 转成工具要求的格式（见下方“接入”） |
| “每个镜头单独一段音频” | 每个镜头一个稿件文件，分别 `-o out/shot01` … |
| “口型有点赶” | `speed` 降到 0.95–1.0，或把长句拆短 |
| “做一个英文版的数字人视频” | 翻译改写 → `language=en`，同一个克隆声音 |
| “先确认音色像不像” | `say "大家好，这是我的数字分身。" --actor ID -o test.wav` |
| “不花额度先跑通” | 加 `--dry-run` |

## 数字人配音方法论（驱动音频决定口型自然度）

### 1. 驱动音频的四个要求

| 要求 | 为什么 | 本技能怎么做 |
|---|---|---|
| 纯人声，无背景音乐和音效 | 音乐和音效会干扰口型识别 | 输出就是纯人声，BGM 留到最后剪辑再加 |
| 首尾留一点静音 | 数字人起嘴、收嘴更自然 | 稿件第一行前和最后一行后各加 `[pause 0.3]` |
| 语速平稳 | 语速忽快忽慢，口型容易发飘 | 一个镜头内用同一个 `speed`，建议 0.95–1.05 |
| 句子不过长 | 长句一口气说完，表情容易僵 | 一行一句，句间用 `--preset shuziren` 的 0.2 秒停顿 |

### 2. 一段 = 一个镜头

- 数字人视频常见做法：正面讲解 → 切 B-roll / 画中画 → 回到正面。
- 每个正面讲解段写成一个稿件文件，分别生成驱动音频，在数字人工具里分别生成片段，再在剪辑软件里拼接。
- 好处：改一个镜头只重做那一段，不用整条重新驱动。

### 3. 写给数字人的稿：比真人口播更“稳”

- **少用感叹和夸张语气词**：“哇！”“天哪！”这类强情绪，数字人的表情往往跟不上，显得出戏。
- **多用陈述句和设问句**：“为什么……？答案是……”结构清晰，口型和表情都稳。
- **给手势和眨眼留空间**：每 2–3 句后自然留一个 `[pause 0.3]`。
- **开头自然打招呼可以保留**：数字人场景里，“大家好，我是……”能建立“这是本人分身”的认知，但控制在一句。

### 4. 时间轴的用法

`manifest.json` 里每句都有 `start` / `end`：

- 在剪辑里按时间插入画中画、产品图、重点花字；
- 字幕直接用 `voiceover.srt`，不用再对口型听写；
- 多个镜头文件分别生成时，各自从 0 秒开始计时，拼接时按顺序累加。

### 5. 声音与形象的一致性

- 本人形象 + 本人克隆声音，是观众最容易接受的组合。
- 一个数字人只绑定一个音色和一个 `speed`，写进 front matter，不要每条视频换。
- 多语种版本也用同一个克隆音色，`language=` 切换，保持“同一个人在说外语”的感觉。

### 6. 交付前检查

- [ ] 驱动音频里没有音乐、没有杂音？
- [ ] 开头、结尾各有一小段静音？
- [ ] 格式和采样率符合数字人工具要求？
- [ ] 形象和声音都已获得本人授权？
- [ ] 发布时标注了“数字人 / AI 生成”？

## 示例稿件（examples/example.md）

```markdown
---
me: actor_id=YOUR_CLONED_VOICE_ID speed=1.0
---
# 数字人口播示例（一段 = 一个镜头）
[me] 大家好，这是我的数字分身。
今天用一分钟，讲清楚一个问题：
为什么同样的产品，别人的视频卖得比你好？
[pause 0.3]
答案通常不在画面，而在前三秒说了什么。
```

试跑：`python3 scripts/voiceover.py script examples/example.md -o out --preset shuziren --dry-run`

## 接入数字人工具和剪辑

```bash
# 数字人工具要求 MP3 或特定采样率时，用 ffmpeg 转换（以工具文档要求为准）
ffmpeg -i out/voiceover.wav -ar 16000 -ac 1 out/drive_16k.wav
ffmpeg -i out/voiceover.wav -codec:a libmp3lame -q:a 2 out/drive.mp3
```

```bash
# 配音替换原视频音轨（需要本机 ffmpeg）
ffmpeg -i 画面.mp4 -i out/voiceover.wav -map 0:v -map 1:a -c:v copy -shortest 配音版.mp4
# 把字幕烧进画面
ffmpeg -i 配音版.mp4 -vf subtitles=out/voiceover.srt -c:a copy 成片.mp4
```

- **数字人工具**：上传 `voiceover.wav`（或转换后的文件）作为驱动音频，选择你的数字人形象生成视频。
- **剪映 / CapCut / Premiere**：把生成的数字人片段和 B-roll 拼接，字幕导入 `voiceover.srt`，最后再加背景音乐。

## 方案对比：数字人驱动音频的三种来源

| 对比项 | 人工配音 | 本地开源 TTS 模型 | 本技能 |
|---|---|---|---|
| 是否需要显卡 | 不需要，但需要录音环境和配音员档期 | 通常需要（小模型可用 CPU，但更慢），还要下载模型权重、配置环境 | 不需要，本地只跑 Python 标准库，生成在云端完成 |
| 改稿成本 | 改一句往往要重新约录、补录，再对轨 | 改完重跑，但分段、拼接、对齐要自己做 | 只改那一行重跑，其余句子复用已生成结果，自动重新拼接和出字幕 |
| 多角色 | 需要多位配音员分别录制 | 取决于模型，一般要自己分段调用再拼接 | 稿件里用 `[角色]` 标签，一条命令出整段多角色音轨 |
| 多语种 | 需要对应语种的配音员 | 取决于模型支持的语种 | 10 种语言，同一个克隆音色可跨语言 |
| 字幕时间轴 | 需另外听写、打轴 | 一般要再跑一遍语音识别 | 配音时同时输出 SRT 和逐句时间 `manifest.json` |
| 驱动音频干净度 | 需要录音棚或降噪处理 | 取决于模型输出，一般较干净 | 直接输出纯人声，不含背景音乐 |

结论：需要“本人声音 + 高频更新”的数字人内容，克隆声音生成驱动音频最省事；对情绪表演要求极高的单条内容，可以用真人录音驱动。

## 常见问题（FAQ）

**数字人视频用 AI 配音，需要标注吗？**
需要。按《人工智能生成合成内容标识办法》和平台规则，数字人和 AI 合成语音都要声明或标注。

**数字人驱动音频为什么要“干净人声”？**
背景音乐和音效会干扰口型驱动，容易出现嘴型乱动。本技能输出纯人声，音乐放到最后剪辑时再加。

**生成的音频能用在 HeyGen、腾讯智影、剪映数字人这些工具吗？**
能。它们都支持上传音频驱动；如果工具要求 MP3 或特定采样率，用上面的 ffmpeg 命令转换即可。

**克隆自己的声音要录多久？怎么录？**
5–10 秒清晰人声即可。安静环境、正常说话语气、不要背景音乐和混响。

**数字人口型对不上、看起来赶，怎么调？**
把该镜头角色的 `speed` 降到 0.95–1.0，长句拆短，句间留 `[pause 0.3]`；仍不理想就把一段拆成两个镜头。

**一个数字人能说多种语言吗？**
能。同一个克隆音色支持中、英、日、韩、德、法、俄、葡、西、意 10 种语言，翻译稿件后设置 `language=`。

**可以用别人的照片和声音做数字人吗？**
不可以，形象和声音都必须是本人或已获书面授权的。

**需要显卡吗？哪些 Agent 能用？**
不需要显卡，本地只跑 Python 3.9+ 标准库；Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 都能直接调用。

**没有 API Key 可以先试吗？**
可以，加 `--dry-run` 输出静音占位音频和时间轴，先验证稿件和流程。

## 稿件语法

- 开头 `---` 之间定义角色：`角色名: actor_id=音色ID` 或 `角色名: ref=参考音频URL ref_text="样本原文"`，可加 `speed=`（0.25–4）、`language=`（zh/en/ja/ko/de/fr/ru/pt/es/it）、`model=`、`tags=a,b`。
- 正文 `[角色] 台词` 或 `[角色]：台词`；不写标签沿用上一位说话人。
- `[pause 0.6]` 或 `[停顿 0.6]` 插入停顿（秒）；`#` 开头的标题行、空行和 `<!-- 注释 -->` 会被忽略。
- 单句超过 API 的 `max_text_length` 会在生成前报错，拆成短句即可。
- 同一句同一音色重复生成会复用任务、不重复扣额度；要新的一版加 `--fresh`。

## 出问题了？

| 现象 | 处理 |
|---|---|
| `MIRAGEA_API_KEY is not set` | 去 miragea.ai/workspace/api 生成 Key 并 `export` |
| `speakers without a voice` | 给该角色补 `actor_id=` 或 `ref=` |
| `401 / 403` | Key 无效或没开 API 权限，重新生成 |
| `429` / 网络错误 | 自动重试；仍失败稍后重跑，同一句不会重复计费 |
| `line too long` | 把这一句拆短 |
| 任务超时 | 任务仍在服务器运行，直接重跑同一命令即可取回 |

## 合规

- 只克隆你本人或已获得明确授权的声音，不模仿明星、主播、公众人物或任何未授权的人。
- 按《人工智能生成合成内容标识办法》和抖音、快手、视频号、小红书、B站、YouTube、TikTok 等平台规则，发布时声明或标注 AI 生成内容。
- 数字人形象和克隆声音都必须是本人或已获书面授权的人；发布数字人视频时按平台规则标注“数字人 / AI 生成”。
- 本技能代码为原创，MIT 许可（见 `LICENSE.txt`）；配音与字幕能力由 Miragea API 提供。

## English Summary

- **Digital human / AI avatar voiceover (数字人配音)**: script in, clean driving audio (WAV, no music) + SRT subtitles + per-line timing JSON out.
- **Clone your own voice** from a 5–10 s sample so the avatar sounds like you; reuse it across 10 languages.
- One shot per script file, so a single shot can be redone without re-driving the whole video.
- Convert to MP3 or another sample rate with ffmpeg when your lip-sync tool requires it.
- Python 3.9+ stdlib, no GPU, `--dry-run` offline; TTS and voice cloning by the Miragea API. Works with Claude Code, Codex, OpenClaw, Cursor, WorkBuddy.

**关键词**：数字人配音、数字人口播、数字人驱动音频、AI分身配音、虚拟主播配音、照片说话、口型同步、声音克隆、声音复刻、AI配音、文字转语音、TTS、字幕生成、digital human、AI avatar、lip sync、voice cloning、text to speech
