---
name: koubo-ai-voiceover
description: "知识口播、财经口播、情感口播一键配音：用自己5–10秒声音克隆出口播音色，口播稿直接生成配音WAV和竖屏SRT字幕，语速、停顿可控，不用对着镜头反复录。适用于抖音、视频号、小红书、B站、YouTube口播博主。"
version: 1.0.0
display_name: "口播配音神器｜AI口播稿配音·声音克隆·字幕"
display_name_en: "Talking-Head AI Voiceover"
description_zh: "知识口播、财经口播、情感口播一键配音：用自己5–10秒声音克隆出口播音色，口播稿直接生成配音WAV和竖屏SRT字幕，语速、停顿可控，不用对着镜头反复录。适用于抖音、视频号、小红书、B站、YouTube口播博主。"
description_en: "One-command AI voiceover for talking-head scripts: clone your own voice from 5–10 s of audio and get voiceover WAV plus vertical-video SRT subtitles for Douyin, Shorts and YouTube."
metadata:
  version: 1.0.0
  author: Miragea
  homepage: https://miragea.ai
  requires: Python 3.9+（仅标准库）, MIRAGEA_API_KEY
  keywords: [口播配音, AI口播, 口播稿配音, 声音克隆, 知识博主配音, 竖屏字幕, 文字转语音]
---

# 口播配音神器

写好口播稿，不用开麦、不用反复重录：用你自己的克隆声音一键生成口播配音和竖屏字幕。说错一个字只改一行字重新生成，适合每天更新的知识、财经、情感、职场口播博主。

一条命令输出三样东西：`voiceover.wav`（整段配音）、`voiceover.srt`（带时间轴字幕）、`manifest.json`（每句起止时间）。支持 5–10 秒声音克隆，中文、英语、日语、韩语、德语、法语、俄语、葡萄牙语、西班牙语、意大利语 10 种语言，本地无需显卡。

## 能力边界

| 能做 | 不做 |
|---|---|
| 单人或多角色配音、停顿、逐角色语速 | 不剪辑画面、不合成视频（交给剪映 / CapCut / Premiere / ffmpeg） |
| 声音克隆（已保存音色或参考音频） | 不克隆未经授权的声音 |
| 配音同时生成 SRT 字幕和时间轴 | 不自动写稿（可先让 Agent 按下方要点写稿） |
| 已有音频 / 视频转字幕 | 不加背景音乐 |

## 先准备（30 秒）

```bash
python3 scripts/voiceover.py doctor        # 检查 Python 3.9+ 和 API Key
export MIRAGEA_API_KEY=你的key             # 在 https://miragea.ai/workspace/api 生成，只放环境变量，不要贴进聊天
python3 scripts/voiceover.py voices        # 查看已保存音色的 actor_id
```

没有 Key 也能先试：所有生成命令加 `--dry-run`，离线跑通全流程（静音占位音频 + 真实时间轴），不耗额度。

## 一条命令

```bash
python3 scripts/voiceover.py script examples/example.md -o out --preset koubo --dry-run   # 先离线试跑
python3 scripts/voiceover.py script 你的稿件.md -o out --preset koubo                     # 正式生成
```

## 你说什么 → 我做什么

| 用户说 | Agent 执行 |
|---|---|
| “把这篇口播稿配成音频” | 按下方模板写稿 → `script 稿件.md -o out --preset koubo` |
| “用我自己的声音” | 在 Miragea 用 5–10 秒录音克隆音色拿到 actor_id，或给参考音频 URL |
| “语速快一点，更有节奏” | 角色加 `speed=1.1`，或句子拆得更短 |
| “先听一句看看像不像” | `say "开头第一句" --actor ID -o test.wav` |
| “第三句说错了” | 只改那一行再跑一次，其余句子复用不扣额度 |

## 口播写稿要点

1. **前 3 秒给结论**：第一句直接抛结果或反常识观点，不要“大家好我是……”。
2. **一行一句，一句不超过 20 字**：配音更自然，字幕也刚好一屏。
3. **口语化**：把“因此”换成“所以”，把长定语拆开。
4. **关键处停顿**：重点前加 `[pause 0.3]`，留给观众反应。
5. **结尾一个动作**：只说一件事（关注、评论某个问题），不要连说三个。

预设 `--preset koubo`：句间 0.15 秒、字幕每条 14 字，适配 9:16 竖屏。

## 示例稿件（examples/example.md）

```markdown
---
me: actor_id=YOUR_ACTOR_ID speed=1.08
---
# 知识口播示例：把 actor_id 换成你的克隆音色
[me] 90%的人存不下钱，不是因为赚得少。
[pause 0.3]
是因为钱一到账，就先花了。
今天教你一个最笨、但最管用的办法：
发工资当天，先把三成转进一个看不见的账户。
剩下的，才是这个月能花的钱。
你现在每个月能存下几成？评论区说说。
```

## 接入剪辑

```bash
ffmpeg -i 画面.mp4 -i out/voiceover.wav -map 0:v -map 1:a -c:v copy -shortest 配音版.mp4
ffmpeg -i 配音版.mp4 -vf subtitles=out/voiceover.srt -c:a copy 成片.mp4
```

剪映 / CapCut：音频轨导入 `voiceover.wav`，字幕轨导入 `voiceover.srt`。

## 稿件语法（通用）

- 开头 `---` 之间定义角色：`角色名: actor_id=音色ID` 或 `角色名: ref=参考音频URL ref_text="样本原文"`，可加 `speed=`（0.25–4）、`language=`（zh/en/ja/ko/de/fr/ru/pt/es/it）。
- 正文 `[角色] 台词` 或 `[角色]：台词`；不写标签沿用上一位说话人。
- `[pause 0.6]` 或 `[停顿 0.6]` 插入停顿；`#` 开头和 `<!-- -->` 注释会被忽略。
- 同一句同一音色重复生成会复用任务、不重复扣额度；要新的一版加 `--fresh`。

## 出问题了？

| 现象 | 处理 |
|---|---|
| `MIRAGEA_API_KEY is not set` | 去 miragea.ai/workspace/api 生成 Key 并 `export` |
| `speakers without a voice` | 给该角色补 `actor_id=` 或 `ref=` |
| `401 / 403` | Key 无效或没开 API 权限，重新生成 |
| `429` / 网络错误 | 自动重试；仍失败稍后重跑，同一句不会重复计费 |
| `line too long` | 把这一句拆短 |

## 合规

- 只克隆你本人或已获授权的声音，不模仿明星、主播或他人声音。
- 按抖音、视频号、快手、B站、YouTube 等平台规则标注 AI 生成内容。
- 代码原创，MIT 许可（`LICENSE.txt`）。配音能力由 Miragea API 提供（Miragea 团队出品）。

## 常见问题（FAQ）

**Q：口播配音需要自己录音吗？** 不需要整段录音。只需一次 5–10 秒清晰录音克隆音色，之后都用文字生成；也可以直接用已保存的音色。

**Q：需要显卡或部署模型吗？** 不需要，生成在 Miragea 云端完成，本地只要 Python 3.9+。

**Q：支持哪些 AI Agent？** Codex、Claude Code、WorkBuddy、Cursor 等能运行 Python 脚本的 Agent 都可以。

**Q：字幕怎么对齐？** 每句起止时间来自实际生成的音频长度；需要更精细的时间轴，对成品再跑 `subtitles`。

**Q：能做多语种版本吗？** 可以，同一个克隆音色可以说 10 种语言，翻译稿件后设置 `language=` 即可。
