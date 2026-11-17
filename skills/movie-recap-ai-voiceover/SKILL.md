---
name: "movie-recap-ai-voiceover"
description: "电影解说配音、短剧解说配音、影视解说配音技能：把解说稿（Markdown / TXT，可带时间码）、分镜表（CSV/TSV：镜号、画面、开始、时长、角色、文案、语气）或 SRT 字幕交给它，解说旁白和角色台词各用你自己克隆或保存的音色，逐句按语气配音；有时间码时按画面时长对轨落位，报告超出画面的句子、建议语速和要删的字数，`--fit` 可自动重配。输出整段 voiceover.wav、旁白分轨 stems/narration.wav 和台词分轨 stems/dialogue.wav（另有每个角色单独音轨）、无角色名和带角色名两份 SRT 字幕、逐句计划表 cues.csv 和 report.md，可直接导入剪映 / CapCut / Premiere。改一句只重配一句，`--retake` 单句重录；内置 selftest 离线自检。配音调用 Miragea 开放 API（需要 API Key 和已克隆音色），本地只需 Python 3.9+ 标准库、无需显卡，无 Key 时 --dry-run 可完整跑通。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。Movie recap voiceover, narration and dialogue stems, voice cloning, SRT subtitles."
version: "1.1.0"
display_name: "电影解说配音｜短剧解说·影视解说·AI配音"
display_name_en: "Movie Recap Voiceover · Narration + Dialogue Stems · SRT"
description_zh: "电影解说配音：解说稿、分镜表或SRT字幕一键配音，旁白和角色台词用不同克隆音色分轨输出，按画面时长对轨提示超时句，逐句语气可调，改一句只重配一句，输出WAV和SRT字幕，无需显卡。"
description_en: "Movie / TV / short-drama recap voiceover: script, shot list or SRT in; narrator and character lines in your own cloned voices, locked to picture time codes with an overrun report, separate narration and dialogue stems, SRT subtitles, edit one line re-render one line. No GPU."
metadata:
  version: "1.1.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["电影解说配音", "解说配音", "短剧解说", "影视解说", "短剧解说配音", "影视解说配音", "电影解说", "AI配音", "旁白配音", "多角色配音", "声音克隆", "字幕对轨", "分镜配音", "画面对轨", "剪映配音", "SRT字幕", "文字转语音", "movie recap", "recap voiceover", "voiceover", "narration", "voice cloning"]
---

# 电影解说配音

「电影解说配音」是一个给电影、电视剧、短剧和动漫解说号做配音的 Agent 技能：解说稿、分镜表或 SRT 字幕进，解说旁白和角色台词各用你克隆的音色逐句配音，按画面时长对轨并提示超时句，输出整段配音、旁白 / 台词分轨、SRT 字幕和逐句计划表，本地无需显卡。

## 沙箱 / 离线快速验证（不需要 API Key，不联网）

解压后在技能目录里依次运行，每条命令都能直接跑通（只用 Python 3.9+ 标准库）：

```bash
python3 scripts/recap_dub.py selftest                                         # 内置自检：解析、对轨、超时报告、分轨、无 Key 拦截、全部示例
python3 scripts/recap_dub.py check examples/example.md                        # 逐句看识别成旁白还是台词、什么语气、预计时长
python3 scripts/recap_dub.py build examples/example.md -o out --dry-run       # 解说稿 → 整段配音 + 分轨 + SRT + 计划表
python3 scripts/recap_dub.py build examples/timed_script.txt -o out_timed --dry-run   # 带时间码的稿件：按画面对轨，报告超时句
python3 scripts/recap_dub.py build examples/storyboard.csv -o out_board --dry-run     # 分镜表输入
python3 scripts/recap_dub.py build examples/sample_srt.txt -o out_srt --dry-run       # SRT 字幕输入（.srt 或存成 .txt 都行）
python3 scripts/recap_dub.py cast examples/storyboard.csv                     # 列出说话人，打印待填写的音色表
python3 scripts/voiceover.py check                                            # 环境检查：Python、Key 是否已设置、服务地址
```

实际输出（`--dry-run` 用占位提示音、按每秒约 4.5 字估算时长，不调用接口）：

