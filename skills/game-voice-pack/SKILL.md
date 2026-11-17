---
name: "game-voice-pack"
description: "游戏配音、批量配音、NPC台词语音包、游戏语音技能：把台词写成 CSV（id、角色、台词、语气标签、语速、备注），用 Miragea 账号里你自己的克隆音色按角色逐句生成，输出按 id 命名的 WAV（按角色分文件夹或平铺）、manifest.csv / manifest.json 清单和时长报告，方便导入 Unity、Godot、Unreal 或游戏策划表；`--map 村长=老者` 把剧中角色映射到账号角色，`--only` 只重配指定 id，改一行只重生成一行，断网续跑。适用于独立游戏、手游 NPC 对白、教学关卡旁白、UI 提示语音、视觉小说。需要 API Key；本地只用 Python 3.9+ 标准库，无需显卡，可 --dry-run 离线试跑。适用于 Claude Code、Codex、OpenClaw、Cursor、WorkBuddy。Game voiceover, batch TTS, NPC dialogue, voice pack."
version: "1.0.0"
display_name: "游戏配音｜批量配音·NPC台词语音包·游戏语音"
display_name_en: "Game Voice Pack · Batch Voiceover · NPC Lines"
description_zh: "游戏配音批量生成：把NPC台词写成CSV表格，每行一个编号和角色，按角色套用你的克隆音色，自动输出按编号命名的、分角色文件夹的语音文件和清单，改一行只重配一行，也可离线试跑。"
description_en: "Batch game voiceover: a CSV of lines (id, role, text, tag) becomes one audio file per line, named by id and grouped by role, with a manifest for your game engine. Map each character to one of your cloned voices; edit one row and regenerate only that row."
metadata:
  version: "1.0.0"
  author: "Miragea"
  homepage: "https://miragea.ai"
  requires: "Python 3.9+（仅标准库，无需显卡）, MIRAGEA_API_KEY"
  keywords: ["游戏配音", "批量配音", "NPC配音", "台词语音包", "游戏语音", "游戏台词", "批量文字转语音", "自动批量配音", "视觉小说配音", "独立游戏", "Unity", "Godot", "声音克隆", "AI配音", "game voiceover", "batch voiceover", "NPC dialogue", "voice pack", "voice cloning"]
---

# 游戏配音

「游戏配音」是一个把台词表批量变成语音包的 Agent 技能：CSV 每行一个编号、角色和台词，按角色用你自己的克隆音色生成，输出按编号命名的音频文件和清单，改一行只重配一行，本地无需显卡。

## 一句话定义

游戏配音 = 台词 CSV（id, role, text…）→ `game_voice.py build --map 角色=账号角色` → `角色/id.wav` 语音文件 + `manifest.csv`（id、文件、时长、台词）+ `report.txt`。

## 适用人群与场景

| 谁在用 | 典型场景 |
|---|---|
| 独立游戏开发者 | NPC 对白、任务提示，台词改动频繁，需要只重配改过的行 |
| 游戏策划 | 从策划表导出 CSV，按 id 对应到引擎里的台词键 |
| 视觉小说 / 互动叙事作者 | 多角色对白，每个角色一个音色 |
| 教学关卡 / 应用 | 新手引导旁白、界面提示语音 |

## 能力一览

| 项目 | 说明 |
|---|---|
| 输入 | UTF-8 CSV，表头至少 `id,role,text`；可选 `tag`（`capabilities` 允许的语气标签）、`speed`（0.25–4）、`lang`（语言提示）、`note`（备注，不朗读） |
| 角色映射 | `--map 村长=老者` 把剧中角色映射到账号里的角色名（可重复）；未映射的角色用 `--voice` |
| 输出 | `OUT/角色名/id.wav`（`--layout flat` 时 `OUT/id.wav`）、`manifest.csv`、`manifest.json`、`report.txt` |
| 增量 | 每句按内容缓存在 `cache/`；改一行重跑只重配这一行；`--only id1,id2` 指定重配 |
| 校验 | `check` 离线统计角色、句数、粗估时长；id 只允许字母数字下划线横线点，重复 id 报错 |
| 长句 | 超过 120 字自动在标点处切开再拼回 |
| 本地依赖 | Python 3.9+ 标准库，无需显卡 |

## 快速开始

先离线试跑（不需要 Key、不联网）：

```bash
python3 scripts/game_voice.py selftest
python3 scripts/game_voice.py check examples/lines.csv --map 村长=老者
python3 scripts/game_voice.py build examples/lines.csv -o pack --map 村长=老者 --voice 默认 --dry-run
python3 scripts/game_voice.py build examples/lines.csv -o pack_flat --layout flat --only npc_001,ui_ok --voice 默认 --dry-run
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
python3 scripts/game_voice.py build 台词.csv -o voicepack --map 村长=老者 --map 少女=少女角色 --voice 旁白角色
python3 scripts/game_voice.py build 台词.csv -o voicepack --only npc_002          # 只重配改过的一行
```

