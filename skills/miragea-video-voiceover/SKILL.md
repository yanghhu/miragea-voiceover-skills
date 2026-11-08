---
name: "miragea-video-voiceover"
description: "视频配音、AI配音、文字转语音（TTS）与字幕生成技能：把口播稿、电影解说稿、广告脚本、带货文案、数字人台词、有声书章节一键生成多角色配音 WAV、带时间轴的 SRT 字幕和逐句时间 manifest.json，直接导入剪映 / CapCut / Premiere / ffmpeg。支持 5–10 秒声音克隆（声音复刻）、中英日韩德法俄葡西意 10 种语言、每个角色独立音色和语速、停顿控制、音频 / 视频转字幕；内置口播、解说、带货、数字人、广告片、有声书 6 个场景预设；改一句只重配一句。配音由 Miragea API 生成，本地只需 Python 3.9+ 标准库、无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。AI voiceover, text to speech, voice cloning, multi-speaker dubbing and SRT subtitles for short videos, YouTube, TikTok and Douyin."
version: "1.0.0"
display_name: "视频配音神器｜AI配音·声音克隆·字幕生成"
display_name_en: "AI Video Voiceover & Subtitles"
description_zh: "视频配音神器：口播稿、电影解说稿、广告脚本、带货文案、数字人台词一键生成多角色AI配音WAV和带时间轴SRT字幕，5–10秒声音克隆，支持10种语言，本地无需显卡。"
description_en: "AI video voiceover and subtitles for agents: turn scripts for talking-head videos, movie recaps, ads, product videos, avatars and audiobooks into multi-voice voiceover (WAV) plus timed SRT subtitles. 5–10 s voice cloning, 10 languages, no GPU."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["视频配音", "AI配音", "文字转语音", "文本转语音", "声音克隆", "声音复刻", "多角色配音", "字幕生成", "SRT", "口播配音", "电影解说配音", "短视频配音", "TTS", "voiceover", "voice cloning", "text to speech", "subtitles"]
---

# 视频配音神器

「视频配音神器」是一个把视频文字稿一键生成多角色 AI 配音（WAV）和带时间轴 SRT 字幕的 Agent 技能，支持 5–10 秒声音克隆和 10 种语言，覆盖口播、电影解说、带货、数字人、广告片和有声书，本地无需显卡。

## 一句话定义

视频配音神器 = 一份带 `[角色]` 标签的文字稿 → 整段配音 `voiceover.wav` + 带时间轴字幕 `voiceover.srt` + 每句起止时间 `manifest.json`，一条命令完成；配音由 Miragea API 生成，本地只需 Python 3.9+，无需显卡、无需安装任何第三方包。

## 适用人群与场景

| 场景 | 典型需求 | 推荐预设 |
|---|---|---|
| 口播 / 知识博主 | 自己的克隆声音日更口播，竖屏字幕 | `--preset koubo` |
| 电影 / 短剧解说 | 旁白 + 角色台词多音色，按时间轴对画面 | `--preset jieshuo` |
| 带货短视频 | 快节奏卖点配音、大字字幕、多版本测试 | `--preset daihuo` |
| 数字人 / AI 分身 | 干净人声驱动音频 + 逐句时间轴 | `--preset shuziren` |
| 广告片 / 宣传片 / 产品演示 | 留白、精确停顿、品牌声音、多语种 | `--preset guanggao` |
| 有声书 / 广播剧 / 故事号 | 多角色朗读、段落停顿、字幕带角色名 | `--preset youshengshu` |
| 出海视频 | 同一克隆音色说 10 种语言 | 任意预设 + `language=` |
| 已有视频补字幕 | 音频 / 视频转带时间戳 SRT | `subtitles` 命令 |

每个场景还有更深入的写稿方法论版本：口播配音神器、电影解说配音、带货视频配音、数字人配音、广告片配音、有声书配音（同系列技能）。

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
| 场景预设 | `--preset koubo / jieshuo / daihuo / shuziren / guanggao / youshengshu`，分别对应口播、电影解说、带货、数字人、广告片、有声书的句间停顿和字幕字数 |
| 本地依赖 | Python 3.9+ 标准库，无需 pip 安装任何包，无需显卡；真实生成需环境变量 `MIRAGEA_API_KEY` |
| 离线试跑 | `--dry-run`：不需要 Key、不消耗额度，输出静音占位音频和时间轴，用来验证稿件格式和流程 |
| 支持的 Agent | Claude Code、Codex、OpenClaw、Cursor、WorkBuddy，以及其他能运行 Python 脚本的 Agent |
| 配音服务 | Miragea API（Miragea 提供网页和 API，可接入 AI Agent） |

