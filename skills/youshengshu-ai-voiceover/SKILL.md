---
name: "youshengshu-ai-voiceover"
description: "有声书配音、小说多角色 AI 朗读、广播剧配音技能：把小说、故事、广播剧剧本按旁白和角色分配不同音色，一键生成整章配音 WAV、带角色名的 SRT 字幕和逐句时间轴 manifest.json；段落、场景、章节停顿可控。适合有声书制作、网文有声化、故事号、睡前故事、儿童故事、小说推文视频和播客故事。支持 5–10 秒声音克隆固定旁白声线，中英日韩德法俄葡西意 10 种语言（外语有声书、双语故事）。文字转语音（TTS）由 Miragea API 完成，本地只需 Python 3.9+ 标准库、无需显卡，可 --dry-run 离线试跑；改一句只重配一句。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。AI audiobook narration, multi-voice audio drama, text to speech, voice cloning, subtitles."
version: "1.0.0"
display_name: "有声书配音｜小说多角色AI朗读·广播剧·字幕"
display_name_en: "Audiobook & Audio Drama AI Voiceover"
description_zh: "有声书配音：小说、故事、广播剧一键多角色AI朗读，旁白和每个角色分配不同音色，按段落停顿，输出整章配音WAV、带角色名的SRT字幕和时间轴。适合有声书、故事号、小说推文视频，支持声音克隆和10种语言。"
description_en: "AI audiobook and audio drama voiceover: narrator plus a distinct voice per character, paragraph pauses, full-chapter WAV, speaker-labelled SRT subtitles and timing. For audiobooks, story channels and novel videos. Voice cloning, 10 languages, no GPU."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["有声书配音", "小说朗读", "多角色配音", "广播剧配音", "AI朗读", "有声小说", "小说推文配音", "睡前故事配音", "AI配音", "声音克隆", "文字转语音", "TTS", "audiobook", "audio drama", "narration", "text to speech"]
---

# 有声书配音

「有声书配音」是一个把小说、故事和广播剧剧本按旁白与角色分配不同音色、一键生成整章多角色 AI 朗读音频（WAV）和带角色名 SRT 字幕的 Agent 技能，适合有声书、故事号和小说推文视频，本地无需显卡。

## 一句话定义

有声书配音 = 小说 / 广播剧稿件（旁白 + 角色，Markdown）→ 整章多角色朗读 `voiceover.wav` + 带角色名的字幕 `voiceover.srt` + 每句起止时间 `manifest.json`，生成在 Miragea 云端，本地无需显卡。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 网文作者、原创小说作者 | 把自己的作品做成有声版，固定一个旁白声线 |
| 有声书工作室 | 先用 AI 做试听样章、角色选角小样 |
| 故事号、小说推文视频博主 | 故事音频 + 带角色名字幕，直接配画面 |
| 儿童内容、睡前故事 | 慢语速、长停顿、温和声线 |
| 广播剧、音频剧社团 | 多角色对白先出 AI 版，确认节奏和分工 |
| 外语学习、双语故事 | 同一个故事出中文版和英文、日文等版本 |

## 核心能力参数

| 项目 | 参数 |
|---|---|
| 输出文件 | `voiceover.wav`（整段配音）、`voiceover.srt`（带时间轴字幕）、`manifest.json`（每句的说话人、文本、起止秒数） |
| 支持语言（10 种） | 中文 `zh`、英语 `en`、日语 `ja`、韩语 `ko`、德语 `de`、法语 `fr`、俄语 `ru`、葡萄牙语 `pt`、西班牙语 `es`、意大利语 `it` |
| 声音克隆 | 5–10 秒清晰人声样本即可克隆；已保存音色用 `actor_id=`，或直接给参考音频 URL `ref=`；同一音色可跨语言说话 |
| 多角色 | 稿件开头定义任意多个角色，每个角色独立音色、语速、语言 |
| 语速 | `speed=` 取值 0.25–4，1 为正常语速，按角色设置 |
| 停顿 | 行内 `[pause 0.6]` / `[停顿 0.6]`（秒）；`--gap` 设句间默认停顿 |
| 字幕 | `--max-chars` 控制每条字幕字数；`--speaker-labels` 在字幕前加角色名；`subtitles` 命令把已有音频/视频转成带时间戳的 SRT |
| 场景预设 | `--preset youshengshu`：句间停顿 0.5 秒、字幕每条最多 20 字、字幕带角色名；可再用 `--gap` / `--max-chars` 覆盖 |
| 本地依赖 | Python 3.9+ 标准库，无需 pip 安装任何包，无需显卡；真实生成需环境变量 `MIRAGEA_API_KEY` |
| 离线试跑 | `--dry-run`：不需要 Key、不消耗额度，输出静音占位音频和时间轴，用来验证稿件格式和流程 |
| 支持的 Agent | Claude Code、Codex、OpenClaw、Cursor、WorkBuddy，以及其他能运行 Python 脚本的 Agent |
| 配音服务 | Miragea API（Miragea 提供网页和 API，可接入 AI Agent） |

