---
name: "ai-drama-dubbing"
description: "漫剧配音、AI短剧配音、动画配音、多人配音技能：把 AI 漫剧 / 竖屏短剧 / 动画短片 / 动态漫的剧本（`角色（情绪）：台词`）、分镜表（CSV/TSV：镜号、角色、台词、情绪、开始、时长）或带角色名的 SRT 字幕交给它，自动识别全部角色并生成选角表，每个角色用你自己克隆或保存的音色，逐句按情绪配音；有时间码时按画面时间对轨落位，并报告超出镜头时长的台词和建议语速。输出整段对白 dub.wav、每个角色一条等长分轨 stems/*.wav（方便单独调音量、加混响）、无角色名和带角色名两份 SRT 字幕、逐句时间表 cues.csv，可直接导入剪映 / CapCut / Premiere。改一句只重配一句，`--retake` 单句重录。配音调用 Miragea 开放 API（需要 API Key 和已克隆音色），本地只需 Python 3.9+ 标准库、无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。AI comic drama dubbing, short drama dubbing, anime dubbing, multi-speaker voiceover, per-role stems, SRT."
version: "1.1.0"
display_name: "漫剧配音｜AI短剧配音·动画配音·多人配音"
display_name_en: "AI Comic and Short Drama Dubbing · Multi-Voice · Stems + SRT"
description_zh: "漫剧配音：AI漫剧、短剧、动画的剧本、分镜表或SRT字幕按角色分配克隆音色，逐句带情绪配音并按时间码对轨，输出整段配音、角色分轨WAV和SRT字幕，超时台词自动提示，本地无需显卡。"
description_en: "AI comic-drama, short-drama and animation dubbing: give every role its own cloned voice, voice each line with an emotion, lock lines to storyboard or SRT time codes, and get the full dialogue track, one WAV stem per role, SRT subtitles and an overrun report. No GPU."
metadata:
  version: "1.1.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["漫剧配音", "AI漫剧配音", "短剧配音", "AI短剧配音", "动画配音", "动漫配音", "多人配音", "多角色配音", "情绪配音", "声音克隆", "分镜配音", "字幕对轨", "角色分轨", "AI漫剧", "AI短剧", "动态漫配音", "剪映配音", "SRT字幕", "comic drama dubbing", "short drama dubbing", "anime dubbing", "multi-speaker TTS", "voice cloning"]
---

# 漫剧配音

「漫剧配音」是一个给 AI 漫剧、竖屏短剧和动画短片做多角色对白配音的 Agent 技能：按剧本、分镜表或 SRT 识别角色，每个角色用你克隆的音色、逐句按情绪配音，可按时间码对轨，输出整段配音、角色分轨和 SRT 字幕，本地无需显卡。

## 一句话定义

漫剧配音 = 剧本 / 分镜表 / SRT → `drama_dub.py cast` 生成选角表（每个角色填一个你克隆的音色）→ `drama_dub.py build` 逐句带情绪配音 → `dub.wav`（整段对白）+ `stems/`（每个角色一条等长分轨）+ `dub.srt` / `dub_roles.srt` + `cues.csv` + `report.md`。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| AI 漫剧 / 动态漫工作室 | 一集几十句对白、五六个角色，画面已按分镜出好，需要按镜头时间把配音落进去 |
| 竖屏短剧团队 | 真人或 AI 仿真人短剧补录、改台词、出小样；同一角色全剧固定一个声音 |
| 动画短片 / 定格动画作者 | 角色对白 + 旁白，按 SRT 时间轴配到画面上 |
| 小说改漫剧的编剧 | 剧本写完先听一遍角色对手戏，找出拗口、过长的台词 |
| 剪辑师 / 后期 | 拿到每个角色单独的分轨，在剪映 / Premiere 里分别调音量、加混响、做电话音 |
| 不方便请多位配音员的个人创作者 | 把自己或已授权的几种声音克隆好，分给不同角色 |

和本系列其他技能的分工：小说推文配音以旁白讲故事为主、按句顺排；电影解说配音是解说旁白 + 少量原片台词；AI 播客是一到两位主持人的长对谈。**漫剧配音面向对白驱动的剧情短片**：多角色对手戏、逐句情绪、按分镜或字幕时间码对轨、按角色分轨交付。

