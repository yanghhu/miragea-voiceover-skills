---
name: youshengshu-ai-voiceover
description: "小说、故事、广播剧一键多角色朗读：旁白和每个角色分配不同音色，按段落停顿，输出整章配音WAV、带角色名的SRT字幕和时间轴，适合有声书、故事号、睡前故事、小说推文视频，支持声音克隆和10种语言。"
version: 1.0.0
display_name: "有声书配音｜小说多角色AI朗读·广播剧·字幕"
display_name_en: "Audiobook Multi-voice AI Narration"
description_zh: "小说、故事、广播剧一键多角色朗读：旁白和每个角色分配不同音色，按段落停顿，输出整章配音WAV、带角色名的SRT字幕和时间轴，适合有声书、故事号、睡前故事、小说推文视频，支持声音克隆和10种语言。"
description_en: "Multi-voice AI narration for novels, stories and audio dramas: narrator plus a voice per character, chapter WAV and speaker-labelled SRT subtitles. Voice cloning, 10 languages."
metadata:
  version: 1.0.0
  author: Miragea
  homepage: https://miragea.ai
  requires: Python 3.9+（仅标准库）, MIRAGEA_API_KEY
  keywords: [有声书配音, 小说朗读, 多角色配音, 广播剧, AI朗读, 小说推文, 故事配音]
---

# 有声书配音

有声书和小说推文视频的难点是角色多、篇幅长。旁白一个声音，每个角色一个声音，按章节一键生成整章音频和带角色名的字幕，适合有声书、故事号、睡前故事和小说推文视频。

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
python3 scripts/voiceover.py script examples/example.md -o out --preset youshengshu --dry-run   # 先离线试跑
python3 scripts/voiceover.py script 你的稿件.md -o out --preset youshengshu                     # 正式生成
```

## 你说什么 → 我做什么

| 用户说 | Agent 执行 |
|---|---|
| “把这一章做成有声书” | `script 第一章.md -o out --preset youshengshu` |
| “每个角色不同声音” | front matter 为每个角色指定音色 |
| “字幕里显示是谁在说话” | 预设已开启角色名；关闭去掉 `--preset` 改用默认参数 |
| “小说推文视频要竖屏字幕” | `--preset youshengshu --max-chars 14` |
| “整本书太长” | 按章节拆稿件，每章一份分别生成 |

## 有声书写稿要点

1. **只配对白给角色**，叙述交给旁白；`他说`、`她笑着问` 这类提示语留在旁白里。
2. **段落之间停顿** `[pause 0.8]`，章节开头停顿 1–2 秒。
3. **每章一份文件**：方便返工和分集发布。
4. **版权**：只朗读你有权使用的文字（原创、已授权或公版作品）。
5. `--preset youshengshu`：句间 0.5 秒、字幕每条 20 字、显示角色名。

## 示例稿件（examples/example.md）

```markdown
---
narrator: actor_id=NARRATOR_ID speed=0.95
xiaoyu: actor_id=GIRL_VOICE_ID
laozhang: actor_id=OLD_MAN_ID speed=0.9
---
# 第一章 夜里的灯（原创短篇示例）
[narrator] 小镇的灯塔，已经三十年没有亮过。
可那天夜里，小雨分明看见，塔顶闪了一下。
[xiaoyu]：张爷爷，灯塔里是不是有人？
[laozhang]：别瞎说。那座塔，早就没有门了。
[pause 0.8]
[narrator] 话音刚落，海面上又亮起了一道光。
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

**Q：有声书配音需要自己录音吗？** 不需要整段录音。只需一次 5–10 秒清晰录音克隆音色，之后都用文字生成；也可以直接用已保存的音色。

**Q：需要显卡或部署模型吗？** 不需要，生成在 Miragea 云端完成，本地只要 Python 3.9+。

**Q：支持哪些 AI Agent？** Codex、Claude Code、WorkBuddy、Cursor 等能运行 Python 脚本的 Agent 都可以。

**Q：字幕怎么对齐？** 每句起止时间来自实际生成的音频长度；需要更精细的时间轴，对成品再跑 `subtitles`。

**Q：能做多语种版本吗？** 可以，同一个克隆音色可以说 10 种语言，翻译稿件后设置 `language=` 即可。
