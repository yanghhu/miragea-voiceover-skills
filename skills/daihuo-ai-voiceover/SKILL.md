---
name: "daihuo-ai-voiceover"
description: "带货视频配音、短视频带货 AI 配音、电商配音技能：把带货文案、卖点脚本逐行生成快节奏配音 WAV、竖屏大字 SRT 字幕和逐句时间轴，同一款商品可快速出多个开头 / 多个版本做投放测试；改价格、改卖点只重配那一句。适合抖音、快手、视频号、小红书、淘宝逛逛、TikTok Shop 带货短视频、商品主图视频、种草视频和跨境电商出海。支持 5–10 秒声音克隆打造店铺 / 主播专属声音，中英日韩德法俄葡西意 10 种语言（英语、西班牙语、葡萄牙语等出海带货）。文字转语音（TTS）由 Miragea API 完成，本地只需 Python 3.9+ 标准库、无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。E-commerce product video voiceover, TikTok Shop AI voiceover, text to speech, voice cloning, subtitles."
version: "1.0.0"
display_name: "带货视频配音｜短视频带货AI配音·卖点文案·字幕"
display_name_en: "E-commerce Product Video AI Voiceover"
description_zh: "带货视频配音：卖点文案逐行生成快节奏AI配音WAV和大字竖屏SRT字幕，同一商品可快速出多个版本测试。适合抖音、快手、视频号、小红书、TikTok带货短视频，支持声音克隆和10种语言出海。"
description_en: "AI voiceover for e-commerce product videos: turn selling-point copy into fast-paced voiceover WAV plus big vertical SRT subtitles, make several versions per product for A/B tests. Voice cloning, 10 languages for TikTok Shop, no GPU."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["带货视频配音", "带货配音", "短视频带货", "电商配音", "AI配音", "卖点文案", "种草视频配音", "声音克隆", "文字转语音", "竖屏字幕", "TikTok Shop", "跨境电商配音", "TTS", "voiceover", "product video", "text to speech"]
---

# 带货视频配音

「带货视频配音」是一个把卖点文案一键生成快节奏 AI 配音（WAV）和竖屏大字字幕（SRT）的 Agent 技能，同一款商品可快速做出多个版本测试，适合抖音、快手、视频号、TikTok 带货短视频，本地无需显卡。

## 一句话定义