## 能力一览

| 项目 | 说明 |
|---|---|
| 输入 | ① 剧本 `.md/.txt`：`角色（情绪）：台词`、`[角色\|情绪] 台词`、`旁白：……`，`=== 镜1 ===` / `## 第1场` 分镜，`[pause 0.5]` 停顿，行首 `@00:12.5` 锁定时间；② 分镜表 `.csv/.tsv`：自动识别 镜号 / 角色 / 台词 / 情绪 / 开始 / 时长 / 语速 列；③ 字幕 `.srt`：每条 `角色：台词`，按字幕开始时间落位 |
| 角色识别 | `drama_dub.py cast` 列出全部角色、句数、字数和用到的情绪，生成 `cast.md` 选角表；没标角色的行归为「旁白」 |
| 音色 | 每个角色一个账号角色：`voice=角色名称` 或 `actor_id=角色ID`（可用本人授权录音 `create-actor` 创建）；`speed=` 0.25–4 |
| 逐句情绪 | 台词里的（愤怒）（低语）等会从朗读文本中去掉，并作为语气标签随这一句提交；标签名须是 `capabilities` 里所选模式 `tags[].label` 的原文，用 `@emotions: 愤怒=标签名` 映射 |
| 时间轴 | 无时间码：按 `--gap`（句间）和 `--shot-gap`（换镜）顺排；有时间码：对轨落位，前一句没说完会把后一句顺延并记录；`--allow-overlap` 允许抢话重叠 |
| 超时检查 | 对轨模式下，每句实际时长和可用时长（下一句开始前 / 分镜时长 / 字幕时长）比较，`report.md` 列出超时句和建议语速；`--fit` 按建议语速自动重配一次 |
| 输出 | `dub.wav`、`stems/NN_角色.wav`（与整段等长，可直接叠轨）、`dub.srt`（无角色名，成片用）、`dub_roles.srt`（带角色名，审片用）、`cues.csv`（镜号、角色、情绪、起止、超时、顺延）、`manifest.json`、`report.md`、`lines/` 每句缓存 |
| 改稿 | 每句按内容和音色缓存，改哪句只重配哪句；`--retake 3,7` 让第 3、7 句重新生成一版 |
| 本地依赖 | Python 3.9+ 标准库，无需 pip、无需显卡；`--dry-run` 不需要 Key、不调用接口，用不同音高的提示音占位、按估算时长跑通全流程 |

## 快速开始

配音调用 Miragea 开放 API：需要一个 API Key，以及你在 https://miragea.ai 用本人录音克隆、保存为账号角色的音色（`actors` 列出账号里的角色和 `actor_id`；用 `actor_id` 时音色由服务端读取）。Key 在 https://miragea.ai/workspace/api 生成，只放在环境变量里，不要贴进聊天或写进文件。

```bash
python3 scripts/voiceover.py check                         # 离线检查 Python、Key、服务地址
python3 scripts/drama_dub.py check examples/example.md     # 看每一句被识别成哪个角色、什么情绪
python3 scripts/drama_dub.py build examples/example.md -o out --dry-run   # 不用 Key，离线跑通

export MIRAGEA_API_KEY=你的key
python3 scripts/miragea_audio.py actors --limit 50         # 找到你克隆的角色名称和 actor_id（has_more 为真时加 --offset 翻页）
python3 scripts/miragea_audio.py create-actor --file 我的录音.wav --name 我的声音 --language zh   # 还没有角色：用本人或已获授权的录音创建私有角色（按账号规则计费）
python3 scripts/miragea_audio.py capabilities              # 当前模式、可用语气标签 tags[].label、单句字数上限，以实时返回为准
python3 scripts/drama_dub.py cast 第1集.md -o cast.md        # 生成选角表，填入每个角色的 voice=角色名称 或 actor_id
python3 scripts/drama_dub.py build 第1集.md --cast cast.md -o ep01
```

Default API root is `https://miragea.ai/v1`; set `MIRAGEA_BASE_URL` (including `/v1`) only for a private deployment.

