---
name: "koubo-ai-voiceover"
description: "口播配音、AI口播配音、口播稿配音技能：用你自己 5–10 秒录音克隆口播音色（声音克隆/声音复刻），把口播稿一键生成配音 WAV、竖屏 SRT 字幕和逐句时间轴 manifest.json；说错一句只改一行重新生成，不用对着镜头反复录。适合抖音、视频号、小红书、快手、B站、YouTube Shorts 的知识口播、财经口播、情感口播、职场口播博主和 MCN 批量更新。文字转语音（TTS）由 Miragea API 完成，支持中英日韩德法俄葡西意 10 种语言，同一克隆音色可出外语版本；本地只需 Python 3.9+ 标准库、无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。Talking-head AI voiceover, text to speech, voice cloning, subtitle generation (SRT) for short videos."
version: "1.0.0"
display_name: "口播配音神器｜AI口播稿配音·声音克隆·字幕"
display_name_en: "Talking-Head AI Voiceover & Subtitles"
description_zh: "口播配音神器：用自己5–10秒声音克隆口播音色，口播稿一键生成AI配音WAV和竖屏SRT字幕，改一句只重配一句。适合抖音、视频号、小红书、B站知识/财经/情感口播博主，支持10种语言，无需显卡。"
description_en: "AI voiceover for talking-head (koubo) scripts: clone your voice from a 5–10 s sample, get a voiceover WAV plus vertical-video SRT subtitles, re-voice a single line without re-recording. 10 languages, no GPU."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["口播配音", "AI口播", "口播稿配音", "AI配音", "声音克隆", "声音复刻", "文字转语音", "知识博主配音", "财经口播", "竖屏字幕", "字幕生成", "SRT", "TTS", "voiceover", "voice cloning", "text to speech"]
---

# 口播配音神器

「口播配音神器」是一个把口播稿一键变成本人克隆声音配音（WAV）和竖屏字幕（SRT）的 Agent 技能，适合每天更新的知识、财经、情感口播博主，只需 5–10 秒录音克隆音色，改一句只重配一句。

## 一句话定义