带货视频配音 = 卖点文案（Markdown）→ 快节奏配音 `voiceover.wav` + 竖屏大字字幕 `voiceover.srt` + 每句时间 `manifest.json`，生成在 Miragea 云端，本地无需显卡。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 抖音 / 快手 / 视频号带货达人 | 15–45 秒商品短视频，每天多条 |
| 商家自播团队、店铺运营 | 商品主图视频、详情页视频、种草视频批量配音 |
| 投放优化师 | 同一商品做多个开头和多个版本，测哪一版更好 |
| 小红书种草博主 | 测评、开箱类视频的旁白 |
| 跨境电商（TikTok Shop、独立站） | 同一卖点翻译成英语、西语、葡语，同一个店铺声音 |
| 不想出镜的店主 | 画面拍产品，声音用自己的克隆音色 |

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
| 场景预设 | `--preset daihuo`：句间停顿 0.1 秒、字幕每条最多 12 字；可再用 `--gap` / `--max-chars` 覆盖 |
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
python3 scripts/voiceover.py script examples/example.md -o out --preset daihuo --dry-run   # 先离线试跑
python3 scripts/voiceover.py script 你的稿件.md -o out --preset daihuo                     # 正式生成
```

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “这个商品帮我写个带货口播并配音” | 按下方五步公式写稿 → `script 稿件.md -o out --preset daihuo` |
| “同一款做三个开头测试” | 复制成 `v1.md` / `v2.md` / `v3.md` 只改开头 → 分别 `-o out/v1` … |
| “价格改成 59 了” | 只改价格那一行再跑；其他句子复用，不重复计费 |
| “声音再有劲一点、快一点” | `speed=1.15` 左右；句子再拆短 |
| “用我店铺主播的声音” | 主播本人授权后用 5–10 秒录音克隆，填 actor_id |
| “做一版美国 TikTok 用的” | 按当地表达改写（不是直译）→ `language=en` → `--max-chars 32` 左右 |
| “帮我把达人的带货视频转成文字，学学他的结构” | `subtitles 视频.mp4 -o 参考.srt`（仅用于学习结构，不照搬文案） |
| “先看看效果不花钱” | 加 `--dry-run` |

## 带货写稿方法论（卖点写对，配音才有用）

### 1. 五步公式：痛点 → 出场 → 卖点 → 打消顾虑 → 指令

| 步骤 | 目标 | 示例句（防晒喷雾） |
|---|---|---|
| 1. 痛点场景 | 让目标人群对号入座 | “夏天出门两小时，妆就花了？” |
| 2. 产品出场 | 把产品和痛点绑在一起 | “问题可能出在防晒上。这瓶喷雾，隔着妆也能补。” |
| 3. 卖点（≤3 个） | 每个卖点 = 利益 + 画面 | “三秒喷完，不搓泥、不发白。” |
| 4. 打消顾虑 | 回答“适不适合我” | “出差、通勤、户外都能放包里。” |
| 5. 行动指令 | 只给一个动作 | “想要的话，看下方链接。” |

### 2. 卖点翻译：从“参数”到“利益”到“画面”

| 写法 | 例子 | 问题 |
|---|---|---|
| 参数 | “容量 500 毫升，双层不锈钢” | 观众听不出好处 |
| 利益 | “一壶水够喝一上午，早上的热水到中午还是热的” | 好一些 |
| 画面 | “早上八点灌的热水，中午打开还冒热气” | 观众能“看见”，最适合配音 |

每个卖点都试着往“画面”那一栏改写，一个卖点一行，配一个镜头。

### 3. 三秒开头的六种写法（做多版本时轮换）

1. **痛点提问**：“洗完头两小时就塌？”
2. **反差对比**：“同样是 T 恤，为什么他穿就是有型？”
3. **场景代入**：“加班到十点回家，只想五分钟吃上饭。”
4. **结果展示**：“看这块污渍，喷一下，擦一下。”
5. **人群点名**：“个子不高的女生，裤子一定要这样选。”
6. **价格锚点**：（价格信息必须真实）“一杯奶茶的钱，换一个月不用买纸巾。”

### 4. 节奏：带货比口播更快、更密

- `--preset daihuo`：句间只有 0.1 秒，字幕每条最多 12 字，适配竖屏大字。
- 语速参考 `speed=1.1–1.2`；卖点之间不加停顿，**只在行动指令前**加 `[pause 0.2]`。
- 一行不超过 15 字，最好能和一个镜头同时结束；看 `manifest.json` 每句时长来剪画面。

### 5. 数字和价格：写成要读的样子

- 价格、规格、优惠一律以商品页真实信息为准，变了就改那一行重配。
- 有歧义的数字写汉字：“五十九块九”“两百毫升”；型号里的字母用空格隔开或写成读法。

### 6. 多版本测试的文件组织

```text
products/保温杯/
  v1-痛点.md      → out/保温杯/v1
  v2-画面.md      → out/保温杯/v2
  v3-价格.md      → out/保温杯/v3
