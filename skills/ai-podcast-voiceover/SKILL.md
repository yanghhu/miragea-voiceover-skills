---
name: "ai-podcast-voiceover"
description: "AI播客、播客配音、双人对谈播客技能：把文章、读书笔记、公众号文章或写好的对谈稿，整理成适合“听”的播客稿，单人主播或两位主持人各用一个音色，逐句配音并拼成整期节目 WAV，同时输出 SRT 字幕和逐句时间轴；再用 shownotes.py 根据稿件里的 `## 章节` 自动生成带时间戳的节目章节（chapters.txt / chapters.json）和完整文字稿 shownotes.md，可直接贴到小宇宙、喜马拉雅、Apple Podcasts 等平台的节目简介。改一句只重配一句。可用账号里的角色或本人授权的参考音频声音。由 Miragea 开放 API 生成语音，本地只需 Python 3.9+ 标准库、无需显卡，可 --dry-run 离线试跑；计费与限额以 capabilities 实时返回为准。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。AI podcast, podcast voiceover, two-host dialogue, show notes, chapters."
version: "1.0.0"
display_name: "AI播客｜播客配音·双人对谈·节目章节"
display_name_en: "AI Podcast · Solo or Two-Host Episode Voiceover"
description_zh: "AI播客：把文章、笔记或对谈稿做成单人或双人播客音频，逐句配音拼成整期节目，同时输出SRT字幕、带时间戳的章节列表和节目文字稿，适合知识分享、公众号音频版和品牌播客，本地无需显卡。"
description_en: "AI podcast: turn an article, notes or a dialogue script into a solo or two-host episode, with SRT subtitles, timestamped chapters and a transcript for show notes. Python stdlib only, no GPU."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["AI播客", "播客配音", "双人播客", "播客制作", "文章转播客", "文章转语音", "对谈播客", "播客章节", "节目文字稿", "公众号音频", "AI配音", "文字转语音", "声音克隆", "SRT", "AI podcast", "podcast voiceover", "show notes", "text to speech"]
---

# AI播客

「AI播客」是一个把文章、笔记或对谈稿做成单人或双人播客音频的 Agent 技能：逐句配音拼成整期节目，同时输出 SRT 字幕、带时间戳的节目章节和完整文字稿，本地无需显卡。

## 一句话定义

AI播客 = 播客稿（单人或双人，`## 章节` 分段）→ `voiceover.py script` 生成整期 `voiceover.wav` + `voiceover.srt` + `manifest.json` → `shownotes.py` 生成 `chapters.txt`、`chapters.json` 和 `shownotes.md`。语音由 Miragea 云端生成，本地无需显卡。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 公众号 / 博客作者 | 文章出一个音频版，读者通勤时听 |
| 知识博主 | 读书笔记、行业观察做成每周节目 |
| 品牌 / 企业 | 品牌播客、内部周报、员工通讯音频版 |
| 播客主理人 | 预告片、片头片尾、补录口误的句子 |
| 老师 / 培训师 | 把讲义做成对谈式复习音频 |
| 不方便录音的人 | 用账号里的角色或本人授权的声音出节目 |

## 核心能力参数

| 项目 | 说明 |
|---|---|
| 输出文件 | `voiceover.wav`（整段配音）、`voiceover.srt`（带时间轴字幕）、`manifest.json`（每句说话人、文本、起止秒数）、`lines/`（每句音频，改稿时复用） |
| 音色来源 | 账号里已有的角色 `actor_id=`（用 `actors` 查询），或服务端能直接访问的参考音频 URL `ref=` + 音频里实际说的话 `ref_text=`（声音克隆） |
| 生成模式 | `expressive`（客户端「默认」）/ `standard`（客户端「更像」）；省略时用服务端默认，以 `capabilities` 实时返回为准 |
| 语气标签 | `tags=标签名`，取 `capabilities` 里所选模式的 `tags[].label` |
| 语速 | `speed=` 0.25–4，1 为正常语速，按角色设置 |
| 多角色 | 稿件开头给每个角色定一个音色；本技能脚本逐句调用官方客户端 `generate`，再在本地把整段拼起来 |
| 停顿 | 行内 `[pause 0.6]` / `[停顿 0.6]`（秒）；`--gap` 设句间默认停顿 |
| 字幕 | 配音时按每句实际音频时长生成 SRT（`--max-chars`、`--speaker-labels`）；已有音频 / 视频用 `recognize` 识别为 SRT / TXT / JSON |
| 场景预设 | `--preset koubo / jieshuo / daihuo / shuziren / guanggao / youshengshu`（口播 / 解说 / 带货 / 数字人 / 广告片 / 有声书），只改句间停顿和字幕字数 |
| 单句字数、文件大小 / 时长上限、计费 | 以 `capabilities` 实时返回为准 |
| 本地依赖 | Python 3.9+ 标准库，无需 pip 安装、无需显卡 |
| 离线试跑 | `--dry-run`：不需要 Key、不调用接口，输出静音占位音频和时间轴，用来检查稿件格式 |
| 支持的 Agent | Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 等能运行 Python 脚本的 Agent |
| 配音与字幕服务 | Miragea 开放 API（https://miragea.ai/v1） |