- 接口只按账号里的角色配音（官方客户端 1.3.0）：稿件里给每个角色写 `voice=角色名称` 或 `actor_id=角色ID`，也可以命令行加 `--voice 角色名称` 统一指定。旧版用音频链接直接克隆的写法服务端已停用，旧稿件改成角色写法即可。

## 选用你自己克隆的音色

1. 用本人（或已获书面授权的人）的干净录音创建账号角色：在网站完成声音克隆，或运行上面的 `create-actor`。
2. `python3 scripts/miragea_audio.py actors --limit 50` 列出账号里的角色（`actor_id`、`name`、`language`），按名称找到你的克隆音色，记下名称或 `actor_id`。
3. 先单句试听，确认音色和语速：

```bash
python3 scripts/miragea_audio.py generate --text '三年了，你一句解释都没有？' --actor-name 林夏的声音 --wait --output test_linxia.mp3
```

4. 把 `voice=角色名称` 或 `actor_id=` 填进 `cast.md` 对应角色那一行。同一个克隆音色可以用不同 `speed=`、不同语气标签分给两个次要角色，但主角之间最好用不同的音色。
5. 还没有角色、只有一段授权录音时，先 `create-actor --file 录音.wav --name 角色名称` 建成账号角色再用；全剧固定用同一个角色，声音更稳定。

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “给这集漫剧配音” | `cast` 出选角表 → 你确认每个角色用哪个音色 → `build` |
| “这是分镜表 / 字幕文件” | 直接 `build 分镜.csv` 或 `build 字幕.srt`，按时间码对轨 |
| “我只有小说片段” | Agent 先改成 `角色（情绪）：台词` 的剧本给你确认（改编由 Agent 完成），再配音 |
| “女主声音用我克隆的那个” | `actors` 查到角色名称，`voice=角色名称` 填进 cast.md 的女主那一行 |
| “这句太长，画面已经切走了” | 看 `report.md` 的建议语速：删减台词，或给这句写 `语速`，或 `--fit` 自动重配 |
| “第 7 句情绪不对，再来一条” | 改情绪标注后重跑；只想换一版就 `--retake 7` |
| “给我每个角色单独的音轨” | 用 `stems/` 里的文件，和 `dub.wav` 等长，导入后直接对齐 |
| “字幕不要角色名” | 成片用 `dub.srt`；审片用 `dub_roles.srt` |
| “先别调用接口” | `build ... --dry-run` |

## 漫剧配音方法

### 1. 先定选角表，再写情绪

- 每个主要角色一个音色，主角之间的音色、语速要拉开；龙套可以共用音色但换 `speed=`。
- 旁白（画外音）单独一个音色，语速比角色略慢，`speed=0.95` 左右。
- 选角表定下来后整部剧不换，观众靠声音认人。

### 2. 台词写给耳朵听

| 剧本里 | 配音稿里 |
|---|---|
| 长句、书面语 | 拆短，一行一句，口语化 |
| “……”“！！！” | 用（情绪）和 `[pause 0.4]` 表达，不靠标点堆 |
| 人名、生僻字、多音字 | 先单句试听，读错就改写成同音字或换说法 |
| 内心独白 | 写成 `林夏（低语）：……` 或单独建一个「林夏OS」角色用不同语速 |

### 3. 情绪标注要克制

- 一句只标一个最主要的情绪；连续几句同一情绪时只在第一句标，后面靠台词本身。
- 标签必须来自 `capabilities` 的 `tags[].label`。剧本里习惯写的词（如“冷笑”）和账号里的标签名不同时，在选角表里写 `@emotions: 冷笑=实际标签名`。
- 账号当前模式没有合适的标签时，`--no-emotion` 只去掉括号、不传标签，靠语速和停顿表现。

### 4. 对轨：配音时长服从镜头

- 分镜表里写清每镜的“开始”和“时长”，或者直接用剪辑软件导出的 SRT。
- 生成后先看 `report.md`：超时句优先删字，其次调语速；建议语速高于 1.3 时听感会赶。
- 抢话、争吵可用 `--allow-overlap` 保留原时间码，让两句局部重叠。

### 5. 交付前检查

