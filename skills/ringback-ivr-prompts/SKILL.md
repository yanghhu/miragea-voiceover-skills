---
name: "ringback-ivr-prompts"
description: "彩铃制作、企业彩铃、IVR语音导航、电话提示音技能：把欢迎语、按键菜单（“咨询请按1，人工服务请按0”）、排队提示、下班留言、节假日通知等话术按 `id: 文本` 一行一条写好，用 Miragea 账号里你自己的克隆音色批量生成，按 id 命名输出电话系统常用格式：8000 / 16000 Hz 单声道，16 位 PCM 或 8 位 G.711 A-law / μ-law WAV，同时保留 24 kHz 高清母版和 prompts.csv 清单；可把指定几条拼成彩铃并按秒数循环，附 inspect 命令核对文件格式。适用于企业总机、客服中心、门店电话、呼叫中心。需要 API Key；本地只用 Python 3.9+ 标准库，无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。Ringback tone, IVR prompts, phone menu, call center voice prompts, G.711."
version: "1.0.0"
display_name: "彩铃制作｜企业彩铃·IVR语音导航·电话提示音"
display_name_en: "Ringback Tone Maker · IVR Phone Menu Prompts · Call Center Voice Prompts"
description_zh: "彩铃制作：企业彩铃和IVR语音导航一次做好，欢迎语、按键菜单等话术一行一条，用你自己的克隆音色批量生成电话提示音，导出8k/16k、PCM或A-law格式，拼出循环彩铃，可离线试跑。"
description_en: "Make company ringback tones and IVR phone-menu prompts: write the welcome, key menu and after-hours messages one per line, voice them in batch with your own cloned voice, export telephone formats (8/16 kHz, 16-bit PCM or G.711 A-law/mu-law) and join selected prompts into a ringback track."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["彩铃制作", "企业彩铃", "企业彩铃制作", "IVR语音", "IVR语音导航", "语音导航录音", "电话提示音", "总机语音", "客服语音提示", "按键菜单录音", "电话录音制作", "G.711", "A-law", "8k WAV", "声音克隆", "AI配音", "ringback tone", "IVR prompts", "phone menu", "call center", "voice prompts", "voice cloning"]
---

# 彩铃制作

「彩铃制作」是一个批量生成企业彩铃和 IVR 语音导航提示音的 Agent 技能：话术一行一条，用你自己的克隆音色生成，按 id 命名导出 8k / 16k、PCM 或 A-law / μ-law 电话格式，并能拼出循环彩铃，本地无需显卡。

## 一句话定义

彩铃制作 = 话术清单（`id: 文本`）→ `phone_prompts.py build --voice 你的角色 --rate 8000 --codec alaw` → `phone/welcome.wav`、`phone/menu.wav` …（电话格式）+ `hq/`（高清母版）+ `prompts.csv` + 可选 `ringback.wav`（彩铃）。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 企业行政 / IT | 总机欢迎语、按键菜单、转接提示，上传到 IP-PBX / 云总机 |
| 客服中心 | 排队提示、满意度邀请、节假日通知，一次生成一整套 |
| 门店 / 小微企业 | 来电彩铃：品牌口号 + 营业时间，循环播放 |
| 呼叫中心实施 | 按交换机要求导出 8 kHz A-law / μ-law 文件，`inspect` 批量核对 |

## 能力一览

| 项目 | 说明 |
|---|---|
| 输入 | `.txt` 每行 `id: 文本`（id 用字母、数字、`_`、`-`，同时作为文件名，不能重复）；或 `.csv`（列 `id,text`）；`#` 开头为注释 |
| 电话格式 | `--rate 8000\|16000`，`--codec pcm`（16 位）/ `alaw` / `ulaw`（8 位 G.711），单声道；先低通滤波再降采样，避免 8 kHz 下刺耳 |
| 母版 | `hq/id.wav`：24 kHz、16 位，留作以后换格式 |
| 清单 | `prompts.csv`：id、文本、秒数、文件路径（UTF-8 带 BOM，Excel 直接打开） |
| 彩铃 | `--ringback id1,id2`：按顺序拼接、条间 `--ringback-gap` 秒，整段重复到不超过 `--ringback-seconds` 秒，输出 `ringback.wav`（同样是所选电话格式） |
| 前后留白 | `--lead`（默认 0.2 秒）/ `--tail`（默认 0.3 秒），避免按键菜单首字被吞 |
| 核对 | `inspect 文件.wav` 显示编码、采样率、声道、位深、时长 |
| 本地依赖 | Python 3.9+ 标准库，无需显卡、无需 pip 安装；A-law / μ-law 编码为脚本自带实现 |

## 快速开始

先离线试跑（不需要 Key、不联网）：

```bash
python3 scripts/phone_prompts.py selftest
python3 scripts/phone_prompts.py check examples/company_ivr.txt
python3 scripts/phone_prompts.py build examples/company_ivr.txt -o out --codec alaw --ringback welcome,slogan --ringback-seconds 30 --dry-run
python3 scripts/phone_prompts.py inspect out/phone/menu.wav
```

