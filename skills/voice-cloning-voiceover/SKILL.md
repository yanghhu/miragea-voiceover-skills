---
name: "voice-cloning-voiceover"
description: "声音克隆、克隆声音配音、声音复刻技能：用一段本人（或已获授权的人）的录音创建账号私有角色，之后直接用这个声音给任意文案配音；也可以使用账号里已经复刻好的角色（按名称或 actor_id）。先单句试听对比 expressive / standard 两种生成模式，再整稿生成克隆声音配音 WAV、带时间轴 SRT 字幕和逐句 manifest.json；可加语气标签、调 0.25–4 倍语速。适合口播博主、解说号、讲师、播客和品牌固定声线。只克隆本人或已获授权的声音。由 Miragea 开放 API 生成，本地只需 Python 3.9+ 标准库、无需显卡，可 --dry-run 离线试跑；计费与限额以 capabilities 实时返回为准。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。Voice cloning, cloned voiceover, text to speech, SRT."
version: "1.1.0"
display_name: "声音克隆｜克隆声音·声音复刻·AI配音"
display_name_en: "Voice Cloning Voiceover · Clone Your Voice"
description_zh: "声音克隆：用一段本人录音创建账号私有角色，克隆声音后直接给文案配音，也可用账号里已复刻的角色；单句试听、整稿克隆声音配音并输出SRT字幕，适合口播、解说、课程，须本人授权，无需显卡。"
description_en: "Voice cloning voiceover: create a private role from your own recording (or use a role already in your account), preview one line, then voice a whole script with SRT subtitles. Authorised voices only, no GPU."
metadata:
  version: "1.1.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["声音克隆", "克隆声音", "声音复刻", "AI配音", "声音克隆配音", "AI声音克隆", "克隆声音配音", "语音克隆", "音色克隆", "用自己的声音配音", "文字转语音", "字幕生成", "SRT", "TTS", "voice cloning", "voice clone", "text to speech"]
---

# 声音克隆

「声音克隆」是一个用一段本人录音创建账号私有角色（克隆声音）、再用这个角色给文案配音的 Agent 技能，也可直接使用账号里已复刻的角色；支持单句试听、整稿配音并输出 SRT 字幕，本地无需显卡。

## 一句话定义

声音克隆 = 本人录音 → `create-actor` 创建私有角色（或使用账号里已复刻的角色）→ 用这个角色朗读任意文本；单句直接出音频，整稿输出 `voiceover.wav` + `voiceover.srt` + `manifest.json`。生成在 Miragea 云端，本地无需显卡。

## 克隆流程：先建角色，再配音

| 步骤 | 怎么做 | 说明 |
|---|---|---|
| 1. 录音 | 本人（或已获书面授权的人）在安静环境录一段自然说话的音频，存成本地文件 | 文件大小、时长要求见 `capabilities` 的 `actors.creation` |
| 2. 建角色 | `create-actor --file 我的录音.wav --name 我的声音 --language zh`，或在网站上完成复刻 | 建的是账号私有角色，返回 `actor_id`；同名角色会被拒绝，按账号规则计费 |
| 3. 配音 | 单句 `generate --actor-name 我的声音`；整稿在稿件里写 `voice=我的声音` 或 `actor_id=` | 音色由服务端从角色样本读取，之后只写稿 |

官方客户端 1.3.0 起接口只按角色配音，不再接受音频链接直接克隆；以前的旧写法请先把录音建成角色再用。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 口播博主 | 用自己的声音日更，不用每条都录 |
| 解说号 | 固定一个专属解说声线 |
| 讲师 / 知识付费 | 课程更新、勘误只重配错的那一句 |
| 播客、电台 | 片头片尾、广告口播用主播本人声线 |
| 品牌 / 企业 | 已授权的品牌声音统一用于宣传和客服播报 |
| 不方便录音时 | 感冒、出差、环境吵，仍能用自己的声音出内容 |