## 你说什么 → Agent 执行

| 你说 | Agent 执行 |
|---|---|
| “把这张台词表配成语音包” | 检查 CSV → `build --map ...` |
| “村长用老者的声音，少女用另一个” | 对每个角色加 `--map` |
| “第 12 句改了，重配一下” | 改 CSV 后 `--only 该 id` |
| “所有文件放一个文件夹” | `--layout flat` |
| “先看看多长” | `check`，离线粗估时长 |

## 使用建议

1. id 直接用游戏里的台词键（如 `npc_001`），文件名就是 id，导入引擎无需改名。
2. 语气标签只能用 `capabilities` 返回的标签；不确定就留空。
3. 先挑几句试听再批量跑。
4. 导入引擎前需要 OGG/MP3 时用 ffmpeg 转：`ffmpeg -i npc_001.wav npc_001.ogg`。

## dry-run 实际输出

```text
$ python3 scripts/game_voice.py check examples/lines.csv --map 村长=老者
村长 → 账号角色：老者｜2 句｜约 5 秒
少女 → 账号角色：（未指定）｜1 句｜约 2 秒
系统 → 账号角色：（未指定）｜1 句｜约 1 秒
共 4 句、3 个角色，粗估总时长 0.1 分钟

$ python3 scripts/game_voice.py build examples/lines.csv -o pack --map 村长=老者 --voice 默认 --dry-run
4 条 → pack/（manifest.csv / manifest.json / report.txt）  [dry-run：占位提示音，未调用接口]

$ python3 scripts/game_voice.py build examples/lines.csv -o pack_flat --layout flat --only npc_001,ui_ok --voice 默认 --dry-run
2 条 → pack_flat/（manifest.csv / manifest.json / report.txt）  [dry-run：占位提示音，未调用接口]
```

## 示例台词表（examples/lines.csv，原创）

```text
id,role,text,tag,speed,lang,note
npc_001,村长,欢迎来到青石村，旅人。,,,,开场白
npc_002,村长,山里最近不太平，出门要小心。,,0.95,,
npc_010,少女,你看见我的小猫了吗？,,1.05,,支线任务
ui_ok,系统,任务完成！,,,,UI 提示
```

## 和常见做法的区别

| 对比项 | 逐条网页配音 | 找配音演员 | 本技能 |
|---|---|---|---|
| 批量 | 一条条点 | 排期录制 | 一张表一条命令 |
| 文件命名 | 手动改名 | 手动整理 | 按 id 自动命名、按角色分目录 |
| 改词 | 重做 | 补录 | 只重配改过的行 |
| 清单 | 无 | 手工表格 | `manifest` 自动生成 |

## 常见问题（FAQ）

**游戏配音怎么批量做？**
写好 CSV，运行 `build`，每行得到一个以 id 命名的 WAV。

**多个角色怎么配不同声音？**
每个剧中角色用 `--map 剧中角色=账号角色名` 指到你账号里不同的角色。

**改了几句怎么办？**
改 CSV 重跑，未改动的行从缓存复用；也可以 `--only` 指定 id。

**能输出 OGG 吗？**
本技能输出 WAV，需要 OGG/MP3 请用 ffmpeg 转换。

**需要显卡吗？**
不需要。

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

- 只输出 WAV；不做口型驱动、变声或音效。
- 语气标签、语言提示是否生效以接口和所选角色为准；可用项以 `capabilities` 为准。
- `--dry-run` 输出的是占位提示音，只用于检查流程和命名。

## 合规与 AI 生成内容标识

- 只用你本人或已获书面授权的声音创建角色和配音，不模仿他人声音；不得用于冒充、诈骗或误导。
- 按《人工智能生成合成内容标识办法》和各平台规则，在需要的场合标注 AI 生成内容。
- `scripts/miragea_audio.py` is the official client 1.3.0, shipped unchanged；`scripts/audio_kit.py` 和本技能主脚本为原创，MIT 许可（见 `LICENSE.txt`）。

## English Summary

- **Game voice pack**: CSV (`id, role, text, tag`) → `game_voice.py build --map ROLE=ACCOUNT_ROLE` → `ROLE/id.wav` plus `manifest.csv` / `manifest.json`.
- `--only id1,id2` regenerates edited rows; finished rows are cached.
- Local requirements: Python 3.9+ standard library only, no GPU, no pip install. Every command has an offline `--dry-run` (no key, no network).

**关键词**：游戏配音、批量配音、NPC配音、台词语音包、游戏语音、批量文字转语音、视觉小说配音、声音克隆、AI配音、game voiceover、batch voiceover、NPC dialogue
