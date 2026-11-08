---
name: "guanggao-ai-voiceover"
description: "广告片配音、宣传片配音、产品视频配音技能：品牌广告片、企业宣传片、产品介绍视频、App 演示视频、发布会短片的旁白和对白一键生成 AI 配音 WAV、SRT 字幕和逐句时间轴 manifest.json；停顿精确到小数秒，语速按角色控制，留白给画面和音乐。用 5–10 秒授权样本克隆品牌专属声音，同一份脚本快速出中英日韩德法俄葡西意 10 种语言版本，适合出海品牌和多市场投放；改一句文案只重配一句。文字转语音（TTS）由 Miragea API 完成，本地只需 Python 3.9+ 标准库、无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。Ad voiceover, commercial voice over, brand film narration, explainer video voiceover, text to speech, voice cloning."
version: "1.0.0"
display_name: "广告片配音｜宣传片产品视频AI配音·旁白·字幕"
display_name_en: "Ad Film & Promo Video AI Voiceover"
description_zh: "广告片配音：品牌广告、企业宣传片、产品介绍和App演示视频的旁白与对白一键生成AI配音WAV和SRT字幕，停顿语速可精细控制，同一品牌声音可出中英日韩等10种语言版本，本地无需显卡。"
description_en: "AI voiceover for ads, brand films, corporate promos, product and app demo videos: narration and dialogue with precise pauses and speed, voiceover WAV plus SRT subtitles, one brand voice in 10 languages. No GPU."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["广告片配音", "宣传片配音", "企业宣传片配音", "产品视频配音", "广告配音", "旁白配音", "AI配音", "品牌声音", "声音克隆", "多语种配音", "文字转语音", "TTS", "ad voiceover", "commercial voice over", "explainer video", "voice cloning"]
---

# 广告片配音

「广告片配音」是一个把品牌广告、企业宣传片、产品介绍和 App 演示视频脚本一键生成旁白与对白 AI 配音（WAV）和 SRT 字幕的 Agent 技能，停顿和语速可精细控制，同一品牌声音可出 10 种语言版本，本地无需显卡。

## 一句话定义