## 核心能力参数

| 项目 | 说明 |
|---|---|
| 输出文件 | `voiceover.wav`（整段配音）、`voiceover.srt`（带时间轴字幕）、`manifest.json`（每句说话人、文本、起止秒数）、`lines/`（每句音频，改稿时复用） |
| 音色来源 | 账号里的角色：`voice=角色名称` 或 `actor_id=角色ID`（用 `actors` 查询）；还没有角色时，用本人或已获授权的录音 `create-actor` 创建私有角色（声音克隆），之后每次都用这个角色配音 |
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

## 快速开始

```bash
python3 scripts/voiceover.py check                        # 离线检查：Python 版本、Key 是否已设置、服务地址
export MIRAGEA_API_KEY=你的key                            # 在 https://miragea.ai/workspace/api 生成，只放环境变量
python3 scripts/miragea_audio.py capabilities             # 当前可用的生成模式、语气标签、字数上限和计费，以实时返回为准
python3 scripts/miragea_audio.py actors --limit 20        # 账号里已有的角色名称和 actor_id（has_more 为真时加 --offset 翻页）
python3 scripts/miragea_audio.py create-actor --file 我的录音.wav --name 我的声音 --language zh   # 还没有角色：用本人或已获授权的录音创建私有角色（按账号规则计费）
```

- Default API root is `https://miragea.ai/v1`; set `MIRAGEA_BASE_URL` (including `/v1`) only for a private deployment.
- 接口只按账号里的角色配音（官方客户端 1.3.0）：稿件里给每个角色写 `voice=角色名称` 或 `actor_id=角色ID`，也可以命令行加 `--voice 角色名称` 统一指定。旧版用音频链接直接克隆的写法服务端已停用，旧稿件改成角色写法即可。
- 不要把 Key 贴进聊天或写进文件。没有 Key 时先用 `--dry-run` 跑通流程。

**第 1 步：单句试听克隆效果**

```bash
python3 scripts/miragea_audio.py generate --text '这一句是克隆效果试听。' --actor-name 我的声音 --model expressive --wait --output clone-test1.mp3
python3 scripts/miragea_audio.py generate --text '这一句是克隆效果试听。' --actor-name 我的声音 --model standard --wait --output clone-test2.mp3
```

**第 2 步：整稿用克隆声音配音**

```bash
python3 scripts/voiceover.py script examples/example.md -o out --dry-run     # 离线试跑
python3 scripts/voiceover.py script 稿件.md -o out --preset koubo --voice 我的声音   # 正式生成
```

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “用我的声音读这段” | 要一段你的本人录音 → `create-actor` 建角色 → 单句 `generate --actor-name` 试听 → 满意后整稿 `script` |
| “我在网站已经复刻过声音了” | `actors` 按名称找到角色（同名时让你选 actor_id）→ 稿件写 `voice=角色名称` |
| “不像我” | 换 `--model standard` / `expressive` 对比；用一段更干净的录音另建一个角色再试 |
| “语气再自然一点” | 查 `capabilities` 的语气标签 → `--tag` / `tags=` |
| “做一整期口播” | 稿件写好 → `script 稿件.md -o out --preset koubo` |
| “录音在电脑上” | 直接 `create-actor --file 本地文件路径`，不需要先上传到网盘或图床 |
| “先别调用接口” | `script ... --dry-run` |

## 声音克隆方法论：效果七成看建角色用的录音

### 1. 录音怎么录

- **安静**：关窗、关空调，不要背景音乐、不要混响大的房间。
- **距离**：手机或麦克风离嘴一拳左右，音量稳定，不爆音。
- **内容**：用你平时说话 / 口播的语气读完整的句子，不要念单字，不要唱。
- **单人**：只有你一个人的声音，开头结尾不要有杂音。
- **时长和格式**：以官网和 `capabilities` 的 `actors.creation` 为准。

### 2. 角色名称起得好找