正式生成需要 Miragea 的 API Key 和账号里你自己的角色（https://miragea.ai）：

```bash
export MIRAGEA_API_KEY=你的key                       # 在 https://miragea.ai/workspace/api 生成，只放环境变量，不要贴进聊天
python3 scripts/miragea_audio.py capabilities        # 当前可用模式、语气标签、单句字数上限和计费，以实时返回为准
python3 scripts/miragea_audio.py actors --limit 20   # 账号里已有的角色（名称、actor_id、语言）
# 还没有自己的角色：用本人或已获授权的 3–60 秒清晰录音创建一个私有角色（会按账号规则计费）
python3 scripts/miragea_audio.py create-actor --file 我的录音.wav --name 我的声音 --language zh
```

- Default API root is `https://miragea.ai/v1`; set `MIRAGEA_BASE_URL` (including `/v1`) only for a private deployment.
- 接口只按角色配音：`--voice 角色名称`（脚本让官方客户端按名称精确匹配）或 `--actor-id 角色ID`。旧的“参考音频 URL 直接克隆”入口服务端已移除，本技能不使用。
- 没有 Key 时所有命令都可以先加 `--dry-run` 离线跑通；不加 `--dry-run` 又没有 Key 时，脚本给出中文提示并以退出码 2 结束，不会调用接口。

```bash
python3 scripts/phone_prompts.py build 我的话术.txt -o ivr --voice 我的声音 --rate 8000 --codec alaw
python3 scripts/phone_prompts.py build 我的话术.txt -o ivr16 --voice 我的声音 --rate 16000 --codec pcm --ringback welcome,slogan
```

## 选哪种格式？

| 你的系统 | 常见要求（以系统文档为准） |
|---|---|
| 传统 / IP 交换机、呼叫中心 | 8000 Hz、单声道，G.711 A-law（国内常用）或 μ-law（北美常用），或 16 位 PCM |
| 云总机、宽带语音 | 常见 8000 或 16000 Hz、16 位 PCM WAV |
| 运营商企业彩铃 | 按运营商或代理平台的上传要求（格式、时长、审核）；本技能只生成音频文件，开通和审核需另行办理 |

不确定时先导出 `--codec pcm --rate 8000`，上传后试拨；或把 `hq/` 母版交给系统管理员转换。

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “做一套公司总机语音导航” | 按你的部门和按键写话术清单 → `build` |
| “交换机要 8k A-law” | `--rate 8000 --codec alaw` |
| “再做个 30 秒的来电彩铃” | `--ringback welcome,slogan --ringback-seconds 30` |
| “这个文件格式对吗” | `inspect 文件.wav` |
| “改一下下班提示” | 改那一行重跑，其余提示音复用缓存 |

## 话术建议

1. 菜单先说动作再说按键：“售后服务请按 2”，每层不超过 4–5 个选项。
2. 每条一个 id，id 用英文便于系统配置（`welcome`、`menu_main`、`after_hours`）。
3. 数字、电话号码、时间用汉字写出期望读法（如“九点到六点”），避免读法歧义。
4. 同一套提示音用同一个角色、同一个语速，听感统一。

## dry-run 实际输出

```text
$ python3 scripts/phone_prompts.py check examples/company_ivr.txt
  welcome        约  4.5 秒  您好，欢迎致电晴川科技，我们将竭诚为您服务。
  menu           约  6.7 秒  产品咨询请按1，售后服务请按2，查询订单请按3，人工服务请按0。
  queue          约  4.5 秒  当前坐席繁忙，请稍候，您的来电对我们很重要。
  after_hours    约  9.8 秒  您好，现在是非工作时间，我们的服务时间是周一至周五上午九点到下午六点，请在工作时间再来电。
  invalid        约  2.1 秒  输入有误，请重新选择。
  slogan         约  3.1 秒  晴川科技，让每一次沟通更简单。
6 条提示音，合计约 30.7 秒（粗估，实际以生成为准）

$ python3 scripts/phone_prompts.py build examples/company_ivr.txt -o out --codec alaw --ringback welcome,slogan --ringback-seconds 30 --dry-run
6 条提示音 → out/phone/（8000 Hz，alaw）+ hq/ + prompts.csv；彩铃 ringback.wav 21.2 秒  [dry-run：占位提示音，未调用接口]

$ python3 scripts/phone_prompts.py inspect out/phone/menu.wav
out/phone/menu.wav  alaw  8000 Hz  1 声道  8 bit  7.17 秒
```

## 示例话术（examples/company_ivr.txt，原创）

