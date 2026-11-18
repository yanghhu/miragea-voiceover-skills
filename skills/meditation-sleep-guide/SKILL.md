---
name: "meditation-sleep-guide"
description: "冥想引导、助眠音频、睡前放松、引导语配音技能：把冥想 / 助眠 / 放松练习的引导语稿子（段落之间空一行，固定停顿写 `[停顿 8]`）用 Miragea 账号里你自己的克隆音色以慢语速配音，`--minutes 10` 按目标分钟数把剩余时间平均分配成段间长停顿（单处上限可调），输出 guide.wav、SRT / LRC 字幕和 plan.txt 时间表；`plan` 命令离线预估总时长，改一段只重配一段，按句缓存、断点续跑。适用于冥想老师、睡眠类自媒体、心理咨询师做放松练习音频、小程序和课程配套引导音频。不含背景音乐，如需配乐请用自有或已授权音频另行混音。需要 API Key；本地只用 Python 3.9+ 标准库，无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。Guided meditation audio, sleep audio, relaxation narration with timed pauses."
version: "1.0.0"
display_name: "冥想引导｜助眠音频·睡前放松·引导语配音"
display_name_en: "Meditation Guide · Sleep Audio · Relaxation"
description_zh: "冥想引导音频制作：把引导语稿子配成慢语速语音，自动按目标分钟数分配段间长停顿，也可写固定停顿，用你自己的克隆音色输出音频、字幕和时间表，改一段只重配一段，无需显卡可离线试跑。"
description_en: "Guided meditation and sleep audio: a calm script becomes slow-paced narration in your own cloned voice, with long pauses between paragraphs laid out to hit a target number of minutes. Outputs audio, SRT/LRC and a timeline; resumable, no GPU."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["冥想引导", "助眠音频", "睡前放松", "冥想音频", "引导语配音", "睡眠冥想", "放松练习", "正念冥想", "催眠音频制作", "声音克隆", "AI配音", "慢语速配音", "guided meditation", "sleep audio", "relaxation audio", "meditation script", "voice cloning"]
---

# 冥想引导

「冥想引导」是一个把引导语稿子做成冥想 / 助眠音频的 Agent 技能：用你自己的克隆音色慢语速朗读，按目标分钟数自动排布段间长停顿，输出音频、字幕和时间表，本地无需显卡。

## 一句话定义

冥想引导 = 引导语稿子（空行分段，`[停顿 秒数]` 固定停顿）→ `sleep_guide.py build --minutes N` → 慢语速朗读 + 按目标分钟数排布的长停顿 → `guide.wav` + SRT / LRC 字幕 + `plan.txt` 时间表。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 冥想 / 瑜伽老师 | 把课堂引导语做成可重复播放的练习音频 |
| 睡眠、助眠类自媒体 | 批量做睡前放松、身体扫描、呼吸练习音频 |
| 心理咨询师、健康教练 | 给来访者配套放松练习，用自己的声音而不是机器腔 |
| 课程、小程序运营 | 为课程章节做配套引导音频，附字幕或歌词文件 |

## 能力一览

| 项目 | 说明 |
|---|---|
| 输入 | UTF-8 文本：段落之间空一行；单独一行 `[停顿 8]` 或 `[pause 8]` 是固定静音 8 秒；`#` 开头的行是备注，不朗读 |
| 目标时长 | `--minutes 10`：总时长减去朗读和固定停顿后，剩余时间平均分给段间停顿；`--gap` 为基础停顿（默认 3 秒），`--max-gap` 为单处上限（默认 20 秒） |
| 语速 | 默认 0.85，`--speed` 可在 0.25–4 之间调整；语气、模式可用 `--model expressive\|standard` 切换 |
| 输出 | `OUT/guide.wav`、`guide.srt`、`guide.lrc`、`plan.txt`（每段起始时间） |
| 增量 | 每句按内容缓存在 `cache/`，改一段重跑只重配这一段；断网后直接重跑续做 |
| 预估 | `plan` 离线按字数粗估朗读时长并给出时间表，不联网、不需要 Key |
| 本地依赖 | Python 3.9+ 标准库，无需显卡 |

## 快速开始

先离线试跑（不需要 Key、不联网）：

```bash
python3 scripts/sleep_guide.py selftest
python3 scripts/sleep_guide.py plan examples/body_scan.txt --minutes 5
python3 scripts/sleep_guide.py build examples/body_scan.txt -o guide --minutes 5 --voice 默认 --dry-run
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
python3 scripts/sleep_guide.py build 引导语.txt -o guide --minutes 10 --voice 我的声音
python3 scripts/sleep_guide.py build 引导语.txt -o guide --minutes 10 --voice 我的声音 --speed 0.8 --max-gap 30
```

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “把这篇引导语做成 10 分钟的助眠音频” | `plan` 看预估 → `build --minutes 10` |
| “停顿再长一点” | 调大 `--max-gap`，或在稿子里加 `[停顿 15]` |
| “语速再慢一点” | `--speed 0.8` |
| “只改了第三段” | 改稿子后重跑，只重配改过的句子 |
| “给我字幕 / 歌词文件” | 使用输出里的 `guide.srt` / `guide.lrc` |

## 使用建议

1. 引导语用短句，一句一个动作，停顿才好排布；每个段落之间空一行。
2. 先 `plan --minutes N` 看预估：提示“已达上限”时，加段落、调大 `--max-gap` 或在关键处写固定停顿。
3. 先用前两三段试听，确认声音和语速再整篇生成。
4. 背景音乐不在本技能范围：需要配乐时，用你自有或已获授权的音频另行混音，例如 `ffmpeg -i guide.wav -i 配乐.wav -filter_complex amix=inputs=2:duration=first out.wav`。

