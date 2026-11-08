---
name: daihuo-ai-voiceover
description: "抖音、快手、视频号、TikTok带货短视频一键配音：卖点文案逐行生成快节奏配音和大字竖屏字幕，同一款商品可批量出多个版本测试，支持声音克隆和多语种出海带货（英语、西语、葡语等10种语言）。"
version: 1.0.0
display_name: "带货视频配音｜短视频带货AI配音·卖点文案·字幕"
display_name_en: "E-commerce Video AI Voiceover"
description_zh: "抖音、快手、视频号、TikTok带货短视频一键配音：卖点文案逐行生成快节奏配音和大字竖屏字幕，同一款商品可批量出多个版本测试，支持声音克隆和多语种出海带货（英语、西语、葡语等10种语言）。"
description_en: "Fast-paced AI voiceover for product and e-commerce short videos (Douyin, TikTok Shop): selling-point scripts to WAV plus big-caption SRT, quick A/B versions, voice cloning, 10 languages."
metadata:
  version: 1.0.0
  author: Miragea
  homepage: https://miragea.ai
  requires: Python 3.9+（仅标准库）, MIRAGEA_API_KEY
  keywords: [带货视频配音, 带货配音, 短视频带货, 电商配音, 卖点文案, TikTok带货, AI配音]
---

# 带货视频配音

带货视频要的是快：一个商品要测好几版文案。卖点一行一句写下来，一条命令出快节奏配音和大字字幕；换文案只改字不重录，还能一键出英语、西语版做 TikTok 出海。

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
python3 scripts/voiceover.py script examples/example.md -o out --preset daihuo --dry-run   # 先离线试跑
python3 scripts/voiceover.py script 你的稿件.md -o out --preset daihuo                     # 正式生成
```

## 你说什么 → 我做什么

| 用户说 | Agent 执行 |
|---|---|
| “给这个商品文案配音” | `script 文案.md -o out --preset daihuo` |
| “出三个版本测试” | 写三份文案分别生成，输出到 out1/out2/out3 |
| “节奏再快一点” | 角色 `speed=1.15`，删掉形容词，一行一个卖点 |
| “做 TikTok 美国站英文版” | 翻译文案，`language=en`；西语站 `language=es` |
| “视频已剪好，只要字幕” | `subtitles 成片.mp4 -o 成片.srt` |

## 带货文案要点

1. **第 1 句说痛点**：“夏天出门两小时，妆就花了？”
2. **一行一个卖点**：用数字和场景，不堆形容词。
3. **给证据**：材质、测试、使用前后对比，避免“最”“第一”等极限词（广告法）。
4. **价格和优惠写在画面**，口播只说“看下方”，方便同一配音复用多次活动。
5. **结尾一个指令**：只说一个动作。

预设 `--preset daihuo`：句间 0.1 秒、字幕每条 12 字，适合大字竖屏。

## 示例稿件（examples/example.md）

```markdown
---
host: actor_id=YOUR_ACTOR_ID speed=1.12
---
# 带货示例：防晒喷雾（文案为示例，请按真实商品改写）
[host] 夏天出门两小时，妆就花了？
问题可能出在防晒上。
这瓶喷雾，隔着妆也能补，
三秒喷完，不搓泥、不发白。
出差、通勤、户外都能放包里。
[pause 0.2]
想要的话，看下方链接。
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

**Q：带货视频配音需要自己录音吗？** 不需要整段录音。只需一次 5–10 秒清晰录音克隆音色，之后都用文字生成；也可以直接用已保存的音色。

**Q：需要显卡或部署模型吗？** 不需要，生成在 Miragea 云端完成，本地只要 Python 3.9+。

**Q：支持哪些 AI Agent？** Codex、Claude Code、WorkBuddy、Cursor 等能运行 Python 脚本的 Agent 都可以。

**Q：字幕怎么对齐？** 每句起止时间来自实际生成的音频长度；需要更精细的时间轴，对成品再跑 `subtitles`。

**Q：能做多语种版本吗？** 可以，同一个克隆音色可以说 10 种语言，翻译稿件后设置 `language=` 即可。