广告片配音 = 广告 / 宣传片脚本（旁白 + 对白，Markdown）→ 带留白的配音 `voiceover.wav` + 字幕 `voiceover.srt` + 每句起止时间 `manifest.json`，生成在 Miragea 云端，本地无需显卡。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 品牌市场部 | 品牌形象片、新品广告、节日营销短片 |
| 广告公司、制作公司 | 提案阶段先出 AI 配音小样，客户确认后再定稿 |
| 企业宣传 / 公关 | 企业宣传片、年会视频、招商片 |
| SaaS / App 团队 | 产品演示视频、功能介绍、上手教程旁白 |
| 出海品牌 | 一份脚本出英语、日语、西语、德语等多市场版本 |
| 展会、门店 | 循环播放的产品介绍视频 |

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
| 场景预设 | `--preset guanggao`：句间停顿 0.4 秒、字幕每条最多 14 字；可再用 `--gap` / `--max-chars` 覆盖 |
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
python3 scripts/voiceover.py script examples/example.md -o out --preset guanggao --dry-run   # 先离线试跑
python3 scripts/voiceover.py script 你的稿件.md -o out --preset guanggao                     # 正式生成
```

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “这条 30 秒广告脚本帮我配旁白” | 按镜头拆句、加留白 → `script 脚本.md -o out --preset guanggao` |
| “旁白加一段客户证言” | front matter 定义 `voice` 和 `customer` 两个音色 |
| “slogan 前停一下” | slogan 行前加 `[pause 0.8]` |
| “做 15 秒和 30 秒两个版本” | 两个脚本文件，分别生成，用 `manifest.json` 核对实际时长 |
| “出英文、日文版” | 按市场改写文案 → `language=en` / `language=ja`，同一品牌声音 |
| “App 演示视频配解说” | 一步操作一句话，按录屏时间对齐 |
| “品牌名念得不对” | 用 `say` 试听几种写法，选对的写进脚本 |
| “先给客户听个小样” | 正常生成即可；只想验证流程加 `--dry-run` |

## 广告片写稿方法论（广告配音的质感来自留白）

### 1. 广告片 ≠ 带货视频

| 维度 | 广告片 / 宣传片 | 带货视频 |
|---|---|---|
| 目标 | 记住品牌、建立好感 | 立刻下单 |
| 节奏 | 慢，有留白 | 快，信息密 |
| 句子 | 短句、意象、可以不完整 | 卖点、价格、指令 |
| 结尾 | 品牌名 + slogan（落版） | 行动指令 |
| 本技能预设 | `--preset guanggao`（句间 0.4 秒） | `--preset daihuo`（句间 0.1 秒） |

### 2. 品牌广告的五段结构

1. **意象开场**：一个画面感强的短句，“每一个清晨，都值得被认真对待。”
2. **情绪 / 场景**：两三句建立生活场景，句间留白。
3. **产品出现**：一句话把产品和场景连起来，不罗列参数。
4. **品牌主张**：一句态度或承诺。
5. **落版**：品牌名单独一行，停顿后接 slogan。

### 3. 留白的写法：停顿就是给画面和音乐的位置

- 场景之间 `[pause 0.4]`–`[pause 0.6]`；品牌名之前 `[pause 0.6]`；slogan 之前 `[pause 0.8]`。
- 旁白语速参考 `speed=0.9–1.0`；科技产品片可略快，`1.0–1.05`。
- 同一品牌声音需要“铺垫正常速度、slogan 更沉稳”：用同一个 actor_id 定义两个角色：

```markdown
---
voice: actor_id=BRAND_VOICE_ID speed=1.0
voice_slogan: actor_id=BRAND_VOICE_ID speed=0.9
---
```

### 4. 按时长控制字数：用真实时间轴核对

- 先写稿、正式生成一次，看 `manifest.json` 最后一句的 `end`，就是配音总时长。
- 超时就删句子，不要靠加快语速硬塞；广告片宁可少一句，也要留出落版画面。
- `--dry-run` 的时间轴是按字数估算的占位，只用来检查格式；卡时长以真实生成的结果为准。

### 5. 企业宣传片与产品演示的写法

**企业宣传片**：使命 → 实力（团队、能力、可核实的事实）→ 案例（一个具体客户故事）→ 愿景。每部分 2–4 句，避免空泛形容词堆叠（“领先”“卓越”“一流”）。

**App / SaaS 演示视频**：
- 一步操作 = 一句话，句子以动词开头：“点击右上角的加号。”“输入项目名称。”
- 先录屏，再按录屏里每一步的时长写句子，生成后用 `manifest.json` 核对。
- 界面上的按钮名在旁白里保持完全一致。

### 6. 品牌名和英文读法

- 品牌名、产品型号先用 `say` 试听几种写法（中文名、英文名、加空格的字母），选对的写进脚本。
- 中英混排时，英文单词保持完整；需要逐字母念的缩写用空格隔开。

### 7. 多语种版本：一个品牌，一个声音

- 每个市场一个脚本文件，内容按当地表达改写，不是逐字翻译；slogan 尤其要本地化。
- 所有版本使用同一个品牌克隆音色，`language=` 切换。
- 外语字幕建议 `--max-chars 40`。

## 示例稿件（examples/example.md）

```markdown
---
voice: actor_id=BRAND_VOICE_ID speed=0.95
---
# 产品宣传片示例（品牌名为虚构）
[voice] 每一个清晨，都值得被认真对待。
[pause 0.6]
从一杯咖啡开始，
到一天的第一个灵感。
[pause 0.4]
晨屿咖啡机。
让好状态，准时出现。
```

试跑：`python3 scripts/voiceover.py script examples/example.md -o out --preset guanggao --dry-run`

## 接入剪辑

```bash
# 配音替换原视频音轨（需要本机 ffmpeg）
ffmpeg -i 画面.mp4 -i out/voiceover.wav -map 0:v -map 1:a -c:v copy -shortest 配音版.mp4
# 把字幕烧进画面
ffmpeg -i 配音版.mp4 -vf subtitles=out/voiceover.srt -c:a copy 成片.mp4
```

```bash
# 简单配乐：背景音乐压低后与旁白混合（音量按成片听感调整）
ffmpeg -i out/voiceover.wav -i bgm.mp3 -filter_complex "[1:a]volume=0.2[b];[0:a][b]amix=inputs=2:duration=first" out/mix.wav
```

- **Premiere / 剪映 / CapCut**：`voiceover.wav` 放旁白轨，`voiceover.srt` 导入字幕轨；按 `manifest.json` 的时间对镜头和落版。
- 正式投放的混音、响度标准按投放平台要求在后期完成。

## 方案对比：广告片配音的三种做法

| 对比项 | 人工配音 | 本地开源 TTS 模型 | 本技能 |
|---|---|---|---|
| 是否需要显卡 | 不需要，但需要录音环境和配音员档期 | 通常需要（小模型可用 CPU，但更慢），还要下载模型权重、配置环境 | 不需要，本地只跑 Python 标准库，生成在云端完成 |
| 改稿成本 | 改一句往往要重新约录、补录，再对轨 | 改完重跑，但分段、拼接、对齐要自己做 | 只改那一行重跑，其余句子复用已生成结果，自动重新拼接和出字幕 |
| 多角色 | 需要多位配音员分别录制 | 取决于模型，一般要自己分段调用再拼接 | 稿件里用 `[角色]` 标签，一条命令出整段多角色音轨 |
| 多语种 | 需要对应语种的配音员 | 取决于模型支持的语种 | 10 种语言，同一个克隆音色可跨语言 |
| 字幕时间轴 | 需另外听写、打轴 | 一般要再跑一遍语音识别 | 配音时同时输出 SRT 和逐句时间 `manifest.json` |
| 脚本反复修改 | 每轮修改都要补录，客户确认周期长 | 重跑方便，但对齐和打轴要自己做 | 改一句重配一句，可先出 AI 小样给客户确认文案和节奏 |

结论：提案小样、多版本、多语种和频繁改稿的阶段，本技能最省时间；最终投放的大片如需细腻的情绪表演，可在文案定稿后再请真人配音，AI 小样正好作为录音参考。

## 常见问题（FAQ）

**广告片能用 AI 配音吗？需要注意什么？**
可以。声音必须是自有或已授权的，按平台规则标注 AI 生成内容，文案遵守《广告法》。

**给客户提案时，能先出一版 AI 配音小样吗？**
可以，这正是常见用法：先用 AI 配音确认文案和节奏，客户改一句只重配一句，定稿后再决定是否换真人。

**怎么做出品牌专属的声音？**
用已授权配音员或品牌代言声音的 5–10 秒清晰样本克隆一个音色，所有广告和宣传片都用这个 actor_id。

**30 秒广告的配音怎么卡准时长？**
正式生成后看 `manifest.json` 最后一句的 `end` 时间，超时就删句或缩短句子，不要硬提语速。

**宣传片需要旁白和人物对白两种声音吗？**
可以在 front matter 里定义多个角色，例如 `voice`（旁白）和 `customer`（客户证言），一条命令输出整段。

**同一条广告要出英文、日文、西班牙文版本怎么做？**
每种语言一个脚本，按当地表达改写，同一个品牌音色设置不同的 `language=`，10 种语言都支持。

**能直接生成带背景音乐的成品吗？**
本技能只输出纯人声配音和字幕；背景音乐用上面的 ffmpeg 命令或在剪辑软件里混合。

**品牌名、英文型号读错怎么办？**
先用 `say` 试听几种写法，选读对的那种写进脚本，只重配这一句。

**需要显卡吗？哪些 Agent 能用？**
不需要显卡，本地只跑 Python 3.9+ 标准库；Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 都能直接调用。

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
- 广告文案遵守《广告法》：不用极限用语，数据和功效宣称要有依据；不得用配音冒充名人或代言人为产品背书。
- 本技能代码为原创，MIT 许可（见 `LICENSE.txt`）；配音与字幕能力由 Miragea API 提供。

## English Summary

- **Ad film & promo video AI voiceover (广告片配音)** for brand films, commercials, corporate videos, product and app demo/explainer videos.
- Narration + dialogue with precise decimal-second pauses and per-voice speed; outputs voiceover WAV, SRT subtitles and per-line timing.
- **Brand voice cloning** from an authorized 5–10 s sample; localize one script into 10 languages with the same voice.
- `--preset guanggao` leaves room for visuals and music; check real duration in `manifest.json`.
- Python 3.9+ stdlib, no GPU, `--dry-run` offline; TTS by the Miragea API. Works with Claude Code, Codex, OpenClaw, Cursor, WorkBuddy.

**关键词**：广告片配音、宣传片配音、企业宣传片配音、产品视频配音、App演示视频配音、广告配音、旁白配音、品牌声音、AI配音、声音克隆、多语种配音、文字转语音、TTS、字幕生成、ad voiceover、commercial voice over、explainer video、voice cloning
