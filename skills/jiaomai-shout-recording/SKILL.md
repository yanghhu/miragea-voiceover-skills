---
name: "jiaomai-shout-recording"
description: "叫卖录音、喊话录音、店铺促销广播技能：把地摊清仓、水果摊、早餐铺、门店促销、超市闭店广播、旧物回收等叫卖词一行一句写好，用 Miragea 账号里你自己的克隆音色生成响亮清晰的喊话录音，输出单遍 single.wav 和自动循环到指定时长（默认 10 分钟）的 loop.wav，可在每遍前加“叮咚”提示音，峰值归一更响亮，支持每句语气标签和语速；附 6 个原创场景模板，ffmpeg 一条命令转 MP3 拷进喇叭、扩音器、喊话器。需要 API Key；本地只用 Python 3.9+ 标准库，无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。Hawker shout recording, shop announcement, promo broadcast, loudspeaker loop."
version: "1.0.0"
display_name: "叫卖录音｜地摊叫卖·喊话录音·店铺促销广播"
display_name_en: "Hawker Shout Recording · Stall Calls · Shop Announcements"
description_zh: "叫卖录音制作：输入地摊、水果摊、门店促销或超市广播的叫卖词，用你自己的克隆音色生成响亮清晰的喊话录音，自动循环成10分钟等长音频，可加叮咚提示音，导出给喇叭和扩音器播放，可离线试跑。"
description_en: "Make hawker / shop announcement recordings: type the slogans for a street stall, fruit stand, shop promotion or supermarket announcement, voice them with your own cloned voice, and get a loud single pass plus a ready-to-loop 10-minute track (optional ding-dong chime) for loudspeakers and megaphones."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["叫卖录音", "叫卖录音制作", "喊话录音", "喊话录音制作", "地摊叫卖录音", "店铺广播", "促销广播", "超市广播", "门店促销口播", "喇叭录音", "扩音器录音", "循环播放", "带货叫卖", "声音克隆", "AI配音", "文字转语音", "hawker recording", "shop announcement", "promo broadcast", "loudspeaker", "voice cloning"]
---

# 叫卖录音

「叫卖录音」是一个把叫卖词变成喇叭可循环播放音频的 Agent 技能：一行一句写好叫卖词，用你自己的克隆音色生成响亮的喊话录音，自动循环成 10 分钟等长音频，可加“叮咚”提示音，本地无需显卡。

## 一句话定义

叫卖录音 = 叫卖词（一行一句）→ `shout_loop.py build --voice 你的角色` → `single.wav`（单遍，先试听）+ `loop.wav`（循环到 10 分钟，直接拷进喇叭）→ ffmpeg 转 MP3。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 摆摊 / 夜市 | 清仓甩卖、水果、小吃、玩具的循环叫卖 |
| 门店 / 便利店 | 店庆、会员日、新品上市的门口促销口播 |
| 超市 / 商场 | 闭店提醒、特价播报、寻物寻人广播（加“叮咚”提示音） |
| 流动商贩 / 回收 | 车载喇叭的回收、上门服务喊话 |
| 社区 / 物业 | 活动通知、防火防汛提示的循环播报 |

## 能力一览

| 项目 | 说明 |
|---|---|
| 输入 | `.txt` 一行一句；`#` 开头为注释；`[停顿 2]` / `[pause 2]` 插入停顿；行首 `(激昂)` 等写语气标签（标签名取 `capabilities` 返回的列表）；也可 `--text "叫卖词"` 直接给 |
| 单遍 | `single.wav`：开头静音 `--lead`、可选叮咚 `--chime`、句间停顿 `--gap`，峰值归一到 `--peak`（默认 -1 dBFS，更响亮） |
| 循环 | `loop.wav`：整遍重复，遍与遍之间 `--loop-gap` 秒，总长不少于 `--loop-minutes`（默认 10 分钟；设 0 只出单遍） |
| 记录 | `script.txt`（本次叫卖词）、`info.json`（单遍时长、循环遍数、参数） |
| 模板 | `templates` 列出 6 个原创场景模板，`templates -o tpl` 保存成 txt 再改 |
| 语速 | `--speed` 0.25–4；叫卖通常 1.1–1.2 听起来更有劲 |
| 本地依赖 | Python 3.9+ 标准库，无需显卡、无需 pip 安装 |

## 快速开始

先离线试跑（不需要 Key、不联网）：

```bash
python3 scripts/shout_loop.py selftest
python3 scripts/shout_loop.py templates
python3 scripts/shout_loop.py check examples/stall_clearance.txt --loop-minutes 10
python3 scripts/shout_loop.py build examples/stall_clearance.txt -o out --loop-minutes 3 --dry-run
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
python3 scripts/shout_loop.py build 我的叫卖词.txt -o shout --voice 我的声音 --speed 1.15
python3 scripts/shout_loop.py build examples/supermarket_closing.txt -o close --voice 我的声音 --chime --loop-minutes 5
python3 scripts/shout_loop.py build --text "新鲜草莓到货，十五块一盒！" -o berry --voice 我的声音 --loop-minutes 10
```

## 拷进喇叭 / 扩音器

多数喊话器、扩音器、车载喇叭从 U 盘或 TF 卡播放 MP3（具体格式看设备说明书）：

```bash
ffmpeg -i out/loop.wav -codec:a libmp3lame -b:a 128k 叫卖.mp3
```