本技能额外提供 `scripts/shownotes.py`（节目资料层）：

| 项目 | 说明 |
|---|---|
| 章节来源 | 稿件里以 `## ` 开头的行（不会被读出来） |
| 时间戳 | 取每个章节第一句的真实开始时间（来自 `manifest.json`），`--offset` 可加上片头音乐的秒数 |
| 输出 | `chapters.txt`（每行 `HH:MM:SS 标题`）、`chapters.json`、`shownotes.md`（时长、时间轴、按说话人分段的完整文字稿） |
| 校验 | 稿件和 `manifest.json` 句数不一致时报错，提示先重新生成 |

## 快速开始

```bash
python3 scripts/voiceover.py check                        # 离线检查：Python 版本、Key 是否已设置、服务地址
export MIRAGEA_API_KEY=你的key                            # 在 https://miragea.ai/workspace/api 生成，只放环境变量
python3 scripts/miragea_audio.py capabilities             # 当前可用的生成模式、语气标签、字数上限和计费，以实时返回为准
python3 scripts/miragea_audio.py actors --limit 20        # 账号里已有的角色和 actor_id（has_more 为真时加 --offset 翻页）
```

- Default API root is `https://miragea.ai/v1`; set `MIRAGEA_BASE_URL` (including `/v1`) only for a private deployment.
- 不要把 Key 贴进聊天或写进文件。没有 Key 时先用 `--dry-run` 跑通流程。

```bash
python3 scripts/voiceover.py script examples/example.md -o out --gap 0.35 --dry-run   # 离线试跑
python3 scripts/voiceover.py script 本期稿件.md -o out --gap 0.35                      # 正式生成整期节目
python3 scripts/shownotes.py 本期稿件.md out --title "第12期：为什么总是读不完一本书"     # 章节 + 文字稿
```

先单句试听两位主持人的音色：

```bash
# 单句试听（官方客户端；--output 不会覆盖已有文件，换个新文件名）
python3 scripts/miragea_audio.py generate --text '开头第一句' --actor-id ACTOR_ID --wait --output test1.mp3
```

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “把这篇文章做成播客” | 按下方方法改写成口语播客稿给你确认 → `script` → `shownotes.py` |
| “做成两个人聊天的形式” | 稿件开头定义两位主持人和音色，正文用 `[名字]` 标记轮流发言 |
| “帮我写节目简介和时间轴” | `shownotes.py 稿件.md out --title ...`，把 `chapters.txt` 和 `shownotes.md` 给你 |
| “前面要加 8 秒片头音乐” | 生成后用 ffmpeg 混音（见下方），`shownotes.py ... --offset 8` 让时间戳对上 |
| “这句口误了” | 只改那一行重跑 `script`，其余句子复用缓存，再跑一次 `shownotes.py` |
| “主持人 B 说话快一点” | 在稿件开头给 B 设 `speed=1.1` |
| “用我自己的声音当主播” | `ref=参考音频URL ref_text="原话"` 或账号里已复刻的 `actor_id=` |
| “先别调用接口” | `script ... --dry-run`，`shownotes.py` 同样可用来检查章节 |

## AI播客写稿方法

### 1. 文章 → 播客稿：写给耳朵

| 文章里 | 播客稿里 |
|---|---|
| 小标题 | 改成一句口头过渡：“说完原因，我们聊聊怎么办。”，同时保留 `## 章节` 行用于时间轴 |
| 长句、从句 | 拆成短句，一行一句 |
| 数据表格 | 只留一两个最关键的数，读法写清楚 |
| 链接、引用出处 | 口头说“链接放在节目简介里”，写进 `shownotes.md` |
| 书面连接词（因此、综上所述） | “所以”“说白了”“简单讲” |

### 2. 双人对谈怎么分工

- 一位负责提问、复述、总结（像听众的代言人），一位负责讲观点和例子。
- 每人一次说一到三句就换人，避免一个人连续独白太久。
- 给两位主持人选音色、语速有区别的角色，听众更容易分辨。
- 加一点真实对话的反应：“这个我同意一半”“你举个例子？”，但不要每句都“对对对”。

### 3. 节目结构