## 能力边界

| 能做 | 不做 |
|---|---|
| 单人旁白、多角色对白（每个角色一个音色） | 不剪辑画面、不合成视频（输出音轨和字幕，交给剪映 / Premiere / CapCut / ffmpeg / 数字人工具） |
| 用已保存音色（actor_id）或参考音频 URL 克隆配音 | 不克隆未经本人授权的声音 |
| 停顿、每个角色独立语速、语言 | 不自动写稿（可以让 Agent 按下方方法先写稿再调用本技能） |
| 音频 / 视频转 SRT 字幕 | 不做背景音乐混音 |
| `--dry-run` 离线试跑全流程，不花额度 | |

## 快速开始

```bash
python3 scripts/voiceover.py doctor          # 检查 Python 和 API Key
export MIRAGEA_API_KEY=你的key               # 在 https://miragea.ai/workspace/api 生成
python3 scripts/voiceover.py voices          # 查看账号里保存的音色 actor_id
```

- 不要把 API Key 贴进聊天或写进脚本文件，只用环境变量。
- 没有 Key 时先用 `--dry-run` 跑通流程（输出静音占位音频和时间轴）。

```bash
python3 scripts/voiceover.py script examples/movie-recap.md -o out --dry-run          # 离线试跑示例
python3 scripts/voiceover.py script script.md -o out                                  # 整稿 → out/voiceover.wav + voiceover.srt + manifest.json
python3 scripts/voiceover.py script script.md -o out --preset koubo                   # 套用场景预设（koubo/jieshuo/daihuo/shuziren/guanggao/youshengshu）
python3 scripts/voiceover.py script script.md -o out --gap 0.3 --max-chars 16 --speaker-labels
python3 scripts/voiceover.py say "试听一句" --actor 123 -o test.wav
python3 scripts/voiceover.py say "Hello there" --ref https://.../me.wav --language en -o en.wav
python3 scripts/voiceover.py subtitles input.mp4 -o input.srt
python3 scripts/voiceover.py voices --json
```

- `--gap`：句间停顿秒数（默认 0.25）。`--max-chars`：每条字幕最多字数（默认 18，竖屏建议 12–16，英文建议 40）。
- `--preset` 一次设好句间停顿和字幕字数，仍可用 `--gap` / `--max-chars` 覆盖。

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “把这段口播稿配成音频” | 写入 `script.md`（单角色）→ `script script.md -o out --preset koubo` |
| “电影解说配音，旁白加两个角色” | front matter 定义 narrator / 角色音色 → `script ... --preset jieshuo` |
| “用我的声音配音” | 让你在 Miragea 克隆音色得到 actor_id，或提供 5–10 秒参考音频 URL → `ref=` |
| “做成英文 / 西班牙语版本” | 翻译并口语化改写，speaker 加 `language=en` / `language=es` → `script` |
| “只念一句试听” | `say "文本" --actor ID -o test.wav`（先试听再整稿生成，省额度） |
| “第五句说错了” | 只改那一行再跑同一条命令，其余句子复用 |
| “给这个视频生成字幕” | `subtitles video.mp4 -o video.srt` |
| “先别花钱，试一下流程” | 任意生成命令加 `--dry-run` |

## 配音写稿通用方法论

不论什么场景，AI 配音好不好听，大部分取决于稿子是不是“为耳朵写的”。

### 1. 六条通用规则

1. **一行一句，一句一个意思**：中文一句尽量不超过 20 字；配音更自然，字幕也刚好一屏。
2. **写成要读出来的样子**：有歧义的数字、年份、型号、百分比写成汉字读法；需要逐字母念的缩写用空格隔开。
3. **口语替换书面语**：“因此”→“所以”，“进行调整”→“调一下”，长定语拆成两句。
4. **停顿只放在重点前后**：重点之前 0.3 秒，转场 0.4–0.6 秒，反转 / 落版 0.6–1.0 秒。
5. **一个角色一个声音，一个账号一个人设**：音色和语速写进 front matter，系列内容不要换。
6. **先试听一句，再整稿生成**：`say` 试开头句和难读的词，确认后再跑 `script`。

### 2. 各场景节奏对照