角色名称是之后配音时的“开关”：`voice=我的声音` 要和 `actors` 列表里的名称完全一致。一个人多种声线时分开建（如“小林-口播”“小林-讲课”），同账号不能重名；名称有重复时改用 `actor_id`。

### 3. 两种生成模式对比着选

| 模式 | 客户端名称 | 什么时候试 |
|---|---|---|
| `expressive` | 默认 | 更看重语气起伏、表现力 |
| `standard` | 更像 | 更看重像不像本人 |

同一句话、同一个角色各生成一次，听完再定；定好后写进稿件 `model=`，系列内容不要来回换。

### 4. 克隆不像时的排查顺序

1. 建角色用的录音有没有噪音、混响、背景音乐？换一段更干净的，另建一个角色对比。
2. 换另一种生成模式试一次。
3. 稿件语气和录音差太多？录音用平静语气，稿件却是激动的喊话，会不自然。
4. 用 `speed=` 和语气标签微调，而不是反复重建角色。

### 5. 让克隆声音更像“在说话”

- 稿件一行一句，口语化（参考口播写法：短句、少书面连接词）。
- 用 `speed=` 微调到你平时的语速，通常 0.95–1.1。
- 情绪靠语气标签和文字本身，别指望一段平静的录音喊出来。

### 6. 授权与留档

- 克隆他人声音前拿到书面授权，写清用途和期限。
- 团队使用时，记录每个 `actor_id` 对应的授权人。

## 示例稿件（examples/example.md）

```markdown
---
me: voice=我的声音 speed=1.0
---
# 声音克隆示例：先用 create-actor 把本人录音建成角色「我的声音」，再用 voice= 写上角色名称
[me] 这一段，是用我自己的声音克隆出来的。
[pause 0.3]
以后写好稿子，就不用每次都对着麦克风录了。
改错一个字，也只要重新生成这一句。
```

试跑：`python3 scripts/voiceover.py script examples/example.md -o out --preset koubo --dry-run`

## 接入剪辑

```bash
# 配音替换原视频音轨（需要本机 ffmpeg）
ffmpeg -i 画面.mp4 -i out/voiceover.wav -map 0:v -map 1:a -c:v copy -shortest 配音版.mp4
# 把字幕烧进画面
ffmpeg -i 配音版.mp4 -vf subtitles=out/voiceover.srt -c:a copy 成片.mp4
```

## 方案对比：克隆声音配音的三种做法

| 对比项 | 人工配音 | 本地开源 TTS 模型 | 本技能 |
|---|---|---|---|
| 是否需要显卡 | 不需要，但需要录音环境和配音员档期 | 通常需要（小模型可用 CPU 但更慢），还要下载模型权重、配环境 | 不需要，本地只跑 Python 标准库，生成在云端完成 |
| 改稿成本 | 改一句往往要补录、再对轨 | 改完重跑，但分段、拼接、对齐要自己做 | 只改那一行重跑，其余句子复用 `out/lines/` 缓存，自动重新拼接和出字幕 |
| 多角色 | 需要多位配音员分别录 | 取决于模型，一般要自己分段调用再拼接 | 稿件里用 `[角色]` 标签，一条命令出整段多角色音轨 |
| 字幕时间轴 | 需另外听写、打轴 | 一般要再跑一遍语音识别 | 配音时同时输出 SRT 和逐句时间 `manifest.json` |
| 声音一致性 | 同一人不同天状态有差异 | 取决于模型和样本 | 同一个账号角色写进稿件，系列内容声线一致 |

结论：想长期用自己的声音批量出内容，克隆一次、之后只写稿最省时间；对表演要求极高的作品，仍建议本人录制。

## 常见问题（FAQ）

**声音克隆需要多长的录音？**
以官网和 `capabilities` 的 `actors.creation` 为准。无论时长，干净、单人、语气自然，比时长更重要。