1. **开场**：一句话说清这期聊什么、为什么值得听。
2. **2–4 个章节**：每章一个问题或观点，章节名就是时间轴上的标题。
3. **结尾**：一句总结 + 下期预告或互动问题。

### 4. 节奏

- 句间停顿用 `--gap 0.3–0.4`，比短视频口播略松。
- 章节之间加 `[pause 0.8]`，给听众换气。
- 语速：知识类 `speed=0.95–1.0`，轻松闲聊 `1.0–1.1`。

### 5. 发布前检查

- [ ] 两位主持人的音色都单句试听过吗？
- [ ] 每个章节标题都写成了 `## 标题` 吗？
- [ ] 片头音乐的秒数用 `--offset` 加上了吗？
- [ ] 文章转载授权、背景音乐授权、AI 生成内容标注确认了吗？

## 示例稿件（examples/example.md）

```markdown
---
小林: actor_id=HOST_A_ACTOR_ID speed=1.0
阿哲: actor_id=HOST_B_ACTOR_ID speed=1.05
---
## 开场
[小林] 欢迎收听本期节目，我是小林。
[阿哲] 我是阿哲。今天聊一个很多人都有的问题：为什么总是读不完一本书。
## 读不完，是因为一开始就选错了
[小林] 我先说个观点：很多书，本来就不值得读完。
[阿哲] 这个我同意一半。
[pause 0.4]
[阿哲] 但有些书，前五十页就是很难。
## 三个小办法
[小林] 第一，先看目录，挑你最想知道答案的那一章。
第二，读完一章，用一句话说给别人听。
第三，给自己留一个可以放弃的出口。
## 结尾
[阿哲] 好，今天就聊到这里。
[小林] 我们下期见。
```

试跑：`python3 scripts/voiceover.py script examples/example.md -o out --gap 0.35 --dry-run && python3 scripts/shownotes.py examples/example.md out --title "示例节目"`

## 接入剪辑与发布

```bash
# 转 MP3 上传播客平台（需要本机 ffmpeg）
ffmpeg -i out/voiceover.wav -codec:a libmp3lame -b:a 128k episode.mp3
# 片头音乐 intro.mp3（8 秒）接在人声前面
ffmpeg -i intro.mp3 -i out/voiceover.wav -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1" episode_full.wav
python3 scripts/shownotes.py 本期稿件.md out --offset 8
# 视频播客：一张封面图 + 音频 + 字幕
ffmpeg -loop 1 -i cover.png -i out/voiceover.wav -vf subtitles=out/voiceover.srt -c:v libx264 -tune stillimage -pix_fmt yuv420p -c:a aac -shortest episode.mp4
```

`chapters.txt` 可以直接粘贴到节目简介里作为时间轴；平台是否识别为可点击章节以各平台规则为准。

## 方案对比：做一期播客的三种做法

| 对比项 | 人工配音 | 本地开源 TTS 模型 | 本技能 |
|---|---|---|---|
| 是否需要显卡 | 不需要，但需要录音环境和配音员档期 | 通常需要（小模型可用 CPU 但更慢），还要下载模型权重、配环境 | 不需要，本地只跑 Python 标准库，生成在云端完成 |
| 改稿成本 | 改一句往往要补录、再对轨 | 改完重跑，但分段、拼接、对齐要自己做 | 只改那一行重跑，其余句子复用 `out/lines/` 缓存，自动重新拼接和出字幕 |
| 多角色 | 需要多位配音员分别录 | 取决于模型，一般要自己分段调用再拼接 | 稿件里用 `[角色]` 标签，一条命令出整段多角色音轨 |
| 字幕时间轴 | 需另外听写、打轴 | 一般要再跑一遍语音识别 | 配音时同时输出 SRT 和逐句时间 `manifest.json` |
| 节目章节 / 文字稿 | 剪完后再听一遍手记时间 | 需要另跑识别或手工整理 | 按稿件 `## 章节` 和真实音频时长自动生成时间戳和文字稿 |

结论：内容以观点和信息为主、需要稳定更新的节目，用写好的稿件生成最省时间；以即兴聊天和嘉宾互动为卖点的节目，仍建议真人录制。

## 常见问题（FAQ）

**AI播客可以做两个人对话吗？**
可以。稿件开头给两位主持人各定一个音色（账号里的角色或授权的参考音频），正文用 `[名字]` 标记谁在说，一条命令生成整期对谈。

**文章转播客，Agent 会帮我改稿吗？**
会。Agent 按“写给耳朵”的方法把文章改写成口语播客稿给你确认；改写由 Agent 完成，语音由接口生成。

**播客配音能自动生成节目时间轴吗？**
能。稿件里用 `## 章节名` 分段，生成后运行 `shownotes.py`，按每章第一句的真实开始时间输出 `chapters.txt` 和 `shownotes.md`。