```text
# 企业总机示例（原创，公司名和按键请换成你自己的）
welcome: 您好，欢迎致电晴川科技，我们将竭诚为您服务。
menu: 产品咨询请按1，售后服务请按2，查询订单请按3，人工服务请按0。
queue: 当前坐席繁忙，请稍候，您的来电对我们很重要。
after_hours: 您好，现在是非工作时间，我们的服务时间是周一至周五上午九点到下午六点，请在工作时间再来电。
invalid: 输入有误，请重新选择。
slogan: 晴川科技，让每一次沟通更简单。
```

同目录还有 `examples/company_ivr.csv`（CSV 写法）。

## 和常见做法的区别

| 对比项 | 找录音棚 / 配音员 | 网页文字转语音 | 本技能 |
|---|---|---|---|
| 改一句 | 预约补录 | 重新生成、下载、改名 | 改一行重跑，按 id 自动命名 |
| 电话格式 | 交付后自己转 | 多为 MP3，需要再转 | 直接导出 8k / 16k、PCM / A-law / μ-law |
| 一致性 | 补录可能音色不一致 | 平台预置音色 | 全套同一个你自己的角色 |
| 核对 | 手动 | 手动 | `inspect` 显示编码、采样率、时长 |

## 常见问题（FAQ）

**企业彩铃怎么制作？**
写好欢迎语和口号，`build --ringback welcome,slogan --ringback-seconds 30` 生成 `ringback.wav`，再按运营商或云总机平台的要求上传；开通、审核和费用以平台为准。

**IVR 语音导航要什么格式？**
最常见的是 8000 Hz 单声道，G.711 A-law / μ-law 或 16 位 PCM WAV。以你的交换机或云平台文档为准，本技能都能导出。

**为什么 8 kHz 听起来不如原声？**
电话带宽本身只有约 3.4 kHz，这是正常的；脚本已先低通再降采样，减少失真。高清母版在 `hq/`。

**可以用我自己的声音吗？**
可以。在 https://miragea.ai 用本人 3–60 秒清晰录音创建私有角色（或 `create-actor` 命令）后使用。

**能生成英文提示音吗？**
可以把英文话术写进清单。效果取决于所用角色；建议用英文录音单独建一个英文角色，并先试听。

## 出问题了？

| 现象 | 处理 |
|---|---|
| `未设置环境变量 MIRAGEA_API_KEY` | `export MIRAGEA_API_KEY=...`，或先加 `--dry-run` |
| `还没有指定音色` | 加 `--voice 角色名称` 或 `--actor-id`；没有角色先 `create-actor` |
| `actor_not_found` / `ambiguous_actor_name` | 名称要和 `actors` 列表完全一致；同名角色改用 `--actor-id` |
| 401 / 403 | 检查 Key 和账号的 API 访问权限；不要把 Key 写进日志 |
| 400 / 413 | 修正参数：模式、语气标签、语速、单句字数；超长句子会被自动在标点处切短 |
| 429 | 额度不足或限流，稍后再试或补充额度 |
| 中途断网 / 超时 | 直接重跑同一条命令：已生成的句子在 `cache/` 里复用，同一句用同一个幂等键，服务端返回原任务，不重复计费创建 |

脚本退出码：0 成功；2 输入或环境问题（中文提示）。官方客户端：0 请求成功，1 任务失败，2 客户端或接口错误。

## 限制与注意事项

- 只生成音频文件，不负责开通彩铃业务或配置交换机。
- 彩铃只做整段重复，总长不超过 `--ringback-seconds`（单段本身更长时保留一段）。
- 运营商彩铃、云总机对时长、格式、内容有审核要求，上传前请核对。
- `--dry-run` 输出的是占位提示音，只用于检查流程和文件格式。

## 合规与 AI 生成内容标识

- 只用你本人或已获书面授权的声音创建角色和配音，不模仿他人声音；不得用于冒充、诈骗或误导。
- 按《人工智能生成合成内容标识办法》和各平台规则，在需要的场合标注 AI 生成内容。
- `scripts/miragea_audio.py` is the official client 1.3.0, shipped unchanged；`scripts/audio_kit.py` 和本技能主脚本为原创，MIT 许可（见 `LICENSE.txt`）。

## English Summary

- **Ringback tones and IVR prompts**: `id: text` per line → `phone_prompts.py build --voice YOUR_ROLE` → `phone/ID.wav` in telephone format (8/16 kHz mono, 16-bit PCM or 8-bit G.711 A-law / mu-law), `hq/ID.wav` 24 kHz masters, `prompts.csv`.
- `--ringback welcome,slogan --ringback-seconds 30` joins prompts into `ringback.wav`; `inspect FILE.wav` reports codec / rate / length.
- Local requirements: Python 3.9+ standard library only, no GPU, no pip install. Every command has an offline `--dry-run` (no key, no network).

**关键词**：彩铃制作、企业彩铃、企业彩铃制作、IVR语音、IVR语音导航、语音导航录音、电话提示音、总机语音、客服语音提示、按键菜单录音、G.711、A-law、声音克隆、AI配音、ringback tone、IVR prompts、phone menu、call center