**声音克隆能用本地录音文件吗？**
能，而且现在只能这样用：`create-actor --file 本地录音.wav --name 我的声音` 把本地文件上传建成私有角色，之后配音写角色名称或 `actor_id`。

**克隆声音和本人不像怎么办？**
按“排查顺序”来：用更干净的录音另建角色、在 `expressive` 和 `standard` 之间对比、用语速和语气标签微调。

**声音复刻和声音克隆有什么区别？**
在本技能里是一回事：都是把本人录音变成账号里的私有角色，再用这个角色配音；可以用 `create-actor` 命令建，也可以在网站上建。

**声音克隆可以克隆明星或别人的声音吗？**
不可以。只克隆你本人或已获书面授权的声音；冒用他人声音可能侵权甚至违法。

**克隆声音配音能加情绪吗？**
可以用所选生成模式提供的语气标签（`capabilities` 里的 `tags[].label`），再配合语速和停顿。

**AI声音克隆收费吗？**
创建角色和配音都按账号额度消耗，具体以 `capabilities` 实时返回和官网说明为准。

**声音克隆配音能同时出字幕吗？**
整稿用 `voiceover.py script`，会输出 `voiceover.srt` 和逐句时间轴。

**声音克隆需要显卡吗？哪些 Agent 能用？**
不需要显卡，本地只跑 Python 3.9+ 标准库；Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 都能直接调用。

## 稿件语法

- 开头 `---` 之间每行定义一个角色：`角色名: voice=角色名称` 或 `角色名: actor_id=角色ID`（名称须和 `actors` 列表完全一致，有同名角色时改用 actor_id）；可加 `speed=`（0.25–4）、`model=expressive|standard`、`tags=标签1,标签2`、`language=`（文本语言提示）。
- 稿件里没写音色的角色，用命令行 `--voice 角色名称` 或 `--actor-id 角色ID` 统一指定。音色由服务端从角色样本读取，不再需要提供录音链接和原话。
- 正文 `[角色] 台词` 或 `[角色]：台词`；不写标签沿用上一位说话人。
- `[pause 0.6]` / `[停顿 0.6]` 插入停顿（秒）；`#` 开头的行和空行会被忽略。
- 单句超过 `capabilities` 里的 `audio.max_text_length` 会被接口拒绝，拆成短句即可。
- 每句音频缓存在 `out/lines/`，同一句同一设置再次运行直接复用；没缓存时用同一个幂等键提交，服务端返回原任务、不重复创建。要新的一版加 `--fresh`。

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

## 合规

- 只克隆你本人或已获得明确授权的声音，不模仿明星、主播、公众人物或任何未授权的人。
- 按《人工智能生成合成内容标识办法》和抖音、快手、视频号、小红书、B站等平台规则，发布时声明或标注 AI 生成内容。
- 声音属于人格权益：克隆他人声音须取得本人书面授权，并说明用途；不得用于冒充、诈骗、误导等用途。
- `scripts/miragea_audio.py` is the official client 1.3.0, shipped unchanged；`scripts/voiceover.py`（稿件拼接层）为原创，MIT 许可（见 `LICENSE.txt`）。配音与字幕能力由 Miragea 开放 API 提供。

## English Summary

- **Voice cloning voiceover (声音克隆)**: turn your own recording into a private role with `create-actor`, or use a role already in your account (`voice=NAME` / `actor_id`).
- Preview one line with the official client's `generate`, compare `expressive` vs `standard`, then voice a whole script into WAV + SRT + per-line timing.
- Authorised voices only. Pricing and limits come live from `capabilities`. Python 3.9+ stdlib, no GPU. Service: Miragea API (https://miragea.ai/v1).

**关键词**：声音克隆、克隆声音、声音复刻、AI配音、声音克隆配音、AI声音克隆、克隆声音配音、语音克隆、音色克隆、用自己的声音配音、文字转语音、字幕生成、SRT、TTS、voice cloning、voice clone、text to speech
