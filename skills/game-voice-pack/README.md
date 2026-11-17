# 游戏配音

「游戏配音」是一个把台词表批量变成语音包的 Agent 技能：CSV 每行一个编号、角色和台词，按角色用你自己的克隆音色生成，输出按编号命名的音频文件和清单，改一行只重配一行，本地无需显卡。

- CSV（id, role, text, tag, speed, lang, note）→ `OUT/角色/id.wav` + `manifest.csv` / `manifest.json` + `report.txt`
- `--map 剧中角色=账号角色名`：多个角色各用各的克隆音色；`--layout flat` 平铺到一个目录
- `--only id1,id2` 只重配改过的行；已生成的行缓存复用，断网续跑

## 安装

把本文件夹 `game-voice-pack/` 复制到 Agent 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`），或在技能市场一键安装。完整用法、工作流和 FAQ 见 [SKILL.md](./SKILL.md)。

```bash
python3 scripts/game_voice.py selftest     # 离线自检，不需要 Key
python3 scripts/game_voice.py build examples/lines.csv -o pack_flat --layout flat --only npc_001,ui_ok --voice 默认 --dry-run
```

正式生成需要 Python 3.9+、环境变量 `MIRAGEA_API_KEY` 和账号里你自己的角色（Miragea：https://miragea.ai）。
