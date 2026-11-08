---
name: movie-recap-ai-voiceover
description: "电影解说、影视剧解说、短剧解说一键配音：解说旁白加多个角色台词，各用不同音色，自动停顿、生成整段配音WAV和SRT字幕，方便剪映对轨。支持声音克隆和中英日韩等10种语言，适合影视解说号批量更新。"
version: 1.0.0
display_name: "电影解说配音｜影视解说AI配音·多角色·字幕"
display_name_en: "Movie Recap AI Voiceover"
description_zh: "电影解说、影视剧解说、短剧解说一键配音：解说旁白加多个角色台词，各用不同音色，自动停顿、生成整段配音WAV和SRT字幕，方便剪映对轨。支持声音克隆和中英日韩等10种语言，适合影视解说号批量更新。"
description_en: "AI voiceover for movie and drama recap scripts: narrator plus character lines in different voices, auto pauses, full WAV and SRT subtitles ready for CapCut. Voice cloning, 10 languages."
metadata:
  version: 1.0.0
  author: Miragea
  homepage: https://miragea.ai
  requires: Python 3.9+（仅标准库）, MIRAGEA_API_KEY
  keywords: [电影解说配音, 影视解说, 短剧解说, AI解说配音, 多角色配音, 解说文案, 声音克隆]
---

# 电影解说配音

解说号最费时间的是配音：旁白一遍遍录，角色台词还要换声音。写好解说稿，旁白和每个角色各配一个音色，一条命令出整段配音和字幕，直接拖进剪映对画面。

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
python3 scripts/voiceover.py script examples/example.md -o out --preset jieshuo --dry-run   # 先离线试跑
python3 scripts/voiceover.py script 你的稿件.md -o out --preset jieshuo                     # 正式生成
```

## 你说什么 → 我做什么

| 用户说 | Agent 执行 |
|---|---|
| “这篇电影解说稿配音” | `script 解说稿.md -o out --preset jieshuo` |
| “男主女主台词用不同声音” | front matter 里给每个角色单独 `actor_id=` |
| “旁白要低沉有悬念感” | 选低沉音色，`speed=0.95`，悬念句前加 `[pause 0.5]` |
| “做一版英文解说发 YouTube” | 让 Agent 翻译稿件，角色加 `language=en`，同一克隆音色 |
| “给成片配字幕” | `subtitles 成片.mp4 -o 成片.srt` |

## 解说写稿要点

1. **开头钩子**：用一句反差或悬念开场（“他捡到的不是手机，是自己的死亡预告”）。
2. **旁白讲剧情，角色只留金句**：角色台词控制在全片 20% 以内，节奏更紧。
3. **场景切换停顿**：换场景加 `[pause 0.4]`，方便剪辑卡点。
4. **规避原片台词照搬**：用自己的话复述剧情，降低版权风险。
5. **时间轴对画面**：`manifest.json` 里每句起止时间可直接用来对剪映时间线。

预设 `--preset jieshuo`：句间 0.3 秒、字幕每条 16 字。

## 示例稿件（examples/example.md）

```markdown
---
narrator: actor_id=NARRATOR_ID speed=0.98
hero: actor_id=HERO_ID
---
# 电影解说示例（原创剧情）
[narrator] 一个普通的快递员，捡到了一部能看见未来的手机。
[pause 0.5]
屏幕上只有一条新闻：明天下午三点，他会死在这条街上。
[hero]：如果明天的新闻里有我，那今天我该做什么？
[narrator] 他不知道的是，每看一次未来，现实就会悄悄改变一点。
[pause 0.4]
而这一次，改变的是他最信任的人。
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

**Q：电影解说配音需要自己录音吗？** 不需要整段录音。只需一次 5–10 秒清晰录音克隆音色，之后都用文字生成；也可以直接用已保存的音色。

**Q：需要显卡或部署模型吗？** 不需要，生成在 Miragea 云端完成，本地只要 Python 3.9+。

**Q：支持哪些 AI Agent？** Codex、Claude Code、WorkBuddy、Cursor 等能运行 Python 脚本的 Agent 都可以。

**Q：字幕怎么对齐？** 每句起止时间来自实际生成的音频长度；需要更精细的时间轴，对成品再跑 `subtitles`。

**Q：能做多语种版本吗？** 可以，同一个克隆音色可以说 10 种语言，翻译稿件后设置 `language=` 即可。