- [ ] `check` 里每句的角色和情绪都识别对了吗？
- [ ] 每个角色都单句试听过音色和语速吗？
- [ ] `report.md` 里没有未处理的超时句了吗？
- [ ] 用到的每个克隆音色都有本人授权吗？成片是否按平台要求标注了 AI 生成？

## 示例剧本（examples/example.md）

```markdown
---
旁白: actor_id=NARRATOR_VOICE_ID speed=0.95
林夏: actor_id=YOUR_CLONED_VOICE_ID speed=1.05
顾沉: actor_id=ANOTHER_CLONED_VOICE_ID speed=0.95
@emotions: 愤怒=TAG_LABEL_ANGRY, 冷笑=TAG_LABEL_COLD, 低语=TAG_LABEL_WHISPER
---
=== 镜1 | 雨夜·门口 ===
旁白：退婚那天，下了一整夜的雨。
林夏（愤怒）：三年了，你一句解释都没有？
顾沉（冷笑）：解释？你配听吗。
=== 镜2 | 特写 ===
[pause 0.5]
林夏（低语）：好，那我们……到此为止。
旁白：她不知道，这一转身，就是十年。
```

同目录还有 `examples/storyboard.csv`（分镜表，带开始时间和时长）和 `examples/dialogue_srt.txt`（带角色名的 SRT 字幕，存成 .txt），三种输入都可以直接 `--dry-run` 试跑。

## --dry-run 示例输出

```text
$ python3 scripts/drama_dub.py build examples/example.md -o out --dry-run
wrote out/dub.wav (12.7s, 5 lines, 3 roles, sequential) + stems/ + dub.srt + dub_roles.srt + cues.csv + report.md  [dry-run: placeholder tones, no API call]

$ python3 scripts/drama_dub.py build examples/storyboard.csv -o out2 --dry-run
wrote out2/dub.wav (10.3s, 4 lines, 3 roles, locked) + stems/ + dub.srt + dub_roles.srt + cues.csv + report.md  [dry-run: placeholder tones, no API call]
```

占位音按角色区分音高，时长按字数估算，只用来检查解析、选角、对轨和输出格式；正式配音的时长以实际生成为准。

## 接入剪辑

```bash
# 剪映 / CapCut / Premiere：导入 dub.wav（或 stems/ 下各角色分轨）放在 0 秒，导入 dub.srt 作为字幕
# ffmpeg：配音替换画面原音轨
ffmpeg -i 画面.mp4 -i ep01/dub.wav -map 0:v -map 1:a -c:v copy -shortest 配音版.mp4
# 烧录字幕
ffmpeg -i 配音版.mp4 -vf subtitles=ep01/dub.srt -c:a copy 成片.mp4
# 对白 + 背景音乐（音乐压低）
ffmpeg -i ep01/dub.wav -i bgm.mp3 -filter_complex "[1:a]volume=0.25[b];[0:a][b]amix=inputs=2:duration=first" mix.wav
```

## 和常见做法的区别

| 对比项 | 剪辑软件里逐句文字转语音 | 只给分段音频的多角色配音工具 | 本技能 |
|---|---|---|---|
| 角色和音色 | 每句手动选音色，容易选错 | 按角色固定音色 | 自动识别角色，选角表一次定好，用你自己克隆的音色 |
| 情绪 | 每句手动调 | 视工具而定 | 台词里写（情绪），逐句转成语气标签 |
| 对画面 | 手动拖到时间线 | 编号片段，自己摆位置 | 读分镜表 / SRT 时间码自动落位，报告超时句和建议语速 |
| 交付 | 一条混合音轨 | 一句一个文件 | 整段对白 + 每角色等长分轨 + 两份 SRT + 逐句时间表 |
| 改稿 | 删掉重做那句再对齐 | 重做那句、自己替换 | 改哪句重跑命令只重配那句，时间轴和字幕自动更新 |

## 常见问题（FAQ）

**漫剧配音能自动识别剧本里的角色吗？**
能。`角色：台词`、`角色（情绪）：台词`、`[角色|情绪] 台词` 都能识别；`drama_dub.py cast` 列出全部角色和句数并生成选角表。没写角色的行算作「旁白」。