```text
$ python3 scripts/recap_dub.py selftest
PASS  解析解说稿：3 句、旁白/台词分轨、语气、时间码
...
selftest 通过：16/16 通过（未使用 API Key，未联网）

$ python3 scripts/recap_dub.py build examples/example.md -o out --dry-run
完成：out/voiceover.wav（39.2 秒，9 句，顺排）+ stems/narration.wav + stems/dialogue.wav + voiceover.srt + cues.csv + report.md  [dry-run：占位音，未调用接口]

$ python3 scripts/recap_dub.py build examples/timed_script.txt -o out_timed --dry-run
完成：out_timed/voiceover.wav（33.4 秒，6 句，对轨）+ stems/narration.wav + stems/dialogue.wav + voiceover.srt + cues.csv + report.md  | 1 句超出画面时长，见 report.md  [dry-run：占位音，未调用接口]
```

每个输出目录里有：

| 文件 | 内容 |
|---|---|
| `voiceover.wav` | 整段配音（旁白 + 台词） |
| `stems/narration.wav` / `stems/dialogue.wav` | 解说旁白分轨 / 角色台词分轨，和整段等长，叠在一起就是 `voiceover.wav` |
| `stems/roles/NN_说话人.wav` | 每个说话人单独一轨 |
| `voiceover.srt` / `voiceover_roles.srt` | 成片字幕（无名字）/ 审片字幕（带说话人） |
| `cues.csv` | 逐句计划表：镜号、画面、说话人、分轨、语气、文案、开始、结束、时长、画面可用时长、超出秒数、被顺延秒数 |
| `report.md` | 时长统计、超出画面的句子（建议语速、或删约几字）、画面空着较久的位置、被顺延的句子 |
| `manifest.json` | 以上全部数据，方便 Agent 继续处理 |
| `lines/` | 每句音频缓存（正式生成时），改一句只重配一句 |

没有 Key 时去掉 `--dry-run`：脚本在调用任何接口之前就停下，打印中文提示并以退出码 2 结束；示例稿里的 `NARRATOR_VOICE_ID` 之类占位符也会被拦下，不会发出请求。

## 快速开始（正式配音）

配音调用 Miragea 开放 API，需要 API Key 和你在 https://miragea.ai 用本人录音克隆、保存为账号角色的音色。Key 只放在环境变量里，不要贴进聊天或写进文件。

```bash
export MIRAGEA_API_KEY=你的key
python3 scripts/miragea_audio.py actors --limit 50          # 找到你克隆的角色名称和 actor_id（has_more 为真时加 --offset 翻页）
python3 scripts/miragea_audio.py create-actor --file 我的录音.wav --name 我的声音 --language zh   # 还没有角色：用本人或已获授权的录音创建私有角色（按账号规则计费）
python3 scripts/miragea_audio.py capabilities               # 当前模式、可用语气标签 tags[].label、单句字数上限，以实时返回为准
python3 scripts/recap_dub.py cast 第1期.md -o cast.md        # 生成音色表，填入旁白和每个角色的 actor_id
python3 scripts/recap_dub.py build 第1期.md --cast cast.md -o ep01
```

Default API root is `https://miragea.ai/v1`; set `MIRAGEA_BASE_URL` (including `/v1`) only for a private deployment.

- 接口只按账号里的角色配音（官方客户端 1.3.0）：稿件里给每个角色写 `voice=角色名称` 或 `actor_id=角色ID`，也可以命令行加 `--voice 角色名称` 统一指定。旧版用音频链接直接克隆的写法服务端已停用，旧稿件改成角色写法即可。

## 选用你自己克隆的音色

1. 用本人（或已获书面授权的配音员）的干净录音创建账号角色：在网站完成声音克隆，或运行上面的 `create-actor`。
2. `python3 scripts/miragea_audio.py actors --limit 50` 列出账号角色（`actor_id`、`name`、`language`），找到你的解说声线，记下名称或 `actor_id`。
3. 单句试听，确认音色和语速（`--output` 不会覆盖已有文件，每次换个新文件名）：

```bash
python3 scripts/miragea_audio.py generate --text '他捡到的这部手机，只会显示明天的新闻。' --actor-name 我的声音 --wait --output test_narrator.mp3
```