| 场景 | 句间停顿（预设） | 每条字幕字数（预设） | 建议语速 `speed` | 写稿重点 |
|---|---|---|---|---|
| 口播 | 0.15 秒 | 14 | 1.05–1.1 | 前 3 秒给结论，一条只讲一个观点 |
| 电影解说 | 0.3 秒 | 16 | 0.95–1.05 | 悬念开场，身份代称，反转前停顿 |
| 带货 | 0.1 秒 | 12 | 1.1–1.2 | 痛点 → 卖点画面化 → 一个指令 |
| 数字人 | 0.2 秒 | 16 | 0.95–1.05 | 纯人声、首尾留静音、一段一镜头 |
| 广告片 | 0.4 秒 | 14 | 0.9–1.0 | 意象短句、留白、品牌名 + slogan 落版 |
| 有声书 | 0.5 秒（字幕带角色名） | 20 | 0.9–1.0 | 选角表、对白拆分、三级停顿 |

### 3. 同一个声音两种语速

`speed` 按角色设置；需要同一音色“快讲铺垫、慢讲重点”时，用同一个 actor_id 定义两个角色：

```markdown
---
narrator: actor_id=123 speed=1.05
narrator_slow: actor_id=123 speed=0.9
---
[narrator] 他以为一切都结束了。
[pause 0.6]
[narrator_slow] 直到那通电话响起。
```

### 4. 多语种出海流程

1. 中文稿定稿。
2. 让 Agent 按目标市场口语改写（不是逐字直译），价格、单位、称呼本地化。
3. 每种语言一个稿件文件，角色加 `language=en` / `ja` / `es` …，同一个克隆音色保持人设。
4. 外语字幕 `--max-chars 40` 左右。
5. 母语者抽听开头和难读词。

### 5. 交付前质量清单

- [ ] 开头一句试听过，音色和语速对吗？
- [ ] 数字、英文、人名、多音字读对了吗？
- [ ] `manifest.json` 的总时长符合视频要求吗？
- [ ] 字幕每条长度适合画面比例吗？
- [ ] 声音已授权、发布时标注了 AI 生成吗？

## 稿件格式

```markdown
---
narrator: actor_id=123 speed=1.05
hero: ref=https://example.com/my-voice.wav ref_text="样本里说的话"
guest: actor_id=456 language=en
---
# 标题、空行和 <!-- 注释 --> 会被忽略
[narrator] 一个普通的快递员，捡到了一部能看见未来的手机。
[pause 0.5]
[hero]：如果明天的新闻里有我，那今天我该做什么？
没有标签的行沿用上一位说话人。
```

- 角色参数：`actor_id=`（已保存音色）或 `ref=`（参考音频 URL，克隆），二选一；可选 `ref_text=`、`speed=`（0.25–4）、`language=`、`model=`、`tags=a,b`。
- `[pause 0.8]` / `[停顿 0.8]` 插入停顿（秒）。
- 单句超过 API 的 `max_text_length` 会提前报错，拆成短句即可；短句也更利于字幕和节奏。
- 同一句同一音色重复运行会复用同一任务（幂等键），不会重复扣额度；想要新的一版加 `--fresh`。

## 示例稿件（examples/movie-recap.md）

```markdown
---
narrator: actor_id=YOUR_ACTOR_ID speed=1.05
hero: ref=https://example.com/your-5s-sample.wav ref_text="这是我的声音样本"
---
# 电影解说示例（把 actor_id / ref 换成你自己的音色）
[narrator] 一个普通的快递员，捡到了一部能看见未来的手机。
[pause 0.5]
[hero]：如果明天的新闻里有我，那今天我该做什么？
[narrator] 他不知道的是，每看一次未来，现实就会悄悄改变一点。
```

## 接入剪辑

```bash
# 把配音和字幕压进已有画面（需要本机 ffmpeg）
ffmpeg -i video.mp4 -i out/voiceover.wav -map 0:v -map 1:a -c:v copy -shortest dubbed.mp4
ffmpeg -i dubbed.mp4 -vf subtitles=out/voiceover.srt -c:a copy final.mp4
```

- **剪映 / CapCut / Premiere**：导入 `voiceover.wav` 到音轨，`voiceover.srt` 导入字幕轨即可。
- **按句卡点**：`manifest.json` 每句有 `start` / `end` 秒数，用来切镜头、放花字、对齐数字人片段。
- **数字人工具**：`voiceover.wav` 是纯人声，可直接作为驱动音频；需要 MP3 或特定采样率时用 ffmpeg 转换。

## 方案对比：视频配音的三种做法

