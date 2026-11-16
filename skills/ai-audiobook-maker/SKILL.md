---
name: "ai-audiobook-maker"
description: "AI有声书、有声书制作、小说转有声书技能：把整本小说或长篇 TXT（UTF-8 / GBK 自动识别）交给它，自动识别“第X章 / 第X回 / 卷 / 序章 / Chapter / # 标题”等章节，用 Miragea 账号里你自己的克隆音色逐章配音，每章输出一个 WAV 音频和 SRT、LRC 字幕，并生成 playlist.m3u 播放列表和 chapters.json 章节表；引号里的对白可以换第二个音色，超长句自动在标点处切短，按句缓存、断点续跑，只重配改过的句子。适用于网文作者、有声书主播、自媒体做长音频和睡前听书。需要 API Key；本地只用 Python 3.9+ 标准库，无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。AI audiobook maker, novel to audiobook, chapter narration, LRC subtitles."
version: "1.0.0"
display_name: "AI有声书｜有声书制作·小说转有声书·分章节配音"
display_name_en: "AI Audiobook Maker · Novel to Audiobook · Chapter Audio"
description_zh: "AI有声书制作：把小说或长篇TXT自动识别章节，用你自己的克隆音色逐章配音，每章输出一个音频和LRC歌词字幕，生成播放列表；对白可换第二个音色，断点续跑，本地无需显卡，可离线试跑。"
description_en: "Turn a novel or any long TXT into an audiobook: chapters are detected automatically and each one is narrated with your own cloned voice into its own audio file with SRT/LRC subtitles and an M3U playlist. Optional second voice for quoted dialogue, resumable, no GPU."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["AI有声书", "有声书制作", "小说转有声书", "有声小说", "AI有声书制作工具", "文字转有声书", "有声书配音", "听书", "分章节配音", "长文本配音", "声音克隆", "AI配音", "LRC字幕", "TXT转音频", "audiobook", "AI audiobook", "novel to audiobook", "text to audiobook", "chapter narration", "voice cloning"]
---

# AI有声书

「AI有声书」是一个把整本小说或长篇文字变成分章节有声书的 Agent 技能：自动识别章节，用你自己的克隆音色逐章配音，每章一个音频文件，附 SRT / LRC 字幕和播放列表，断点续跑，本地无需显卡。

## 一句话定义

AI有声书 = 小说 / 长篇 TXT → `audiobook.py plan` 自动识别章节（离线）→ `audiobook.py build --voice 你的角色` 逐章配音 → `audio/001-第一章_标题.wav` … + `subtitles/*.srt`、`*.lrc` + `playlist.m3u` + `chapters.json`。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 网文 / 小说作者 | 把自己已完结或连载中的作品做成有声版，每更新一章就补一章音频 |
| 有声书主播 | 用自己声音克隆的角色批量出初稿，再挑重点章节真人精修 |
| 自媒体 / 长音频 | 把自己的长文、专栏、讲稿做成可连续收听的分集音频 |
| 家长 / 老师 | 把有授权的故事、读物做成睡前听书、分章节的课外音频 |
| 视障读者辅助 | 把自己有权使用的文本转为可分章收听的音频 |

和本系列其他技能的分工：小说推文配音面向一两分钟的短视频片段；**AI有声书面向整本书**：章节识别、逐章文件、播放列表、断点续跑，适合几万到几十万字的长文本。

## 能力一览