4. 把 `voice=角色名称` 或 `actor_id=` 填进 `cast.md` 的「旁白」行；整季所有稿件都用同一个旁白音色和 `speed`，观众靠声音认号。
5. 同一个音色可以配两个名字：`旁白: actor_id=ID speed=1.05` 快讲铺垫，`旁白慢: actor_id=ID speed=0.9` 慢讲反转，两者都进旁白分轨。
6. 角色台词的音色要和旁白拉开（性别、年龄、语速），只用你自有或已授权的音色，不要模仿原片演员。

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “帮我把这篇电影解说稿配成音频” | `check` 看分句 → `cast` 出音色表 → 你确认音色 → `build 稿件.md --cast cast.md -o out` |
| “这是剪好的粗剪字幕 / 分镜表” | 直接 `build 字幕.srt` 或 `build 分镜.csv`，按时间码对轨 |
| “解说和台词分开给我” | 用 `stems/narration.wav` 和 `stems/dialogue.wav`，与整段等长，导入后放在 0 秒即对齐 |
| “这句太长，画面已经切走了” | 看 `report.md` 的建议语速和“或删约几字”，先删字；或 `--fit` 自动重配 |
| “反转那句说慢一点、压低一点” | 改成 `旁白慢（低沉）：……`，重跑同一条命令，只重配这一句 |
| “第 7 句再来一条” | `build ... --retake 7` |
| “先别调用接口，看看格式对不对” | `check`，或 `build ... --dry-run` |
| “原片片段先出个字幕参考剧情” | `miragea_audio.py recognize --file 片段.mp4 --wait --output ref.srt`（只作写稿参考，不要照搬原片台词） |

## 稿件格式（三种输入）

**1. 解说稿（.md / .txt）**

- 不写说话人的行一律是**解说旁白**；角色台词写成 `角色：台词`、`角色（语气）：台词` 或 `[角色|语气] 台词`。
- 开头 `---` 之间给每个说话人定音色：`名字: actor_id=ID speed=1.0`，或 `名字: voice=角色名称`（和 `actors` 列表完全一致）；可加 `model=expressive|standard`、`tags=标签`、`language=`。名字以「旁白 / 解说 / narrator / 画外音」开头的进旁白分轨，其余进台词分轨；也可写 `track=narration|dialogue` 指定。
- `=== 镜3 | 转折 ===` 或 `## 镜3` 标镜号；单独一行的 `> 画面：雨夜街口` 记到下一句的“画面”列；`[pause 0.6]` / `[停顿 0.6]` 插入停顿；`#` 开头的行忽略。
- 时间码写在行首：`00:01:12.5 文案`（从这里开始）、`[00:01:12-00:01:18] 文案`（这段画面 6 秒，超了会报告）、`@72.5 文案`（秒数）。
- 语气：`（低沉）` 会从朗读文本里去掉，作为语气标签随这一句提交；标签名须是 `capabilities` 里 `tags[].label` 的原文，用 `@tones: 低沉=实际标签名` 映射。账号没有合适标签时加 `--no-tone`。

**2. 分镜表（.csv / .tsv）**：表头自动识别 `镜号 / 画面 / 开始 / 结束 / 时长 / 角色 / 文案（或解说词、台词）/ 语气 / 语速`，只有“文案”是必需的；角色留空就是旁白。时间可写 `12.5`、`00:12.5` 或 `00:00:12,500`。

**3. SRT 字幕**：每条字幕一句，按字幕开始时间落位、按字幕时长检查超时；`角色：台词` 前缀会识别成角色。文件扩展名用 `.srt` 或 `.txt` 都行（脚本按内容识别）。

单句超过 `capabilities` 的 `audio.max_text_length` 会被接口拒绝，拆成短句即可。

## 对轨与超时报告

- **顺排**（稿件没有时间码）：按 `--gap`（默认 0.3 秒）和换镜 `--shot-gap`（默认 0.5 秒）依次排列，生成后按 `cues.csv` 的起止时间去截画面。
- **对轨**（有时间码）：每句放在自己的开始时间；上一句没说完时这一句自动顺延，并写进 report；`--allow-overlap` 则严格按时间码，允许重叠。
- 可用时长 = 这句自己的画面时长（`[开始-结束]`、分镜“时长/结束”、字幕时长），没写就算到下一句开始。实际时长超过可用时长 0.05 秒以上即列入“超出画面时长的句子”，给出建议语速和“或删约几字”。
- 处理顺序：先删字，其次调语速；建议语速高于 1.3 时听感偏赶。`--fit` 会按建议语速把超时句重配一次（会产生新的生成任务）。
- 画面比配音长 2 秒以上（`--idle` 可改）的位置也会列出来，可以补一句或留给原声、音乐。
- `--dry-run` 和 `check` 的时长是估算值，只用来提前发现明显过长的句子；正式时长以生成结果为准。

