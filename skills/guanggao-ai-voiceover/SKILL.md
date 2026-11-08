---
name: guanggao-ai-voiceover
description: "品牌广告片、企业宣传片、产品介绍视频、App演示视频一键配音：旁白与对白多角色生成，停顿和语速精细控制，输出配音WAV和SRT字幕，支持中英日韩德法等10种语言，一份脚本快速出多语种版本。"
version: 1.0.0
display_name: "广告片配音｜宣传片产品视频AI配音·旁白·字幕"
display_name_en: "Ad & Promo Video AI Voiceover"
description_zh: "品牌广告片、企业宣传片、产品介绍视频、App演示视频一键配音：旁白与对白多角色生成，停顿和语速精细控制，输出配音WAV和SRT字幕，支持中英日韩德法等10种语言，一份脚本快速出多语种版本。"
description_en: "AI voiceover for brand ads, promo films and product demo videos: narrator and dialogue voices, fine pause and speed control, WAV plus SRT, one script to 10 language versions."
metadata:
  version: 1.0.0
  author: Miragea
  homepage: https://miragea.ai
  requires: Python 3.9+（仅标准库）, MIRAGEA_API_KEY
  keywords: [广告片配音, 宣传片配音, 产品视频配音, 企业宣传片, 旁白配音, 多语种配音, AI配音]
---

# 广告片配音

广告片和宣传片改稿最频繁，每改一次就得重新约配音。用 AI 配音先出可用版本：旁白、对白、停顿都能精细调，客户改一个字只重新生成那一句；同一脚本还能一键出英文、日文等海外版本。

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
python3 scripts/voiceover.py script examples/example.md -o out --preset guanggao --dry-run   # 先离线试跑
python3 scripts/voiceover.py script 你的稿件.md -o out --preset guanggao                     # 正式生成
```

## 你说什么 → 我做什么

| 用户说 | Agent 执行 |
|---|---|
| “给这个宣传片脚本配旁白” | `script 脚本.md -o out --preset guanggao` |
| “客户改了第二句” | 只改那一行重跑，其余句子不重复生成 |
| “出英文和日文版” | 翻译脚本，分别 `language=en` / `language=ja` |
| “男女对白广告” | front matter 定义两个角色各自音色 |
| “要更有呼吸感” | 关键句前后加 `[pause 0.6]`，`speed=0.95` |

## 广告脚本要点

1. **一句一个画面**：脚本按镜头分行，方便对画面。
2. **留白**：广告靠停顿出质感，`--preset guanggao` 句间 0.4 秒。
3. **品牌名单独成句**：读得更清楚，也方便后期加 Logo。
4. **合规用词**：避免“最”“第一”“国家级”等极限词。
5. **多语种版本**：同一音色跨语言，品牌声音统一。

## 示例稿件（examples/example.md）

```markdown
---
voice: actor_id=BRAND_VOICE_ID speed=0.95
---
# 产品宣传片示例（品牌名为虚构）
[voice] 每一个清晨，都值得被认真对待。
[pause 0.6]
从一杯咖啡开始，
到一天的第一个灵感。
[pause 0.4]
晨屿咖啡机。
让好状态，准时出现。
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

**Q：广告片配音需要自己录音吗？** 不需要整段录音。只需一次 5–10 秒清晰录音克隆音色，之后都用文字生成；也可以直接用已保存的音色。

**Q：需要显卡或部署模型吗？** 不需要，生成在 Miragea 云端完成，本地只要 Python 3.9+。

**Q：支持哪些 AI Agent？** Codex、Claude Code、WorkBuddy、Cursor 等能运行 Python 脚本的 Agent 都可以。

**Q：字幕怎么对齐？** 每句起止时间来自实际生成的音频长度；需要更精细的时间轴，对成品再跑 `subtitles`。

**Q：能做多语种版本吗？** 可以，同一个克隆音色可以说 10 种语言，翻译稿件后设置 `language=` 即可。