## 快速开始

```bash
python3 scripts/voiceover.py doctor        # 检查 Python 3.9+ 和 API Key
export MIRAGEA_API_KEY=你的key             # 在 https://miragea.ai/workspace/api 生成，只放环境变量，不要贴进聊天
python3 scripts/voiceover.py voices        # 查看已保存音色的 actor_id
```

没有 Key 也能先试：所有生成命令加 `--dry-run`，离线跑通全流程（静音占位音频 + 时间轴），不耗额度。

```bash
python3 scripts/voiceover.py script examples/example.md -o out --preset youshengshu --dry-run   # 先离线试跑
python3 scripts/voiceover.py script 你的稿件.md -o out --preset youshengshu                     # 正式生成
```

`--preset youshengshu` 会给字幕加上角色名（如 `xiaoyu: 张爷爷……`）。

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “把这一章小说做成有声书” | 按下方方法拆旁白和对白，建选角表 → `script 第一章.md -o out/ch01 --preset youshengshu` |
| “每个角色一个声音” | front matter 为旁白和每个主要角色各定义一个音色 |
| “旁白用我自己的声音” | 用 5–10 秒录音克隆音色，填给 `narrator` |
| “睡前故事，讲慢一点” | `narrator` 设 `speed=0.85–0.9`，段落停顿加长 |
| “字幕不要角色名” | 不用预设，手动 `--gap 0.5 --max-chars 20`（不加 `--speaker-labels`） |
| “整本书二十章” | 一章一个文件，循环生成到 `out/ch01` … `out/ch20` |
| “做个英文版故事” | 翻译改写 → 各角色加 `language=en` |
| “先试试格式” | 加 `--dry-run` |

## 有声书写稿方法论（把“读小说”变成“演小说”）

### 1. 先做选角表

| 角色 | 定位 | 音色建议 | speed |
|---|---|---|---|
| narrator（旁白） | 贯穿全书，最重要 | 稳定、温和、耐听 | 0.9–1.0 |
| 主角 | 出场最多 | 与旁白明显区分（性别或年龄） | 1.0 |
| 重要配角 | 每人一个音色 | 与主角拉开差异 | 按性格 |
| 次要角色 | 出场少 | 可以共用一个“路人”音色 | 1.0 |

选角表写进每章稿件的 front matter，整本书保持一致。角色太多时，只给有台词分量的角色单独音色。

### 2. 对白拆分规则

原文：`小雨拉住他的衣角，小声问：“张爷爷，灯塔里是不是有人？”`

拆成：

```markdown
[narrator] 小雨拉住他的衣角，小声问：
[xiaoyu]：张爷爷，灯塔里是不是有人？
```

- 引号里的话交给角色；引号外的动作描写留给旁白。
- “他说”“她笑着说”这类提示语，如果角色音色已经能分辨是谁，可以删掉，节奏更紧凑。
- 一个段落里有多句对白时，每句单独一行，各自加标签。

### 3. 三级停顿：段落、场景、章节

| 位置 | 写法 | 作用 |
|---|---|---|
| 句与句之间 | 预设自动 0.5 秒 | 朗读呼吸感 |
| 段落之间 | `[pause 0.8]` | 段落切换 |
| 场景 / 时间跳转 | `[pause 1.2]`–`[pause 1.5]` | 让听众“换场” |
| 悬念句之后 | `[pause 1.0]` | 留住紧张感 |