## 改一句只重配一句

每句音频按“文本 + 音色 + 语速 + 语气标签”缓存在 `输出目录/lines/`。改了第 5 句的文案，重跑同一条命令时其余句子直接复用，只生成第 5 句，时间轴、分轨、字幕和报告全部自动更新；report 里会写“本次新生成 N 句，复用缓存 M 句”。

- 同一句想要另一版：`--retake 5`（多句：`--retake 3,7`）。
- 全部重新生成：`--fresh`。
- 没有缓存的句子提交时带固定幂等键，网络中断后重跑同一条命令会取回原任务，不会重复创建。

## 解说写稿方法（解说号的留存靠稿子和节奏）

| 段落 | 作用 | 写法 |
|---|---|---|
| 1. 悬念开场 | 前 10 秒留住人 | 把最大的悬念或结局的一角先抛出来 |
| 2. 身份交代 | 让观众认人 | 一句话：身份 + 处境 |
| 3. 起因 | 事件开始 | 只讲推动剧情的动作，删掉环境描写 |
| 4. 发展 | 2–3 个转折 | 每个转折用“可是 / 没想到 / 就在这时”起句 |
| 5. 高潮 | 情绪顶点 | 句子最短、停顿最多，点睛的一两句交给角色音 |
| 6. 结局 / 反转 | 回收悬念 | 反转前 `[pause 0.6]`–`[pause 0.8]`，换 `旁白慢` |
| 7. 观点收尾 | 让人评论 | 一句个人观点 + 一个开放问题 |

- 人物第一次出场用“名字 + 身份”，之后多用身份代称（“快递员”“老板娘”）；同一段不超过三个新名字。
- 解说主体始终是旁白，角色台词只在点睛处用 1–3 句，而且是你自己写的复述或改写，不照搬原片台词。
- 语速参考：电影解说 `speed=0.95–1.05`，短剧解说 `1.05–1.15`，纪录片旁白 `0.9–0.95`。
- 一句一个镜头：画面不够时拆句或删句，比加快语速更自然。
- 生僻名字、外国人名先单句试听，读不准就换更顺口的称呼。
- 系列化：每期一个稿件文件（如 `S01E01.md`），音色写在同一个 `cast.md`，输出 `-o out/S01E01`。

## 示例稿件（examples/example.md）

```markdown
---
旁白: actor_id=NARRATOR_VOICE_ID speed=1.0
旁白慢: actor_id=NARRATOR_VOICE_ID speed=0.9
快递员: actor_id=ROLE_VOICE_ID_A
老板娘: actor_id=ROLE_VOICE_ID_B speed=1.05
@tones: 低沉=TAG_LABEL_LOW, 紧张=TAG_LABEL_TENSE, 冷笑=TAG_LABEL_COLD
---
# 电影解说示例（原创剧情，非任何影片台词）
=== 镜1 | 悬念开场 ===
> 画面：雨夜，手机屏幕亮起
他捡到的这部手机，只会显示明天的新闻。
而明天的头条，是他自己。
=== 镜2 | 身份交代 ===
> 画面：电动车穿过窄巷
一个送了八年快递、欠着房租的男人，每天在同一条街上跑四十单。
快递员（紧张）：明天下午三点……这不就是我送件的时间吗？
=== 镜3 | 转折 ===
他决定第二天请假，哪儿也不去。
可是就在这时，楼下小店的老板娘敲响了他的门。
老板娘（冷笑）：你今天不送，这条街上的件谁来送？
[pause 0.6]
旁白慢（低沉）：他这才发现，新闻里死的那个人，好像不是他。
=== 镜4 | 观点收尾 ===
如果你提前知道了明天，你会选择躲开，还是走过去看看？
```

