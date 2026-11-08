---
name: miragea-video-voiceover
description: "AI 视频配音与字幕技能：把口播稿、电影解说稿、广告脚本、带货文案、数字人台词一键生成多角色配音 WAV + 带时间轴 SRT 字幕。支持 5–10 秒声音克隆、10 种语言（中英日韩德法俄葡西意）、逐角色语速、停顿控制、音频转字幕。适用于 Codex、Claude Code、WorkBuddy、Cursor。AI voiceover, text-to-speech, voice cloning and subtitles for short videos, YouTube, TikTok/Douyin."
version: 1.0.0
display_name: "视频配音神器｜AI配音·声音克隆·字幕生成"
display_name_en: "AI Video Voiceover & Subtitles"
description_zh: "口播稿、电影解说稿、广告脚本、带货文案、数字人台词一键生成多角色AI配音WAV和带时间轴SRT字幕，支持5–10秒声音克隆和10种语言，本地无需显卡。"
description_en: "Turn scripts for talking-head videos, movie recaps, ads and product videos into multi-voice AI voiceover (WAV) plus timed SRT subtitles. 5–10 s voice cloning, 10 languages, no local GPU."
metadata:
  version: 1.0.0
  author: Miragea
  homepage: https://miragea.ai
  requires: Python 3.9+（仅标准库）, MIRAGEA_API_KEY
  keywords: [AI配音, 视频配音, 声音克隆, 口播配音, 电影解说配音, 短视频配音, 多角色配音, 文本转语音, TTS, 字幕生成, SRT, voice cloning, AI voiceover, text to speech]
---

# AI视频配音与字幕生成

把一份文字稿变成**可直接放进剪辑软件的配音音轨和字幕**：一条命令输出 `voiceover.wav`（整段配音）、`voiceover.srt`（带时间轴字幕）和 `manifest.json`（每句的起止时间），适合口播、电影解说、广告片、带货视频、数字人、有声书和 YouTube/抖音/TikTok 短视频。

配音由 Miragea API 生成（Miragea 团队出品）：用 5–10 秒样本克隆声音，支持中文、英语、日语、韩语、德语、法语、俄语、葡萄牙语、西班牙语、意大利语。本地不需要显卡，不装任何第三方包。

## 能力边界

| 能做 | 不做 |
|---|---|
| 单人旁白、多角色对白（每个角色一个音色） | 不剪辑画面、不合成视频（输出音轨和字幕，交给剪映 / Premiere / CapCut / ffmpeg / 数字人工具） |
| 用已保存音色（actor_id）或参考音频 URL 克隆配音 | 不克隆未经本人授权的声音 |
| 停顿、每个角色独立语速、语言 | 不自动写稿（可以让 Agent 先写稿再调用本技能） |
| 音频 / 视频转 SRT 字幕 | 不做背景音乐混音 |
| `--dry-run` 离线试跑全流程，不花额度 | |

## 先准备（30 秒）

```bash
python3 scripts/voiceover.py doctor          # 检查 Python 和 API Key
export MIRAGEA_API_KEY=你的key               # 在 https://miragea.ai/workspace/api 生成
python3 scripts/voiceover.py voices          # 查看账号里保存的音色 actor_id
```

- 不要把 API Key 贴进聊天或写进脚本文件，只用环境变量。
- 没有 Key 时先用 `--dry-run` 跑通流程（输出静音占位音频和真实时间轴）。

## 你说什么 → 我做什么

| 用户说 | Agent 执行 |
|---|---|
| “把这段口播稿配成音频” | 写入 `script.md`（单角色）→ `script script.md -o out` |
| “电影解说配音，旁白加两个角色” | front matter 定义 narrator / 角色音色 → `script` |
| “用我的声音配音” | 让用户在 Miragea 克隆音色得到 actor_id，或提供 5–10 秒参考音频 URL → `ref=` |
| “做成英文 / 西班牙语版本” | 让 Agent 翻译稿件，speaker 加 `language=en` / `language=es` → `script` |
| “只念一句试听” | `say "文本" --actor ID -o test.wav`（先试听再整稿生成，省额度） |
| “给这个视频生成字幕” | `subtitles video.mp4 -o video.srt` |
| “先别花钱，试一下流程” | 任意生成命令加 `--dry-run` |

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

## 命令