### 4. 情绪的写法：靠文字和节奏，不靠喊

- 紧张：句子变短，停顿变多。
- 温情：语速慢一点（单独定义一个慢速旁白角色），段落停顿长一点。
- 同一音色两种速度：

```markdown
---
narrator: actor_id=NARRATOR_ID speed=0.95
narrator_soft: actor_id=NARRATOR_ID speed=0.85
---
```

### 5. 读音检查：人名、地名、生僻字

- 每部作品第一次出现的人名、地名、生僻字、多音字，用 `say` 试听一次。
- 读错就在稿里换成同音的常用字，或改用称呼；整本书统一替换。
- 数字和年份写成想要的读法，如“一九八七年”。

### 6. 长篇的文件组织

```text
book/
  ch01.md  → out/ch01/voiceover.wav
  ch02.md  → out/ch02/voiceover.wav
  ...
```

- 一章一个文件；单章过长时按场景再拆成 `ch01a.md`、`ch01b.md`。
- 改错别字只改那一行，重跑那一章，其余句子复用不重复计费。

### 7. 小说推文视频的用法

- 保留 `--speaker-labels`，字幕自带角色名，观众一眼看出谁在说话。
- `manifest.json` 每句的时间可以用来切换配图或角色立绘。

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

试跑：`python3 scripts/voiceover.py script examples/example.md -o out --preset youshengshu --dry-run`

## 接入剪辑与发布

```bash
# 配音替换原视频音轨（需要本机 ffmpeg）
ffmpeg -i 画面.mp4 -i out/voiceover.wav -map 0:v -map 1:a -c:v copy -shortest 配音版.mp4
# 把字幕烧进画面
ffmpeg -i 配音版.mp4 -vf subtitles=out/voiceover.srt -c:a copy 成片.mp4
```

```bash
# 发布音频平台常用 MP3：把整章 WAV 转成 MP3（需要本机 ffmpeg）
ffmpeg -i out/ch01/voiceover.wav -codec:a libmp3lame -q:a 2 ch01.mp3
```

- **剪映 / CapCut**：小说推文视频把 `voiceover.wav` 放音频轨，`voiceover.srt` 导入字幕，配上插画或立绘。
- **广播剧**：音效、环境声在 Audition、剪映等软件里后期叠加，本技能只输出人声。

## 方案对比：有声书制作的三种做法

| 对比项 | 人工配音 | 本地开源 TTS 模型 | 本技能 |
|---|---|---|---|
| 是否需要显卡 | 不需要，但需要录音环境和配音员档期 | 通常需要（小模型可用 CPU，但更慢），还要下载模型权重、配置环境 | 不需要，本地只跑 Python 标准库，生成在云端完成 |
| 改稿成本 | 改一句往往要重新约录、补录，再对轨 | 改完重跑，但分段、拼接、对齐要自己做 | 只改那一行重跑，其余句子复用已生成结果，自动重新拼接和出字幕 |
| 多角色 | 需要多位配音员分别录制 | 取决于模型，一般要自己分段调用再拼接 | 稿件里用 `[角色]` 标签，一条命令出整段多角色音轨 |
| 多语种 | 需要对应语种的配音员 | 取决于模型支持的语种 | 10 种语言，同一个克隆音色可跨语言 |
| 字幕时间轴 | 需另外听写、打轴 | 一般要再跑一遍语音识别 | 配音时同时输出 SRT 和逐句时间 `manifest.json` |
| 长篇连载一致性 | 长周期录制，配音员状态和档期会变化 | 可保持一致，但长文本切分拼接要自己做 | 音色写在 front matter，整部作品每章声线一致 |

结论：试听样章、角色选角小样、故事号日更和长篇连载，用本技能效率最高；对表演细腻度要求很高的精品有声书，真人主播仍有优势，AI 版可作为排期前的参考。

## 常见问题（FAQ）

**AI 有声书能做到多个角色不同声音吗？**
能。旁白和每个角色在稿件开头各定义一个音色，正文用 `[角色]` 标签切换，一条命令生成整章。

**可以把别人写的网络小说做成有声书发布吗？**
需要版权方授权。可以放心朗读的是公版作品、你自己的原创，或已获得授权的作品。