设备支持“单曲循环”时，拷 `single.wav` 转出的 MP3 即可；不支持时用 `loop.wav`。

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “帮我做个地摊清仓的叫卖录音” | 按你的商品和价格写叫卖词 → `build --voice 你的角色` |
| “要循环半小时的” | `--loop-minutes 30` |
| “超市广播那种，前面有叮咚” | `--chime`，语速保持 1.0 |
| “再快一点、更有劲” | `--speed 1.2`，或在句首加语气标签 |
| “先看看多长” | `check` |

## 写叫卖词的建议

1. 每句不超过 20 字，先喊“是什么”，再喊“多少钱”，最后喊“在哪儿 / 多久”。
2. 价格用汉字或阿拉伯数字都可以，读法有歧义时写成汉字（如“十元三件”）。
3. 3–5 句一遍最合适，太长路过的人听不全。
4. 不写“全网最低”“绝对正品”等夸大、绝对化用语，遵守广告法和当地市容管理规定，注意音量和时段。

## dry-run 实际输出

```text
$ python3 scripts/shout_loop.py check examples/stall_clearance.txt --loop-minutes 10
3 句，单遍约 13.6 秒（粗估）；循环 39 遍 ≈ 10.1 分钟
  走过路过不要错过，清仓处理，全场十元三件！
  款式多多，先到先挑，挑到就是赚到！
  [停顿 0.8 秒]
  最后几天，卖完就收摊，快来看一看！

$ python3 scripts/shout_loop.py build examples/stall_clearance.txt -o out --loop-minutes 3 --dry-run
单遍 13.9 秒 → out/single.wav；循环 12 遍共 3.1 分钟 → loop.wav  [dry-run：占位提示音，未调用接口]
```

## 示例叫卖词（examples/stall_clearance.txt，原创）

```text
# 地摊清仓（示例，改成你自己的商品和价格）
走过路过不要错过，清仓处理，全场十元三件！
款式多多，先到先挑，挑到就是赚到！
[停顿 0.8]
最后几天，卖完就收摊，快来看一看！
```

同目录还有 `examples/supermarket_closing.txt`（超市闭店广播）。

## 和常见做法的区别

| 对比项 | 自己对着喇叭录 | 网页文字转语音 | 本技能 |
|---|---|---|---|
| 声音 | 自己的声音，但要反复录 | 平台预置音色 | 你自己克隆的角色，改词不用重录 |
| 循环 | 喇叭单曲循环 | 下载后自己剪 | 直接出 10 分钟等长循环文件 |
| 提示音 | 无 | 一般无 | `--chime` 内置合成的叮咚提示音，无版权素材 |
| 改词 | 全部重录 | 重新生成下载 | 只重配改动的句子（按句缓存） |

## 常见问题（FAQ）

**叫卖录音怎么制作？要下载什么软件？**
不用下载专门软件。写好叫卖词，运行 `build --voice 你的角色` 就得到 WAV，再用 ffmpeg 转 MP3 拷进喇叭。本地只要 Python 3.9+。

**能用我自己的声音吗？**
能，而且推荐。在 https://miragea.ai 用本人 3–60 秒清晰录音创建私有角色（或 `create-actor` 命令），之后用这个角色生成。

**有没有现成的叫卖词？**
`templates` 有 6 个原创场景模板，改成你自己的商品和价格即可。

**音量不够大怎么办？**
文件已峰值归一到 -1 dBFS；再响需要调喇叭音量。不建议把 `--peak` 设为 0 以上，会削波失真。

**可以做超市广播、寻人寻物广播吗？**
可以，加 `--chime`，语速保持 1.0 左右，循环时长按需要设置。

**需要显卡吗？哪些 Agent 能用？**
不需要显卡。Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 等能运行 Python 的 Agent 都能用。

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

- 只输出 WAV；喇叭需要 MP3 时用 ffmpeg 转换。
- 循环文件只做整遍重复，不会截断半句。
- 语气标签必须是 `capabilities` 里所选模式提供的标签名，否则接口返回 400。
- `--dry-run` 输出的是占位提示音，只用于检查流程和时长。

## 合规与 AI 生成内容标识

- 只用你本人或已获书面授权的声音创建角色和配音，不模仿他人声音；不得用于冒充、诈骗或误导。
- 按《人工智能生成合成内容标识办法》和各平台规则，在需要的场合标注 AI 生成内容。
- `scripts/miragea_audio.py` is the official client 1.3.0, shipped unchanged；`scripts/audio_kit.py` 和本技能主脚本为原创，MIT 许可（见 `LICENSE.txt`）。

## English Summary

- **Hawker / shop announcement recordings**: one slogan per line → `shout_loop.py build --voice YOUR_ROLE` → `single.wav` (one pass) and `loop.wav` (whole passes repeated to `--loop-minutes`, default 10).
- `--chime` adds a synthesised ding-dong before each pass, peak normalised for loudspeakers; per-line tone tags `(tag)`; 6 original templates (`templates`).
- Local requirements: Python 3.9+ standard library only, no GPU, no pip install. Every command has an offline `--dry-run` (no key, no network).

**关键词**：叫卖录音、叫卖录音制作、喊话录音、地摊叫卖录音、店铺广播、促销广播、超市广播、门店促销口播、喇叭录音、扩音器、循环播放、声音克隆、AI配音、hawker recording、shop announcement、loudspeaker