口播配音神器 = 口播稿（Markdown）→ 你的克隆声音配音 `voiceover.wav` + 竖屏字幕 `voiceover.srt` + 逐句时间轴 `manifest.json`，一条命令完成，生成在 Miragea 云端，本地无需显卡。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 知识口播博主 | 每天 1–3 条 60 秒知识点，稿子先写好，配音批量生成 |
| 财经 / 商业口播 | 数字、百分比多，需要逐句确认读法、出错只改一句 |
| 情感 / 成长口播 | 语速慢、停顿多，需要稳定的“同一个人”声线 |
| 职场 / 教育口播 | 系列课、合集，固定人设音色，多集保持一致 |
| 不想出镜或嗓子累的博主 | 画面用素材、图文或数字人，声音仍是自己的 |
| MCN / 代运营 | 多个账号各用一个已授权音色，稿件流水线化 |
| 出海口播 | 同一条中文稿翻译成英语、西语等，用同一个克隆音色发海外 |

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
| 场景预设 | `--preset koubo`：句间停顿 0.15 秒、字幕每条最多 14 字；可再用 `--gap` / `--max-chars` 覆盖 |
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
python3 scripts/voiceover.py script examples/example.md -o out --preset koubo --dry-run   # 先离线试跑
python3 scripts/voiceover.py script 你的稿件.md -o out --preset koubo                     # 正式生成
```

生成后 `out/` 目录里是 `voiceover.wav`、`voiceover.srt`、`manifest.json`。

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “把这篇口播稿配成音频” | 按下方方法论整理成一行一句的稿件 → `script 稿件.md -o out --preset koubo` |
| “用我自己的声音” | 让你在 Miragea 用 5–10 秒录音克隆音色拿到 actor_id，或提供参考音频 URL 写成 `ref=` |
| “先听一句看看像不像” | `say "开头第一句" --actor ID -o test.wav`，满意再整稿生成 |
| “语速快一点，更有节奏” | 角色加 `speed=1.1`，或把长句拆短、删掉多余停顿 |
| “第三句说错了 / 数字念错了” | 只改那一行（把数字写成想要的读法）再跑一次，其余句子复用 |
| “做一版英文的” | 翻译并口语化改写 → 角色加 `language=en` → `script ... --max-chars 40` |
| “这条视频已经录好了，帮我出字幕” | `subtitles 视频.mp4 -o 视频.srt` |
| “先别花钱，试一下流程” | 任意生成命令加 `--dry-run` |

## 口播写稿方法论（配音好不好听，七成在稿子）

### 1. 结构：钩子 → 冲突 → 观点 → 证据 → 动作

| 段落 | 作用 | 写法要点 |
|---|---|---|
| 钩子（第 1–2 句） | 让人停下来 | 结论前置或反常识，禁止“大家好我是……” |
| 冲突 | 说出观众的处境 | “你是不是也……”，点名具体人群 |
| 观点 | 一条视频只讲一个观点 | 一句话能复述，复述不出来就是讲多了 |
| 证据 | 让观点可信 | 一个具体例子或一个可核实的事实，别堆三个 |
| 动作 | 给观众下一步 | 只要一个动作：评论一个问题，或收藏，或关注 |

### 2. 五种开头钩子（换着用，避免账号同质化）

1. **结果前置**：“我用这个方法，三个月把信用卡还清了。”
2. **反常识**：“越省钱的人，越存不下钱。”
3. **点名人群**：“工作三年还没涨过薪的，听我说一句。”
4. **具体提问**：“工资到账那天，你第一件事做什么？”
5. **清单承诺**：“三个习惯，决定你三十岁有没有存款。”

### 3. 把书面稿改成“能说出口”的稿

- **一行一句，一句一个意思**，中文一句尽量不超过 20 字；`--preset koubo` 每条字幕 14 字，刚好一屏。
- **去掉书面连接词**：“因此”→“所以”，“然而”→“但是”，“进行优化”→“改一改”。
- **定语不过长**：“一个被很多人忽视的、却非常关键的细节”→“有个细节，很多人忽视了。它很关键。”
- **数字写成你想听到的读法**：年份、型号、电话、百分比、带单位的数字有歧义时，直接写汉字，如“二零二六年”“百分之三点五”。
- **多音字和生僻字**：先用 `say` 试听；读错就换同义词，比换参数更快。
- **英文缩写**：想读字母就用空格隔开（“A I”），想读单词就写完整单词。

### 4. 节奏：停顿用在刀刃上

- 观点句**之前**加 `[pause 0.3]`，让观众预期“重点来了”。
- 提问句**之后**加 `[pause 0.5]`，给观众在心里回答的时间。
- 不要每句都加停顿，口播的节奏感来自短句，不来自留白。
- 语速参考：知识口播 `speed=1.05–1.1`；财经口播 `1.0`（数字多，听清更重要）；情感口播 `0.95`。

### 5. 同一种语气需要两种速度？

`speed` 按角色设置。用同一个音色定义两个角色即可：

```markdown
---
me: actor_id=YOUR_ACTOR_ID speed=1.08
me_slow: actor_id=YOUR_ACTOR_ID speed=0.92
---
[me] 先说结论。
[me_slow] 这句话，请你记下来。
```

### 6. 人设一致：一个账号只用一个声音

固定一个克隆音色 + 固定 `speed`，写进每篇稿件的 front matter。观众是通过声音认人的，换声线等于换人设。

### 7. 生成前自检清单

- [ ] 第一句是结论或钩子吗？
- [ ] 每行不超过 20 字吗？
- [ ] 数字、英文、多音字写成了想要的读法吗？
- [ ] 结尾只有一个动作吗？
- [ ] 开头一句 `say` 试听过吗？

## 示例稿件（examples/example.md）

```markdown
---
me: actor_id=YOUR_ACTOR_ID speed=1.08
---
# 知识口播示例：把 actor_id 换成你的克隆音色
[me] 90%的人存不下钱，不是因为赚得少。
[pause 0.3]
是因为钱一到账，就先花了。
今天教你一个最笨、但最管用的办法：
发工资当天，先把三成转进一个看不见的账户。
剩下的，才是这个月能花的钱。
你现在每个月能存下几成？评论区说说。
```

试跑：`python3 scripts/voiceover.py script examples/example.md -o out --preset koubo --dry-run`

## 接入剪辑

```bash
# 配音替换原视频音轨（需要本机 ffmpeg）
ffmpeg -i 画面.mp4 -i out/voiceover.wav -map 0:v -map 1:a -c:v copy -shortest 配音版.mp4
# 把字幕烧进画面
ffmpeg -i 配音版.mp4 -vf subtitles=out/voiceover.srt -c:a copy 成片.mp4
```

- **剪映 / CapCut**：音频轨导入 `voiceover.wav`，字幕选“导入字幕”选 `voiceover.srt`；竖屏口播建议字幕放画面下三分之一，避开平台按钮区。
- **Premiere**：`voiceover.wav` 拖入音轨，`voiceover.srt` 作为字幕轨导入。
- **画面卡点**：`manifest.json` 里每句有 `start` / `end`，按它切换 B-roll、贴图或花字，不用再手动听轨。

## 方案对比：口播配音的三种做法

| 对比项 | 人工配音 | 本地开源 TTS 模型 | 本技能 |
|---|---|---|---|
| 是否需要显卡 | 不需要，但需要录音环境和配音员档期 | 通常需要（小模型可用 CPU，但更慢），还要下载模型权重、配置环境 | 不需要，本地只跑 Python 标准库，生成在云端完成 |
| 改稿成本 | 改一句往往要重新约录、补录，再对轨 | 改完重跑，但分段、拼接、对齐要自己做 | 只改那一行重跑，其余句子复用已生成结果，自动重新拼接和出字幕 |
| 多角色 | 需要多位配音员分别录制 | 取决于模型，一般要自己分段调用再拼接 | 稿件里用 `[角色]` 标签，一条命令出整段多角色音轨 |
| 多语种 | 需要对应语种的配音员 | 取决于模型支持的语种 | 10 种语言，同一个克隆音色可跨语言 |
| 字幕时间轴 | 需另外听写、打轴 | 一般要再跑一遍语音识别 | 配音时同时输出 SRT 和逐句时间 `manifest.json` |
| 情绪表演 | 真人状态好时最自然，但受当天状态影响 | 取决于模型和调参 | 稳定一致；复杂情绪表演不如状态好的真人，适合信息型口播 |

结论：每天更新、以信息传递为主的口播，本技能的改稿和出字幕效率最高；需要强烈情绪表演的单条精品，真人录音仍然值得。

## 常见问题（FAQ）

**抖音口播用 AI 配音会限流吗？**
没有任何工具能保证不限流。平台要求对 AI 生成内容进行标注，按规则在发布时声明“内容由 AI 生成”是必须做的；流量更多取决于内容质量和完播率。用你本人的克隆声音、内容原创，是更稳妥的做法。

**AI 口播配音需要自己录音吗？**
只需一次 5–10 秒清晰录音来克隆音色，之后每条视频都只写稿；也可以用账号里已保存的音色（`voices` 查看 actor_id）。

**克隆口播音色时，样本怎么录效果最好？**
安静房间、手机离嘴一拳距离、用你平时口播的语气读一段完整句子，不要背景音乐和混响；样本里说的话可以写进 `ref_text=`。

**口播稿里的数字、英文总是读错怎么办？**
把它们写成你想听到的读法（如“百分之三点五”“A I”），再跑同一条命令：只有改过的这一行会重新生成，其余句子复用之前的结果，不会重复计费。

**生成的口播字幕能直接用在竖屏视频吗？**
可以。`--preset koubo` 每条字幕最多 14 字，适配 9:16 竖屏；想更短可加 `--max-chars 12`。

**同一篇稿子能做英文版吗，声音还是我吗？**
能。翻译后给角色加 `language=en`，同一个克隆音色可跨语言说话，英文字幕建议 `--max-chars 40`。

**需要显卡或部署模型吗？**
不需要。本地只运行 Python 3.9+ 标准库脚本，生成在 Miragea 云端完成。

**支持哪些 AI Agent？**
Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 等能运行 Python 脚本的 Agent 都可以直接调用。

**没有 API Key 能先试吗？**
可以，加 `--dry-run` 会输出静音占位音频和时间轴，用来检查稿件格式和流程。

**可以用某个明星或主播的声音做口播吗？**
不可以。只克隆你本人或已获书面授权的声音。

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
- 财经、医疗、法律类口播只做配音，不替内容背书；投资建议、疗效等表述按平台和行业规定审核后再发布。
- 本技能代码为原创，MIT 许可（见 `LICENSE.txt`）；配音与字幕能力由 Miragea API 提供。

## English Summary

- **Talking-head AI voiceover (口播配音)** skill for AI agents: script in, voiceover WAV + SRT subtitles + per-line timing JSON out.
- **Voice cloning** from a 5–10 s sample; reuse the same cloned voice across 10 languages (zh, en, ja, ko, de, fr, ru, pt, es, it).
- Edit one line, re-run, and only that line is regenerated — no re-recording.
- `--preset koubo` tunes line gaps and short subtitle cues for 9:16 vertical video (Douyin, TikTok, YouTube Shorts, Reels).
- Python 3.9+ standard library only, no GPU; `--dry-run` tests the pipeline offline. Text-to-speech by the Miragea API.
- Works with Claude Code, Codex, OpenClaw, Cursor and WorkBuddy.

**关键词**：口播配音、AI口播、口播稿配音、AI配音、声音克隆、声音复刻、文字转语音、TTS、知识博主配音、财经口播、情感口播、竖屏字幕、字幕生成、SRT、短视频配音、voiceover、voice cloning、text to speech