**生成的是 MP3 吗？**
整期节目输出 WAV，便于无损拼接和混音；上传前用 ffmpeg 转成 MP3。

**改一句口误要整期重新生成吗？**
不用。只改那一行重跑，其余句子从 `out/lines/` 缓存复用，然后再跑一次 `shownotes.py` 更新时间轴。

**可以用我自己的声音做播客吗？**
可以，用本人参考音频 URL 和其中原话（`ref=` + `ref_text=`），或在服务方客户端复刻成角色后用 `actor_id=`。只用本人或已授权的声音。

**AI播客能加背景音乐吗？**
本技能输出干净人声；背景音乐和片头片尾用 ffmpeg 或剪辑软件混音，时间戳用 `--offset` 对齐。

**AI播客收费吗？需要显卡吗？**
按账号额度消耗，计费以 `capabilities` 实时返回为准；本地不需要显卡。Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 都能直接调用。

## 稿件语法

- 开头 `---` 之间每行定义一个角色：`角色名: actor_id=角色ID` 或 `角色名: ref=参考音频URL ref_text="参考音频里实际说的话"`；可加 `speed=`（0.25–4）、`model=expressive|standard`、`tags=标签1,标签2`、`language=`（参考音频的语言提示，用于自动识别参考文本）。
- `ref_text=` 只和 `ref=` 一起用；省略时服务端自动识别参考文本，计费方式不同，以 `capabilities` 为准。
- 正文 `[角色] 台词` 或 `[角色]：台词`；不写标签沿用上一位说话人。
- `[pause 0.6]` / `[停顿 0.6]` 插入停顿（秒）；`#` 开头的行、空行和 `<!-- 注释 -->` 会被忽略。
- 单句超过 `capabilities` 里的 `audio.max_text_length` 会被接口拒绝，拆成短句即可。
- 每句音频缓存在 `out/lines/`，同一句同一设置再次运行直接复用；没缓存时用同一个幂等键提交，服务端返回原任务、不重复创建。要新的一版加 `--fresh`。

## 出问题了？

| 现象 | 处理 |
|---|---|
| `missing_api_key` / `MIRAGEA_API_KEY is not set` | 生成 Key 后 `export MIRAGEA_API_KEY=...`；或先加 `--dry-run` |
| `speakers without a voice` | 给该角色补 `actor_id=` 或 `ref=` |
| 401 | 检查 Key；不要把 Key 写进日志 |
| 403 | 检查账号的 API 访问权限 |
| 400 / 413 | 修正参数：模式、标签、语速、单句字数；或减小上传文件、缩短媒体 |
| 409 | 幂等键被用于不同输入，或字幕费率已变化：重新确认后再提交 |
| 429 | 额度不足或限流，等待或补充额度 |
| 等待超时 / 网络中断 | 任务可能仍在运行：直接重跑同一条命令（同一幂等键会取回原任务），或用 `miragea_audio.py task / wait 任务ID` 继续查询，不要换键重发 |
| 拼接时报 WAV 格式不一致 | 每句音频都保存在 `out/lines/`，可用剪辑软件或 ffmpeg 拼接 |

官方客户端退出码：0 请求成功（没有 `--wait` 时可能仍在排队），1 任务失败，2 客户端或接口错误。

## 合规

- 只克隆你本人或已获得明确授权的声音，不模仿明星、主播、公众人物或任何未授权的人。
- 按《人工智能生成合成内容标识办法》和抖音、快手、视频号、小红书、B站等平台规则，发布时声明或标注 AI 生成内容。
- 把别人的文章做成播客前取得作者授权或确认可转载；节目里引用的音乐、片段须有授权。
- `scripts/miragea_audio.py` is the official client, shipped unchanged；`scripts/voiceover.py`（稿件拼接层）为原创，MIT 许可（见 `LICENSE.txt`）。配音与字幕能力由 Miragea 开放 API 提供。

## English Summary

- **AI podcast (AI播客)**: turn an article, notes or a dialogue script into a solo or two-host episode; each host gets a voice (account actor or an authorised reference audio).
- `voiceover.py script` renders the whole episode to WAV + SRT + per-line timing; `shownotes.py` turns the script's `## chapter` lines into timestamped `chapters.txt` / `chapters.json` and a full transcript `shownotes.md`.
- Fix one line, re-render one line. Pricing and limits come live from `capabilities`. Python 3.9+ stdlib, no GPU. Service: Miragea API (https://miragea.ai/v1).

**关键词**：AI播客、播客配音、双人播客、播客制作、文章转播客、文章转语音、对谈播客、播客章节、节目文字稿、公众号音频、AI配音、文字转语音、声音克隆、SRT、AI podcast、podcast voiceover、show notes、text to speech