`examples/` 里还有：`timed_script.txt`（带时间码，最后一句故意超时，演示报告）、`storyboard.csv`（分镜表）、`sample_srt.txt`（SRT 格式字幕存成 .txt）。全部为原创文字，可直接 `--dry-run`。

## 接入剪辑

- **剪映 / CapCut**：`stems/narration.wav`、`stems/dialogue.wav` 各放一条音频轨（或只放 `voiceover.wav`），起点放在 0 秒；“导入字幕”选 `voiceover.srt`；按 `cues.csv` 的开始时间摆镜头。
- **Premiere / 达芬奇**：同样导入分轨和 SRT；`cues.csv` 可作为打点表。
- **背景音乐**：本技能不混音，BGM 在剪辑软件里压低到不抢人声；台词段可以把旁白轨和 BGM 一起再压一点。

```bash
# 配音替换原视频音轨（需要本机 ffmpeg）
ffmpeg -i 画面.mp4 -i ep01/voiceover.wav -map 0:v -map 1:a -c:v copy -shortest 配音版.mp4
# 烧录字幕
ffmpeg -i 配音版.mp4 -vf subtitles=ep01/voiceover.srt -c:a copy 成片.mp4
# 配音 + 背景音乐（音乐压低）
ffmpeg -i ep01/voiceover.wav -i bgm.mp3 -filter_complex "[1:a]volume=0.2[b];[0:a][b]amix=inputs=2:duration=first" mix.wav
```

## 方案对比

| 对比项 | 人工配音 | 剪辑软件里逐句文字转语音 | 本技能 |
|---|---|---|---|
| 解说声线 | 随配音员档期变化 | 每句手动选音色 | 你自己克隆的音色写在音色表里，整季固定 |
| 对画面 | 录完再对轨 | 手动拖到时间线 | 读时间码 / 分镜表 / SRT 自动落位，报告超时句和建议语速 |
| 交付 | 一条混合音轨 | 一句一个片段 | 整段 + 旁白分轨 + 台词分轨 + 每人单轨 + 两份 SRT + 计划表 |
| 改稿 | 补录再对轨 | 删掉重做那句再对齐 | 改哪句只重配哪句，时间轴和字幕自动更新 |
| 本地环境 | 录音环境 | 剪辑软件 | Python 3.9+ 标准库，无需显卡 |

## 常见问题（FAQ）

**电影解说配音需要什么才能正式生成？**
需要 Miragea 的 API Key 和账号里克隆好的音色（见「快速开始」）。没有 Key 时 `--dry-run` 和 `selftest` 能把稿件解析、对轨、分轨、字幕和报告全部跑通。

**解说旁白和角色台词能分成两条音轨吗？**
能。`stems/narration.wav` 是旁白、`stems/dialogue.wav` 是台词，和 `voiceover.wav` 等长；`stems/roles/` 还有每个说话人的单轨。

**配音时长和画面对不上怎么办？**
在稿件行首写时间码，或用分镜表 / SRT。`report.md` 会列出超出画面的句子、建议语速和大约要删的字数；`--fit` 可按建议语速自动重配。

**电影解说用 AI 配音会被判搬运吗？**
配音方式不是判断搬运的主要依据，原创解说稿和二创比例才是。按平台规则标注 AI 生成内容；画面素材的版权和二创规则需要你自己遵守。

**能用原片演员的声音吗？**
不能。未经授权克隆演员声音有侵权风险，角色台词用你自有或已授权的音色。

**改了一句稿要全部重新生成吗？**
不用。每句缓存在 `lines/`，重跑同一条命令只生成改动的那句；想换一版用 `--retake 句号`。

**一部电影解说十几分钟，可以一次配音吗？**
可以，保持一行一句、单句不超过 `capabilities` 的字数上限即可。建议按段落拆成几个文件，返工更快。

**能做英文 movie recap 吗？**
把稿件改写成英文再生成，音色选适合英文的角色，字幕用 `--max-chars 40`；效果以试听为准。

**需要显卡吗？哪些 Agent 能用？**
不需要显卡，本地只跑 Python 标准库。Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 等能运行 Python 的 Agent 都能用。

## 出问题了？