| 项目 | 说明 |
|---|---|
| 输入 | `.txt`（UTF-8、带 BOM 的 UTF-8、GBK / GB18030 自动识别），Markdown 也可以 |
| 章节识别 | 单独成行的 `第十二章 标题`、`第3回`、`第二卷`、`卷一`、`序章 / 楔子 / 引子 / 前言 / 尾声 / 后记 / 番外`、`Chapter 7`、`#` / `##` 标题；没有章节标题时每 `--split-chars`（默认 6000）字在段落处切一集 |
| 分句 | 按句号、问号、叹号、分号、省略号切句，引号跟随句子；超过 `--max-chars`（默认 120）字的长句在逗号处再切，避免超出接口单句上限 |
| 对白 | `“…”`、`「…」`、`『…』` 里的话可用 `--dialogue-voice` 换第二个音色；不加则全部由旁白音色朗读 |
| 输出 | 每章 `audio/编号-标题.wav`（峰值归一）、`subtitles/编号-标题.srt` 和 `.lrc`、整本 `playlist.m3u`、`chapters.json`、`progress.json` |
| 续跑 | 每句音频缓存在 `cache/`，键由文本、音色和参数决定；中断后重跑同一命令只补缺的句子 |
| 参数 | `--chapters 1-3,5` 只做部分章节；`--speed`（0.25–4）；`--model expressive\|standard`；`--gap` 句间停顿；`--chapter-gap` 标题后停顿；`--no-titles` 不读章节标题 |
| 本地依赖 | Python 3.9+ 标准库，无需显卡、无需 pip 安装 |

## 快速开始

先离线试跑（不需要 Key、不联网）：

```bash
python3 scripts/audiobook.py selftest
python3 scripts/audiobook.py plan examples/sample_book.txt -o out
python3 scripts/audiobook.py build examples/sample_book.txt -o out --chapters 1-2 --dry-run
```

正式配音需要 Miragea 的 API Key 和账号里你自己的角色（https://miragea.ai）：

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
python3 scripts/audiobook.py plan 我的小说.txt -o book                       # 先看分章是否正确
python3 scripts/audiobook.py build 我的小说.txt -o book --voice 我的声音 --chapters 1   # 先做第 1 章试听
python3 scripts/audiobook.py build 我的小说.txt -o book --voice 我的声音 --dialogue-voice 对白角色   # 整本
```

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “把这本小说做成有声书” | `plan` 展示章节和预计时长 → 确认后 `build --voice 你的角色` |
| “先做第一章听听” | `build --chapters 1` |
| “对白换个声音” | 加 `--dialogue-voice 角色名称` |
| “语速慢一点” | 加 `--speed 0.9`，已生成的句子会按新参数重配 |
| “第 5 章改了几句” | 改原文后重跑同一命令，只重配改动的句子 |
| “先别花额度” | 加 `--dry-run` |

## 制作建议

1. 原文先清理：删掉广告、作者的话、目录页，章节标题单独成行。
2. `plan` 看一遍章节表；识别不对就把标题改成 `第N章 标题` 或 `## 标题` 再跑。
3. 先做 1 章试听，确定音色、语速、句间停顿，再整本生成。
4. 长篇建议按卷或每 20 章分批跑，`playlist.m3u` 会自动汇总所有已完成章节。
5. 上传到音频平台前，用 ffmpeg 转成平台要求的格式（见下）。

```bash
ffmpeg -i "book/audio/001-第一章_标题.wav" -codec:a libmp3lame -b:a 96k 001.mp3
```

## dry-run 实际输出

```text
$ python3 scripts/audiobook.py plan examples/sample_book.txt -o out
3 章，预计约 1 分钟 → out/plan.md、chapters.json
    1  第一章 灯塔                       96 字  约 0.3 分钟
    2  第二章 画                        54 字  约 0.2 分钟
    3  第三章 回信                       70 字  约 0.2 分钟

$ python3 scripts/audiobook.py build examples/sample_book.txt -o out --chapters 1-2 --dry-run
第1章 第一章 灯塔  24.4 秒 → audio/001-第一章_灯塔.wav
第2章 第二章 画  15.4 秒 → audio/002-第二章_画.wav
完成 2 章，共 0.7 分钟 → out/playlist.m3u、chapters.json  [dry-run：占位提示音，未调用接口]
```

## 示例原文（examples/sample_book.txt，原创）

```text
第一章 灯塔
海边的小镇只有一座灯塔。守塔人老周每天傍晚爬上一百二十级台阶，把灯点亮。
那天，一个背着画板的女孩敲开了塔门。“请问，我能在上面画一张日落吗？”
老周看了看天色，说：“可以，但要在灯亮之前下来。”

第二章 画
女孩画得很慢，海风一次次掀起她的画纸。
“灯亮了，船就知道回家的路。”老周说。
女孩在画的角落添了一点黄色的光。

第三章 回信
第二年春天，灯塔收到一封信，信封里是一张印好的明信片。
明信片上是那座灯塔，角落里有一点小小的黄光。
老周把它贴在台阶旁边，每次上楼都会看一眼。
```