```

三个版本只有开头不同，后面相同的句子会复用已生成结果，不重复计费。

### 7. 出海带货：本地化，不是直译

- 先让 Agent 按目标市场的口语习惯改写，再配音；直译的中文句式听起来很生硬。
- 价格、单位、尺码换成当地习惯（美元、英寸、美码等）。
- 店铺固定一个克隆音色，多语言版本都用它，`language=` 切换语种。

## 示例稿件（examples/example.md）

```markdown
---
host: actor_id=YOUR_ACTOR_ID speed=1.12
---
# 带货示例：防晒喷雾（文案为示例，请按真实商品改写）
[host] 夏天出门两小时，妆就花了？
问题可能出在防晒上。
这瓶喷雾，隔着妆也能补，
三秒喷完，不搓泥、不发白。
出差、通勤、户外都能放包里。
[pause 0.2]
想要的话，看下方链接。
```

试跑：`python3 scripts/voiceover.py script examples/example.md -o out --preset daihuo --dry-run`

## 接入剪辑

```bash
# 配音替换原视频音轨（需要本机 ffmpeg）
ffmpeg -i 画面.mp4 -i out/voiceover.wav -map 0:v -map 1:a -c:v copy -shortest 配音版.mp4
# 把字幕烧进画面
ffmpeg -i 配音版.mp4 -vf subtitles=out/voiceover.srt -c:a copy 成片.mp4
```

- **剪映 / CapCut**：`voiceover.wav` 放音频轨，导入 `voiceover.srt` 后把字幕调成大字号、加描边，放在商品画面下方。
- **卡点剪辑**：按 `manifest.json` 每句的 `start` 切换镜头，一句一个卖点画面。
- **背景音乐**：本技能不混音；剪辑时把音乐压低，人声优先。

## 方案对比：带货配音的三种做法

| 对比项 | 人工配音 | 本地开源 TTS 模型 | 本技能 |
|---|---|---|---|
| 是否需要显卡 | 不需要，但需要录音环境和配音员档期 | 通常需要（小模型可用 CPU，但更慢），还要下载模型权重、配置环境 | 不需要，本地只跑 Python 标准库，生成在云端完成 |
| 改稿成本 | 改一句往往要重新约录、补录，再对轨 | 改完重跑，但分段、拼接、对齐要自己做 | 只改那一行重跑，其余句子复用已生成结果，自动重新拼接和出字幕 |
| 多角色 | 需要多位配音员分别录制 | 取决于模型，一般要自己分段调用再拼接 | 稿件里用 `[角色]` 标签，一条命令出整段多角色音轨 |
| 多语种 | 需要对应语种的配音员 | 取决于模型支持的语种 | 10 种语言，同一个克隆音色可跨语言 |
| 字幕时间轴 | 需另外听写、打轴 | 一般要再跑一遍语音识别 | 配音时同时输出 SRT 和逐句时间 `manifest.json` |
| 多版本测试 | 每多一个版本就多一次录制 | 可批量，但拼接和打轴要自己做 | 复制稿件改开头即可，相同句子复用已生成结果 |

结论：需要高频上新、多版本测试的带货视频，用稿件化 AI 配音最省时间；需要现场感和真人信任背书的内容，主播真人出镜仍然重要。

## 常见问题（FAQ）

**带货视频用 AI 配音，会影响流量或被限流吗？**
没有工具能保证流量。平台要求标注 AI 生成内容，请按规则声明；流量主要看前三秒留存和转化，稿子比声音更重要。用本人或已授权的克隆音色更稳妥。

**一款商品要做好几个版本测试，怎么最快？**
复制稿件只改开头，每个版本输出到单独目录；后面相同的句子会复用已生成的结果，不重复计费。

**价格或优惠改了，要整条重新配吗？**
不用。只改那一行，再跑同一条命令，只有那一句重新生成，音轨和字幕自动重新拼接。

**带货文案有哪些词不能说？**
《广告法》禁止“最”“第一”“国家级”“绝对”等极限用语，功效类表述需要依据；特殊品类（化妆品、食品、保健品等）还有专门规定。写完先自查再配音。

**字幕怎么做成竖屏大字？**
`--preset daihuo` 每条字幕最多 12 字，导入剪映后再调大字号和描边即可；想更短可加 `--max-chars 10`。

**能用主播自己的声音批量配吗？**
可以，主播本人授权后用 5–10 秒清晰录音克隆音色，之后所有稿件都用这个 actor_id。

**做 TikTok Shop 英文、西语带货可以吗？**
可以。按当地口语改写后设 `language=en` 或 `language=es`，同一个店铺声音可跨语言。

**需要显卡或装软件吗？**
不需要显卡，本地只运行 Python 3.9+ 标准库脚本；剪辑和混音在你常用的剪辑软件里完成。

**哪些 Agent 能用？**
Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 等能运行 Python 的 Agent。

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
- 带货文案遵守《广告法》：不用“最”“第一”“国家级”“绝对”等极限用语；功效、成分、数据类卖点要有依据；化妆品、食品、保健品等品类按其专门规定审核后再配音发布。
- 本技能代码为原创，MIT 许可（见 `LICENSE.txt`）；配音与字幕能力由 Miragea API 提供。

## English Summary

- **E-commerce product video AI voiceover (带货视频配音)**: selling-point copy in, fast-paced voiceover WAV + big vertical SRT subtitles + per-line timing out.
- Make several hook variants per product for A/B tests; identical lines are reused, so edits only regenerate what changed.
- **Voice cloning** from 5–10 s for a store or host voice; 10 languages for TikTok Shop and cross-border e-commerce.
- `--preset daihuo` = tight 0.1 s gaps and 12-character subtitle cues for 9:16 video.
- Python 3.9+ stdlib, no GPU, `--dry-run` offline; TTS by the Miragea API. Works with Claude Code, Codex, OpenClaw, Cursor, WorkBuddy.

**关键词**：带货视频配音、带货配音、短视频带货、电商配音、种草视频配音、商品视频配音、卖点文案、AI配音、声音克隆、文字转语音、TTS、竖屏字幕、TikTok Shop、跨境电商配音、voiceover、product video、text to speech