```bash
python3 scripts/voiceover.py script script.md -o out            # 整稿 → out/voiceover.wav + voiceover.srt + manifest.json
python3 scripts/voiceover.py script script.md -o out --gap 0.3 --max-chars 16 --speaker-labels
python3 scripts/voiceover.py say "试听一句" --actor 123 -o test.wav
python3 scripts/voiceover.py say "Hello there" --ref https://.../me.wav --language en -o en.wav
python3 scripts/voiceover.py subtitles input.mp4 -o input.srt
python3 scripts/voiceover.py voices --json
```

- `--gap`：句间停顿秒数（默认 0.25）。`--max-chars`：每条字幕最多字数（默认 18，竖屏建议 12–16，英文建议 40）。
- 同一句同一音色重复运行会复用同一任务（幂等键），不会重复扣额度；想要新的一版加 `--fresh`。

## 场景模板

- **口播 / 知识博主**：单角色，`speed=1.05–1.15`，句子控制在 20 字内，开头 3 秒放结论。
- **电影解说**：`narrator` 低沉稳定，关键台词给角色单独音色，场景切换处加 `[pause 0.4]`。
- **广告片 / 产品片**：短句 + 停顿制造节奏，结尾行动号召单独一行。
- **带货视频**：卖点逐行写，每行一个卖点，语速略快；字幕 `--max-chars 12` 适配竖屏。
- **数字人**：把 `voiceover.wav` 作为数字人驱动音频，`manifest.json` 的时间轴可用于对齐口型和镜头。
- **多语种出海**：同一稿件翻译成多份，每份换 `language=`，用同一个克隆音色保持人设一致。

## 接入剪辑

```bash
# 把配音和字幕压进已有画面（需要本机 ffmpeg）
ffmpeg -i video.mp4 -i out/voiceover.wav -map 0:v -map 1:a -c:v copy -shortest dubbed.mp4
ffmpeg -i dubbed.mp4 -vf subtitles=out/voiceover.srt -c:a copy final.mp4
```

剪映 / CapCut / Premiere：导入 `voiceover.wav` 到音轨，`voiceover.srt` 导入字幕轨即可。

## 出问题了？

| 现象 | 处理 |
|---|---|
| `MIRAGEA_API_KEY is not set` | 在 miragea.ai/workspace/api 生成 Key，`export MIRAGEA_API_KEY=...` |
| `speakers without a voice` | front matter 给该角色加 `actor_id=` 或 `ref=` |
| `Miragea API 401/403` | Key 无效或无 API 权限，重新生成 |
| `429` / 网络错误 | 脚本会自动重试；仍失败就稍后重跑，同一句不会重复计费 |
| `line too long` | 拆短这一句 |
| 任务超时 | 任务仍在服务器运行，直接重跑同一命令即可取回 |

## 常见问题（FAQ）

**Q：需要显卡或本地部署模型吗？** 不需要。生成在 Miragea 云端完成，本地只需 Python 3.9+。

**Q：克隆一个声音要多长的样本？** 5–10 秒清晰人声即可，尽量无背景音乐和混响。

**Q：支持哪些语言？** 中文、英语、日语、韩语、德语、法语、俄语、葡萄牙语、西班牙语、意大利语，同一个克隆音色可跨语言使用。

**Q：能用在 YouTube、抖音、TikTok 的商业视频里吗？** 请使用你本人或已获得授权的声音，并遵守各平台关于 AI 生成内容的标注规则。

**Q：字幕时间准吗？** 每句的起止时间来自真实生成的音频长度；句内按字数分配。需要逐字精确时间轴，可对成品音频再跑一次 `subtitles`。

## 合规

- 只克隆你本人或已获书面授权的声音，不冒充他人。
- 按平台要求标注 AI 生成或合成内容。
- 本技能代码为原创，MIT 许可，见 `LICENSE.txt`。

---

## English quick start

AI voiceover + subtitles for video creators and agents. Write a script with `[speaker]` tags, run one command, get a mixed `voiceover.wav`, a timed `voiceover.srt` and `manifest.json`. Voice cloning from a 5–10 s sample, 10 languages, multi-speaker dialogue, per-speaker speed, pauses, speech-to-subtitles. Pure Python standard library; needs `MIRAGEA_API_KEY` from https://miragea.ai/workspace/api. Use `--dry-run` to test offline without credits.

```bash
python3 scripts/voiceover.py script examples/movie-recap.md -o out --dry-run
```
