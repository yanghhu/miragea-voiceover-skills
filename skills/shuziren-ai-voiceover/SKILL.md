---
name: shuziren-ai-voiceover
description: "为数字人、虚拟主播、AI分身生成驱动音频：用本人5–10秒声音克隆音色，口播稿一键生成干净人声WAV、SRT字幕和逐句时间轴JSON，可直接导入HeyGen、硅基智能、腾讯智影、剪映数字人等工具驱动口型。"
version: 1.0.0
display_name: "数字人配音｜数字人口播驱动音频·声音克隆·字幕"
display_name_en: "Digital Human AI Voiceover"
description_zh: "为数字人、虚拟主播、AI分身生成驱动音频：用本人5–10秒声音克隆音色，口播稿一键生成干净人声WAV、SRT字幕和逐句时间轴JSON，可直接导入HeyGen、硅基智能、腾讯智影、剪映数字人等工具驱动口型。"
description_en: "Generate clean driving audio for digital humans and AI avatars: cloned voice, WAV, SRT subtitles and per-line timeline JSON for HeyGen and similar lip-sync tools."
metadata:
  version: 1.0.0
  author: Miragea
  homepage: https://miragea.ai
  requires: Python 3.9+（仅标准库）, MIRAGEA_API_KEY
  keywords: [数字人配音, 数字人口播, AI数字人, 虚拟主播配音, 数字人驱动音频, 声音克隆, AI分身]
---

# 数字人配音

数字人像不像，一半看声音。用你本人的克隆音色生成干净无背景的人声，作为数字人的驱动音频；同时输出字幕和每句时间轴，方便对口型、切镜头、加花字。

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
python3 scripts/voiceover.py script examples/example.md -o out --preset shuziren --dry-run   # 先离线试跑
python3 scripts/voiceover.py script 你的稿件.md -o out --preset shuziren                     # 正式生成
```

## 你说什么 → 我做什么

| 用户说 | Agent 执行 |
|---|---|
| “给我的数字人生成口播音频” | `script 稿件.md -o out --preset shuziren`，用 `out/voiceover.wav` 驱动 |
| “声音要和本人一样” | 用本人 5–10 秒清晰录音克隆音色（无背景音乐、无混响） |
| “分镜头生成” | 每个镜头一份稿件，分别输出，逐段导入数字人工具 |
| “要对口型的时间轴” | 读取 `out/manifest.json` 中每句 start / end |
| “做英文版数字人” | `language=en`，同一克隆音色跨语言 |

## 数字人音频要点

1. **驱动音频要干净**：不要加背景音乐，音乐在剪辑阶段再铺。
2. **句子短、停顿匀**：口型更稳，`--preset shuziren` 句间 0.2 秒。
3. **长视频分段**：每段 30–60 秒一份稿件，数字人工具处理更快、出错好返工。
4. **本人授权**：数字人形象和声音都要本人授权，平台发布时标注 AI 生成。
5. **时间轴复用**：`manifest.json` 可用于自动加花字、切换镜头。

## 示例稿件（examples/example.md）

```markdown
---
me: actor_id=YOUR_CLONED_VOICE_ID speed=1.0
---
# 数字人口播示例（一段 = 一个镜头）
[me] 大家好，这是我的数字分身。
今天用一分钟，讲清楚一个问题：
为什么同样的产品，别人的视频卖得比你好？
[pause 0.3]
答案通常不在画面，而在前三秒说了什么。
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

**Q：数字人配音需要自己录音吗？** 不需要整段录音。只需一次 5–10 秒清晰录音克隆音色，之后都用文字生成；也可以直接用已保存的音色。

**Q：需要显卡或部署模型吗？** 不需要，生成在 Miragea 云端完成，本地只要 Python 3.9+。

**Q：支持哪些 AI Agent？** Codex、Claude Code、WorkBuddy、Cursor 等能运行 Python 脚本的 Agent 都可以。

**Q：字幕怎么对齐？** 每句起止时间来自实际生成的音频长度；需要更精细的时间轴，对成品再跑 `subtitles`。

**Q：能做多语种版本吗？** 可以，同一个克隆音色可以说 10 种语言，翻译稿件后设置 `language=` 即可。
