---
name: "dictation-audio"
description: "听写音频、单词听写、英语单词朗读、词语听写技能：老师或家长把语文词语、英语单词或句子一行一个写好（可写 `apple | 苹果`），自动播报“第1个 / Number one”，每个词读 1–5 遍、遍间停顿、留出可调的书写时间，用 Miragea 账号里你自己的克隆音色生成整段 dictation.wav；支持只读中文意思写英文（英汉互译听写）、按单元分节、按种子打乱顺序，同时输出按播放顺序编号的 answer_key.txt 答案和 LRC / SRT 时间轴。适用于课堂听写、家庭作业、单词复习、考前默写。需要 API Key；本地只用 Python 3.9+ 标准库，无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。Dictation audio, spelling test, word list audio, English vocabulary."
version: "1.0.0"
display_name: "听写音频｜单词听写·英语单词朗读·词语听写"
display_name_en: "Dictation Audio · English Words · Chinese Words"
description_zh: "听写音频一键生成：把语文词语或英语单词表一行一个写好，自动编号、每词读两遍、留出书写时间，用老师或家长自己的克隆音色生成整段听写音频，附答案和LRC字幕，可打乱顺序，可离线试跑。"
description_en: "Generate dictation audio from a word list: numbered items, each read twice with writing time, voiced with the teacher's or parent's own cloned voice, plus an answer key and LRC timeline. Chinese words, English words (or English-Chinese meaning), sentences; optional shuffle."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["听写音频", "听写音频一键生成", "单词听写", "英语单词听写", "词语听写", "生字听写", "英语单词朗读", "单词朗读", "听写软件", "默写", "课堂听写", "家庭作业", "英汉互译", "声音克隆", "AI配音", "LRC", "dictation audio", "spelling test", "word list audio", "vocabulary", "voice cloning"]
---

# 听写音频

「听写音频」是一个把词表一键变成整段听写音频的 Agent 技能：自动编号、每词读两遍、留出书写时间，用老师或家长自己的克隆音色朗读，附按播放顺序编号的答案和 LRC 时间轴，本地无需显卡。

## 一句话定义

听写音频 = 词表（一行一个，可写 `词 | 提示`）→ `dictation.py build --voice 你的角色` → `dictation.wav`（“第1个”+ 读两遍 + 书写停顿）+ `answer_key.txt`（按播放顺序的答案）+ `dictation.lrc` / `dictation.srt`。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 小学语文老师 | 每课生字词听写，课堂直接播放，老师可以巡视 |
| 英语老师 | 单词听写、英汉互译听写（读中文写英文）、句子听写 |
| 家长 | 孩子在家自主听写，家长对着答案批改 |
| 学生自学 | 考前单词复习，打乱顺序多做几遍 |
| 培训机构 | 每个单元批量生成听写音频，统一老师声音 |

## 能力一览

| 项目 | 说明 |
|---|---|
| 输入 | `.txt` 一行一个词条，可写 `词条 \| 提示`（如 `apple \| 苹果`、`春天 \| 春天的春`），也可以是整句；`== 第一单元 ==` 开始新的一节（会读出节名）；`#` 开头为注释 |
| 朗读方式 | `--say word`（读词条，默认）/ `hint`（只读提示，如读中文写英文）/ `both`（先读词条再读提示） |
| 编号 | `--number zh`（“第1个”，默认）/ `en`（“Number one.”）/ `none` |
| 重复与停顿 | `--repeat` 每个读几遍（1–5，默认 2）；`--repeat-gap` 遍间停顿；`--gap` 每个词条后的书写时间（默认 6 秒） |
| 顺序 | `--shuffle` 每节内打乱，`--seed` 固定顺序；答案按实际播放顺序编号 |
| 语言 | `--language en` 作为词条的语言提示传给接口；编号、提示、节名用 `--hint-language`（默认 zh）|
| 输出 | `dictation.wav`、`answer_key.txt`、`dictation.lrc`、`dictation.srt`、`info.json`；每个词和编号只生成一次，存在 `cache/` 复用 |
| 本地依赖 | Python 3.9+ 标准库，无需显卡、无需 pip 安装 |

## 快速开始

先离线试跑（不需要 Key、不联网）：

```bash
python3 scripts/dictation.py selftest
python3 scripts/dictation.py check examples/english_words.txt --repeat 2 --gap 6
python3 scripts/dictation.py build examples/english_words.txt -o out --say word --number en --language en --shuffle --seed 7 --dry-run
python3 scripts/dictation.py build examples/chinese_words.txt -o out_zh --gap 8 --dry-run
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
python3 scripts/dictation.py build 第三课词语.txt -o d3 --voice 王老师 --speed 0.9 --gap 8
python3 scripts/dictation.py build unit1.txt -o u1 --voice 王老师 --say hint --number zh     # 读中文，写英文
python3 scripts/dictation.py build unit1.txt -o u1_en --voice 英文角色 --language en --number en --shuffle --seed 3
```

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “把这课生字做成听写音频” | 整理词表 → `build --voice 你的角色` |
| “每个读三遍，多留点时间” | `--repeat 3 --gap 10` |
| “读中文让孩子写英文” | `--say hint` |
| “顺序打乱，答案也给我” | `--shuffle --seed 任意数字`，答案在 `answer_key.txt` |
| “低年级，读慢一点” | `--speed 0.85` |