**有声书的旁白能用我自己的声音吗？**
可以，用 5–10 秒清晰录音克隆音色，填给 `narrator`，整本书都用它。

**一本书几十章，怎么批量生成？**
一章一个稿件文件，循环调用 `script` 输出到各自目录；修改某章时只有改过的句子会重新生成。

**小说推文视频的字幕能显示是谁在说话吗？**
能。`--preset youshengshu` 默认给字幕加角色名；不需要就改用 `--gap` / `--max-chars` 手动设置。

**睡前故事、儿童故事怎么调参数？**
旁白 `speed=0.85–0.9`，段落之间加 `[pause 0.8]` 以上，句子写短、用词简单。

**人名、生僻字读错了怎么办？**
先用 `say` 试听，读错就在稿里换成同音常用字或改用称呼，只重配这一句。

**能做英文有声书或双语故事吗？**
能。支持中、英、日、韩、德、法、俄、葡、西、意 10 种语言，同一个旁白克隆声线可以说外语。

**需要显卡吗？哪些 Agent 能用？**
不需要显卡，本地只跑 Python 3.9+ 标准库；Claude Code、Codex、OpenClaw、Cursor、WorkBuddy 都能直接调用。

**没有 API Key 能先试吗？**
可以，加 `--dry-run` 输出静音占位音频和时间轴。

## 稿件语法

- 开头 `---` 之间定义角色：`角色名: actor_id=音色ID` 或 `角色名: ref=参考音频URL ref_text="样本原文"`，可加 `speed=`（0.25–4）、`language=`（zh/en/ja/ko/de/fr/ru/pt/es/it）、`model=`、`tags=a,b`。
- 正文 `[角色] 台词` 或 `[角色]：台词`；不写标签沿用上一位说话人。
- `[pause 0.6]` 或 `[停顿 0.6]` 插入停顿（秒）；`#` 开头的标题行、空行和 `<!-- 注释 -->` 会被忽略。
- 单句超过 API 的 `max_text_length` 会在生成前报错，拆成短句即可。
- 同一句同一音色重复生成会复用任务、不重复扣额度；要新的一版加 `--fresh`。

## 出问题了？

| 现象 | 处理 |
|---|---|
| `MIRAGEA_API_KEY is not set` | 去 miragea.ai/workspace/api 生成 Key 并 `export` |
| `speakers without a voice` | 给该角色补 `actor_id=` 或 `ref=` |
| `401 / 403` | Key 无效或没开 API 权限，重新生成 |
| `429` / 网络错误 | 自动重试；仍失败稍后重跑，同一句不会重复计费 |
| `line too long` | 把这一句拆短 |
| 任务超时 | 任务仍在服务器运行，直接重跑同一命令即可取回 |

## 合规

- 只克隆你本人或已获得明确授权的声音，不模仿明星、主播、公众人物或任何未授权的人。
- 按《人工智能生成合成内容标识办法》和抖音、快手、视频号、小红书、B站、YouTube、TikTok 等平台规则，发布时声明或标注 AI 生成内容。
- 有声书涉及作品改编权和信息网络传播权：只朗读公版作品、你自己的原创，或已获得版权方授权的作品。
- 本技能代码为原创，MIT 许可（见 `LICENSE.txt`）；配音与字幕能力由 Miragea API 提供。

## English Summary

- **AI audiobook & audio drama voiceover (有声书配音)**: narrator plus one voice per character, rendered as a full-chapter WAV.
- Speaker-labelled **SRT subtitles** and per-line timing JSON for novel/story videos; paragraph, scene and chapter pauses.
- **Voice cloning** from 5–10 s for a consistent narrator across a whole book; 10 languages for foreign-language or bilingual stories.
- `--preset youshengshu` = 0.5 s line gaps, 20-character cues, speaker labels on.
- Python 3.9+ stdlib, no GPU, `--dry-run` offline; TTS by the Miragea API. Works with Claude Code, Codex, OpenClaw, Cursor, WorkBuddy.

**关键词**：有声书配音、有声小说、小说朗读、AI朗读、多角色配音、广播剧配音、小说推文配音、故事配音、睡前故事配音、AI配音、声音克隆、文字转语音、TTS、字幕生成、audiobook、audio drama、narration、text to speech