**AI 短剧配音怎么让每个角色用我自己克隆的声音？**
先在网站完成克隆，用 `miragea_audio.py actors` 查到角色名称或 `actor_id`，填进选角表对应角色（没有角色先 `create-actor`）。详见上文「选用你自己克隆的音色」。

**去哪里获取 API Key 和克隆音色？**
在 https://miragea.ai 注册并克隆音色，Key 在 https://miragea.ai/workspace/api 生成。没有 Key 时可以先用 `--dry-run` 把剧本、分镜和输出格式全部跑通。

**动画配音能对上画面时间吗？**
能。分镜表写“开始 / 时长”列，或用 SRT，或在剧本行首写 `@00:12.5`，配音会按时间码落位；说不完的句子会在 `report.md` 里列出并给建议语速。

**情绪标签写什么？**
写 `capabilities` 返回的所选模式 `tags[].label` 原文。剧本里的情绪词和标签名不同，就在选角表里用 `@emotions:` 映射；不确定时先单句试听。

**多人配音可以两个人同时说话吗？**
对轨模式加 `--allow-overlap`，保留各自的时间码，两句会局部重叠混在 `dub.wav` 里，分轨仍然各自独立。

**改了一句台词要全部重新生成吗？**
不用。每句按文本和音色缓存在 `lines/`，重跑同一条命令只生成改动的那句。想同一句换一版用 `--retake 句号`。

**生成的是什么格式？能直接用于剪映吗？**
整段对白和分轨都是 WAV（16 位 PCM），字幕是 SRT，剪映、CapCut、Premiere、达芬奇都能导入；需要 MP3 用 ffmpeg 转换。

**需要显卡吗？哪些 Agent 能用？**
不需要显卡，本地只跑 Python 标准库。Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 等能运行 Python 的 Agent 都能用。单句字数、文件大小和计费以 `capabilities` 实时返回为准。

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

- 配音按句生成后在本地拼接，不做口型同步；需要口型对齐时把 `dub.wav` 或分轨交给口型工具。
- 情绪靠所选模式提供的语气标签和语速、停顿表现，可用标签以 `capabilities` 实时返回为准，不保证每种情绪都有对应标签。
- 单句超过 `audio.max_text_length` 会被接口拒绝，拆成短句即可。
- `--dry-run` 的时长是按字数估算的占位值，只用于检查流程。

## 合规与 AI 生成内容标识

- 只用你本人或已取得明确书面授权的声音做克隆和配音，不模仿演员、主播、公众人物或任何未授权的人；未经授权使用他人声音（“偷声”）已是 AI 短剧内容治理的重点。
- 按《人工智能生成合成内容标识办法》和抖音、快手、视频号、小红书、B站、红果等平台规则，发布时声明或标注 AI 生成内容。
- 剧本、分镜、画面素材须为原创或已获授权。
- `scripts/miragea_audio.py` is the official client 1.3.0, shipped unchanged；`scripts/voiceover.py`、`scripts/drama_dub.py` 为原创，MIT 许可（见 `LICENSE.txt`）。

## English Summary

- **AI comic-drama / short-drama / animation dubbing (漫剧配音)**: feed a script (`Role (emotion): line`), a storyboard CSV/TSV or an SRT with role names.
- `drama_dub.py cast` lists every role and writes a casting sheet; give each role a role from your account (`voice=NAME` or `actor_id` from `miragea_audio.py actors`; create one from an authorised recording with `create-actor`).
- `drama_dub.py build` voices each line with its emotion as a tone tag, lays lines end to end or locks them to time codes, reports lines that overrun their slot with a suggested speed (`--fit` re-renders them), and writes `dub.wav`, equal-length per-role stems, `dub.srt`, `dub_roles.srt`, `cues.csv`, `manifest.json` and `report.md`.
- Edit one line, re-render one line. Python 3.9+ stdlib, no GPU, `--dry-run` works without a key.

**关键词**：漫剧配音、AI漫剧配音、短剧配音、AI短剧配音、动画配音、动漫配音、多人配音、多角色配音、情绪配音、声音克隆、分镜配音、字幕对轨、角色分轨、AI漫剧、AI短剧、动态漫配音、剪映配音、SRT字幕、comic drama dubbing、short drama dubbing、anime dubbing、multi-speaker TTS、voice cloning