## 使用建议

1. 一次听写 10–20 个词条为宜，按单元用 `== 单元名 ==` 分节。
2. 多音字、同音字用提示消歧：`长 | 长短的长`，并用 `--say both`。
3. 低年级 `--gap 8` 以上；英语句子听写 `--repeat 3`。
4. 同一份词表换 `--seed` 可以得到不同顺序的多套听写，答案各自对应。
5. 英文单词效果取决于角色：建议用英文录音单独建一个英文角色，并加 `--language en`，先试听。

## dry-run 实际输出

```text
$ python3 scripts/dictation.py check examples/english_words.txt --repeat 2 --gap 6
5 个词条，每个读 2 遍、留 6 秒书写 → 全长约 0.9 分钟（粗估）
  == Unit 1 ==
   1. apple  | 苹果
   2. library  | 图书馆
   3. different  | 不同的
  == Unit 2 ==
   4. tomorrow  | 明天
   5. beautiful  | 美丽的

$ python3 scripts/dictation.py build examples/english_words.txt -o out --say word --number en --language en --shuffle --seed 7 --dry-run
5 个词条，1.0 分钟 → out/dictation.wav + answer_key.txt + dictation.lrc  [dry-run：占位提示音，未调用接口]

$ python3 scripts/dictation.py build examples/chinese_words.txt -o out_zh --gap 8 --dry-run
5 个词条，1.1 分钟 → out_zh/dictation.wav + answer_key.txt + dictation.lrc  [dry-run：占位提示音，未调用接口]
```

## 示例词表（examples/english_words.txt，原创）

```text
# 英语单词听写示例（原创词表）
== Unit 1 ==
apple | 苹果
library | 图书馆
different | 不同的
== Unit 2 ==
tomorrow | 明天
beautiful | 美丽的
```

同目录还有 `examples/chinese_words.txt`（语文词语）。

## 和常见做法的区别

| 对比项 | 老师现场念 | 单词 App 跟读 | 本技能 |
|---|---|---|---|
| 准备 | 每次现场念、难以统一节奏 | 词库固定，难放自己的词表 | 任意词表，一键生成 |
| 节奏 | 靠人掌握 | 一般不留书写时间 | 编号、重复、书写停顿都可调 |
| 答案 | 另写 | 无 | 按播放顺序自动编号的答案 |
| 声音 | 老师本人 | 平台音色 | 老师本人克隆的角色 |
| 多套试卷 | 重新念 | — | `--shuffle --seed` 一键多套 |

## 常见问题（FAQ）

**听写音频怎么一键生成？**
词表一行一个，运行 `build --voice 你的角色`，得到 `dictation.wav` 和答案。本地只要 Python 3.9+。

**能做英语单词听写吗？**
能。`--language en` 作为语言提示传给接口；英文发音效果取决于所用角色，建议用英文录音单独建一个英文角色并先试听。

**能只读中文意思、让学生写英文吗？**
能，词表写 `apple | 苹果`，加 `--say hint`。

**打乱顺序后怎么对答案？**
`answer_key.txt` 按实际播放顺序编号；同一个 `--seed` 每次顺序相同。

**可以在课堂上用老师自己的声音吗？**
可以。老师用本人 3–60 秒录音在 https://miragea.ai 创建私有角色（或 `create-actor` 命令）后使用。

**需要显卡吗？**
不需要，只跑 Python 标准库。

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

- 只输出 WAV；需要 MP3 时用 ffmpeg 转：`ffmpeg -i out/dictation.wav -b:a 96k 听写.mp3`。
- 不做发音评测或自动批改，答案用于人工核对。
- 语言提示是否生效、外语发音效果以接口和所选角色为准；可用语言以 `capabilities` 为准。
- `--dry-run` 输出的是占位提示音，只用于检查流程和时长。

## 合规与 AI 生成内容标识

- 只用你本人或已获书面授权的声音创建角色和配音，不模仿他人声音；不得用于冒充、诈骗或误导。
- 按《人工智能生成合成内容标识办法》和各平台规则，在需要的场合标注 AI 生成内容。
- `scripts/miragea_audio.py` is the official client 1.3.0, shipped unchanged；`scripts/audio_kit.py` 和本技能主脚本为原创，MIT 许可（见 `LICENSE.txt`）。

## English Summary

- **Dictation audio maker**: a word list (`word | hint` per line, `== Unit ==` sections) → `dictation.py build --voice YOUR_ROLE` → `dictation.wav` with item numbers, repeats and writing pauses, plus `answer_key.txt` in play order and `dictation.lrc` / `.srt`.
- `--say word|hint|both` (e.g. read the Chinese meaning, pupils write the English word), `--shuffle --seed`, `--language en`.
- Local requirements: Python 3.9+ standard library only, no GPU, no pip install. Every command has an offline `--dry-run` (no key, no network).

**关键词**：听写音频、听写音频一键生成、单词听写、英语单词听写、词语听写、生字听写、英语单词朗读、单词朗读、默写、课堂听写、英汉互译、声音克隆、AI配音、dictation audio、spelling test、vocabulary