| 现象 | 处理 |
|---|---|
| `未设置 MIRAGEA_API_KEY` / `missing_api_key` | 生成 Key 后 `export MIRAGEA_API_KEY=...`；没有 Key 先用 `--dry-run` 或 `selftest`（不会调用接口） |
| `这些说话人还没有音色` / `还是示例占位符` | `cast 稿件 -o cast.md`，填入 `miragea_audio.py actors` 返回的真实 `actor_id` 或 `voice=角色名称`，再加 `--cast cast.md` |
| `actor_not_found` / `ambiguous_actor_name` | `voice=` 的名称要和 `actors` 列表完全一致；同名角色改用 `actor_id=` |
| `音频链接直接克隆已停用` | 旧稿件用了已停用的音频链接写法：录音先 `create-actor` 建角色，再改成 `voice=` 或 `actor_id=` |
| `找不到稿件文件` | 检查路径；先用 `examples/` 下的示例试跑 |
| report.md 里很多句超时 | 先删字，再调语速，或加 `--fit` |
| 401 | 检查 Key；不要把 Key 写进日志 |
| 403 | 检查账号的 API 访问权限 |
| 400 / 413 | 修正参数：模式、标签、语速、单句字数；或减小上传文件、缩短媒体 |
| 409 | 幂等键被用于不同输入，或字幕费率已变化：重新确认后再提交 |
| 429 | 额度不足或限流，等待或补充额度 |
| 等待超时 / 网络中断 | 任务可能仍在运行：直接重跑同一条命令（同一幂等键会取回原任务），或用 `miragea_audio.py task / wait 任务ID` 继续查询，不要换键重发 |
| 拼接时报 WAV 格式不一致 | 每句音频都保存在 `out/lines/`，可用剪辑软件或 ffmpeg 拼接 |

官方客户端退出码：0 请求成功（没有 `--wait` 时可能仍在排队），1 任务失败，2 客户端或接口错误。

`recap_dub.py` 退出码：0 成功；1 selftest 有未通过项；2 参数、文件或接口错误（含未设置 Key，此时不会调用接口）。

## 限制

- 按句生成后在本地拼接，不做口型同步，不混背景音乐。
- 语气靠所选模式提供的语气标签和语速、停顿表现，可用标签以 `capabilities` 实时返回为准。
- 拼接要求每句都是同一格式的 16 位 PCM WAV（脚本固定请求 wav）；不一致时每句音频仍保存在 `lines/`，可用剪辑软件拼接。
- `--dry-run` / `check` 的时长为估算值，只用于检查流程和提前发现明显超长的句子。

## 合规

- 只克隆你本人或已获得明确授权的声音，不模仿明星、主播、原片演员或任何未授权的人。
- 按《人工智能生成合成内容标识办法》和抖音、快手、视频号、小红书、B站等平台规则，发布时声明或标注 AI 生成内容。
- 影视画面和原片台词有版权：本技能只给你自己写的解说稿配音，不提取、不模仿原片声音；使用影视素材请遵守版权方和平台的二创规则。
- `scripts/miragea_audio.py` is the official client 1.3.0, shipped unchanged；`scripts/voiceover.py`、`scripts/recap_dub.py` 为原创，MIT 许可（见 `LICENSE.txt`）。

## English Summary

- **Movie / TV / short-drama recap voiceover (电影解说配音)**: input a recap script (untagged lines = narration, `Role (tone): line` = dialogue, optional time codes), a shot-list CSV/TSV or an SRT (also as .txt).
- Narrator and characters each use a role in your account (`voice=NAME` or `actor_id` from `miragea_audio.py actors`; create one from your own recording with `create-actor`); per-line tone tags; lines are locked to picture time codes, with an overrun report (suggested speed / characters to cut) and `--fit`.
- Outputs `voiceover.wav`, `stems/narration.wav`, `stems/dialogue.wav`, per-speaker stems, `voiceover.srt`, `voiceover_roles.srt`, `cues.csv`, `report.md`, `manifest.json`. Edit one line, re-render one line; `--retake`.
- Offline: `recap_dub.py selftest` and `--dry-run` need no key and no network. Python 3.9+ stdlib, no GPU.

**关键词**：电影解说配音、解说配音、短剧解说、影视解说、短剧解说配音、影视解说配音、电影解说、AI配音、旁白配音、多角色配音、声音克隆、字幕对轨、分镜配音、画面对轨、剪映配音、SRT字幕、文字转语音、movie recap、recap voiceover、voiceover、narration、voice cloning