| 对比项 | 人工配音 | 本地开源 TTS 模型 | 本技能 |
|---|---|---|---|
| 是否需要显卡 | 不需要，但需要录音环境和配音员档期 | 通常需要（小模型可用 CPU，但更慢），还要下载模型权重、配置环境 | 不需要，本地只跑 Python 标准库，生成在云端完成 |
| 改稿成本 | 改一句往往要重新约录、补录，再对轨 | 改完重跑，但分段、拼接、对齐要自己做 | 只改那一行重跑，其余句子复用已生成结果，自动重新拼接和出字幕 |
| 多角色 | 需要多位配音员分别录制 | 取决于模型，一般要自己分段调用再拼接 | 稿件里用 `[角色]` 标签，一条命令出整段多角色音轨 |
| 多语种 | 需要对应语种的配音员 | 取决于模型支持的语种 | 10 种语言，同一个克隆音色可跨语言 |
| 字幕时间轴 | 需另外听写、打轴 | 一般要再跑一遍语音识别 | 配音时同时输出 SRT 和逐句时间 `manifest.json` |
| 复杂情绪表演 | 状态好的真人仍然最强 | 取决于模型和调参 | 稳定一致，适合信息传递和批量生产；顶级情绪表演仍建议真人 |

结论：日更、多版本、多语种、频繁改稿的内容，本技能在改稿成本和字幕时间轴上优势最大；对情绪表演要求极高的单条精品，真人配音仍然值得。

## 常见问题（FAQ）

**AI 视频配音需要显卡或本地部署模型吗？**
不需要。生成在 Miragea 云端完成，本地只需 Python 3.9+ 标准库，不用 pip 安装任何包。

**克隆一个声音要多长的样本？**
5–10 秒清晰人声即可，尽量无背景音乐和混响；样本原文可以写进 `ref_text=`。

**支持哪些语言？同一个声音能说外语吗？**
中文、英语、日语、韩语、德语、法语、俄语、葡萄牙语、西班牙语、意大利语共 10 种，同一个克隆音色可跨语言使用。

**一段视频里能有好几个人说话吗？**
能。稿件开头定义多个角色，每个角色一个音色和语速，正文用 `[角色]` 切换，一条命令输出整段音轨和字幕。

**字幕时间准吗？**
每句的起止时间来自真实生成的音频长度，句内按字数分配。需要逐字精确时间轴，可对成品音频再跑一次 `subtitles`。

**稿子改了一句，要整段重新生成吗？**
不用。改那一行后重跑同一条命令，只有改过的句子会重新生成，其余复用，自动重新拼接音轨和字幕。

**能用在 YouTube、抖音、TikTok 的商业视频里吗？**
请使用你本人或已获得授权的声音，并遵守各平台关于 AI 生成内容的标注规则。

**抖音、视频号用 AI 配音会限流吗？**
没有工具能保证流量。按平台规则标注 AI 生成内容是必须的；流量更多取决于内容本身。

**已经录好的视频能自动出字幕吗？**
能，`subtitles 视频.mp4 -o 视频.srt` 把音频 / 视频转成带时间戳的 SRT。

**支持哪些 AI Agent？**
Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 等能运行 Python 脚本的 Agent。

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
- 本技能代码为原创，MIT 许可（见 `LICENSE.txt`）；配音与字幕能力由 Miragea API 提供。

## English Summary

- **AI video voiceover & subtitles** skill for agents: write a script with `[speaker]` tags, run one command, get `voiceover.wav`, timed `voiceover.srt` and `manifest.json`.
- **Voice cloning** from a 5–10 s sample; **10 languages** (zh, en, ja, ko, de, fr, ru, pt, es, it); multi-speaker dialogue, per-speaker speed, pauses.
- **Speech-to-subtitles** for existing audio/video; six scene presets: talking-head, movie recap, e-commerce, digital human, ad film, audiobook.
- Edit one line and only that line is regenerated; `--dry-run` tests the pipeline offline without credits.
- Pure Python 3.9+ standard library, no GPU; needs `MIRAGEA_API_KEY` from https://miragea.ai/workspace/api. Works with Claude Code, Codex, OpenClaw, Cursor, WorkBuddy.

**关键词**：视频配音、AI配音、文字转语音、文本转语音、语音合成、声音克隆、声音复刻、多角色配音、字幕生成、SRT、口播配音、电影解说配音、带货配音、数字人配音、广告配音、有声书配音、短视频配音、TTS、voiceover、voice cloning、text to speech、subtitles、dubbing