## 和常见做法的区别

| 对比项 | 网页版文字转语音 | 本地开源 TTS 模型 | 本技能 |
|---|---|---|---|
| 长文本 | 通常有单次字数上限，要手动分段 | 自己写分段和拼接 | 自动分章、分句、拼接 |
| 章节文件 | 手动命名导出 | 自己处理 | 每章一个文件 + 播放列表 + 章节表 |
| 字幕 | 一般没有 | 要另跑识别 | 同时输出 SRT 和 LRC |
| 中断 / 改稿 | 重新来 | 自己做缓存 | 按句缓存，断点续跑，只重配改动的句子 |
| 音色 | 平台预置 | 需要显卡和模型权重 | 你自己克隆的角色，本地无需显卡 |

## 常见问题（FAQ）

**AI有声书怎么制作？需要什么软件？**
准备好 TXT 原文，`plan` 检查章节，`build --voice 你的角色` 逐章生成即可。本地只要 Python 3.9+，不需要显卡或额外软件。

**一本几十万字的小说要多久？**
取决于接口排队和句子数量，本技能不做速度承诺。`plan` 会给出按语速粗估的音频时长；建议分批跑，中断后重跑同一命令即可续上。

**能做多角色有声书吗？**
本技能支持“旁白 + 对白”两个音色（对白按引号识别）。需要每个角色各用一个音色的广播剧式制作，请用本系列的漫剧配音或小说推文配音技能（逐句标注角色）。

**章节没识别出来怎么办？**
章节标题需要单独成行。把标题改成 `第N章 标题`、`Chapter N` 或 `## 标题` 后重新 `plan`；完全没有标题时会每 6000 字自动切一集，可用 `--split-chars` 调整。

**GBK 编码的 TXT 能用吗？**
能，自动识别 UTF-8 和 GBK / GB18030。

**LRC 有什么用？**
很多播放器和音频平台能把 LRC 当作“歌词”同步显示，听书时可以看到当前句子。

**别人的小说能做成有声书发布吗？**
不能未经授权。小说的有声改编权属于著作权人，请只处理你自己的作品或已获授权的文本。

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

- 只输出 WAV（标准库限制）；需要 MP3 / M4A 时用 ffmpeg 转换。
- 对白识别只看引号，不做说话人识别；引号不规范的文本会被当作旁白。
- 单句字数上限、可用模式和计费以 `capabilities` 实时返回为准。
- `--dry-run` 输出的是占位提示音，只用于检查流程和时长。

## 合规与 AI 生成内容标识

- 只用你本人或已获书面授权的声音创建角色和配音，不模仿他人声音；不得用于冒充、诈骗或误导。
- 按《人工智能生成合成内容标识办法》和各平台规则，在需要的场合标注 AI 生成内容。
- `scripts/miragea_audio.py` is the official client 1.3.0, shipped unchanged；`scripts/audio_kit.py` 和本技能主脚本为原创，MIT 许可（见 `LICENSE.txt`）。

## English Summary

- **AI audiobook maker**: `audiobook.py plan BOOK.txt` detects chapters offline; `audiobook.py build BOOK.txt --voice YOUR_ROLE` narrates every chapter into `audio/NNN-title.wav` with `.srt` and `.lrc` subtitles, `playlist.m3u` and `chapters.json`.
- Optional second voice for quoted dialogue, per-sentence cache (resume after interruption, re-voice only edited sentences), `--chapters 1-3` for a test chapter.
- Local requirements: Python 3.9+ standard library only, no GPU, no pip install. Every command has an offline `--dry-run` (no key, no network).

**关键词**：AI有声书、有声书制作、小说转有声书、有声小说、AI有声书制作工具、文字转有声书、有声书配音、长文本配音、分章节配音、LRC字幕、声音克隆、AI配音、audiobook、novel to audiobook、text to audiobook