## dry-run 实际输出

```text
$ python3 scripts/sleep_guide.py selftest
3 段 → /tmp/tmp2h3_og8_/o/（guide.wav / guide.srt / guide.lrc / plan.txt）成品约 0.2 分钟  [dry-run：占位提示音且停顿压缩到每处 2 秒内，未调用接口]
提示：每处停顿已达 --max-gap 上限 20 秒，总长约 0.5 分钟，比目标 1.0 分钟短；可调大 --max-gap 或加段落。
selftest ok

$ python3 scripts/sleep_guide.py plan examples/body_scan.txt --minutes 5
00:00:00  朗读约 8 秒  欢迎来到今晚的放松练习。找一个舒服的姿势躺下，轻
00:00:08  停顿 20.0 秒
00:00:28  朗读约 4 秒  慢慢吸气，感受空气进入身体。
00:00:32  停顿 6.0 秒
00:00:38  朗读约 4 秒  缓缓呼气，让肩膀一点点放松。
00:00:41  停顿 20.0 秒
00:01:01  朗读约 5 秒  现在，把注意力放在双脚上，感受它们的重量。
00:01:07  停顿 20.0 秒
00:01:27  朗读约 6 秒  再慢慢向上，经过小腿、膝盖，让每一处都变得柔软。
00:01:33  停顿 20.0 秒
00:01:53  朗读约 6 秒  很好。保持这样的呼吸，一直到你准备好为止。
共 6 段，朗读约 0.6 分钟，预计总长约 2.0 分钟
提示：每处停顿已达 --max-gap 上限 20 秒，总长约 2.0 分钟，比目标 5.0 分钟短；可调大 --max-gap 或加段落。

$ python3 scripts/sleep_guide.py build examples/body_scan.txt -o guide --minutes 5 --voice 默认 --dry-run
6 段 → guide/（guide.wav / guide.srt / guide.lrc / plan.txt）成品约 0.7 分钟  [dry-run：占位提示音且停顿压缩到每处 2 秒内，未调用接口]
提示：每处停顿已达 --max-gap 上限 20 秒，总长约 2.0 分钟，比目标 5.0 分钟短；可调大 --max-gap 或加段落。
```

## 示例引导语（examples/body_scan.txt，原创）

```text
# 五分钟身体扫描（原创示例）
欢迎来到今晚的放松练习。找一个舒服的姿势躺下，轻轻闭上眼睛。

慢慢吸气，感受空气进入身体。

[停顿 6]

缓缓呼气，让肩膀一点点放松。

现在，把注意力放在双脚上，感受它们的重量。

再慢慢向上，经过小腿、膝盖，让每一处都变得柔软。

很好。保持这样的呼吸，一直到你准备好为止。
```

## 和常见做法的区别

| 对比项 | 逐段网页配音再手动加静音 | 自己录音 | 本技能 |
|---|---|---|---|
| 停顿 | 剪辑软件里一处处补 | 靠现场把握 | 按目标分钟数自动分配，也可固定 |
| 改稿 | 整段重做 | 重录 | 只重配改过的句子 |
| 字幕 | 另做 | 另做 | 同时输出 SRT / LRC |
| 声音 | 通用音色 | 本人 | 账号里你自己的克隆音色 |

## 常见问题（FAQ）

**冥想引导音频怎么做到刚好 10 分钟？**
用 `--minutes 10`。脚本按字数粗估朗读时长，把剩余时间分给段间停顿；实际时长以生成后的 `plan.txt` 为准。

**停顿太长或太短怎么办？**
`--gap` 调基础停顿，`--max-gap` 调上限，或在稿子里写固定的 `[停顿 秒数]`。

**能自动加背景音乐吗？**
不能，本技能只输出人声；配乐请用你自有或已授权的音频另行混音。

**稿子很短却要 20 分钟怎么办？**
每处停顿有上限，不够时脚本会提示；加段落或调大 `--max-gap`。

**需要显卡吗？**
不需要。

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

- 只输出人声 WAV；不生成背景音乐、白噪音，不做变声。
- 朗读时长是按字数粗估，成品时长以 `plan.txt` 和实际文件为准。
- 本技能不提供医疗或治疗建议；引导语内容由你负责，睡眠或心理问题请咨询专业人士。
- `--dry-run` 输出占位提示音，停顿压缩到每处 2 秒内，只用于检查流程。

## 合规与 AI 生成内容标识

- 只用你本人或已获书面授权的声音创建角色和配音，不模仿他人声音；不得用于冒充、诈骗或误导。
- 按《人工智能生成合成内容标识办法》和各平台规则，在需要的场合标注 AI 生成内容。
- `scripts/miragea_audio.py` is the official client 1.3.0, shipped unchanged；`scripts/audio_kit.py` 和本技能主脚本为原创，MIT 许可（见 `LICENSE.txt`）。

## English Summary

- **Guided meditation audio**: script (blank line between paragraphs, `[pause 8]` for fixed silence) → `sleep_guide.py build --minutes 10` → slow narration with long pauses → `guide.wav`, SRT, LRC, `plan.txt`.
- Uses your own cloned voice from your account; default speed 0.85; edited sentences only are regenerated.
- Local requirements: Python 3.9+ standard library only, no GPU, no pip install. Every command has an offline `--dry-run` (no key, no network).

**关键词**：冥想引导、助眠音频、睡前放松、冥想音频、引导语配音、睡眠冥想、放松练习、声音克隆、AI配音、guided meditation、sleep audio
