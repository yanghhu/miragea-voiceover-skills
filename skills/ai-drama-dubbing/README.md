# 漫剧配音

「漫剧配音」是一个给 AI 漫剧、竖屏短剧和动画短片做多角色对白配音的 Agent 技能：按剧本、分镜表或 SRT 识别角色，每个角色用你克隆的音色、逐句按情绪配音，可按时间码对轨，输出整段配音、角色分轨和 SRT 字幕，本地无需显卡。

- 剧本 / 分镜表 CSV / SRT 三种输入，自动识别角色、生成选角表（cast.md）
- 每个角色用自己克隆的音色，台词里的（情绪）逐句转成语气标签；有时间码就按画面对轨，超时台词给出建议语速，`--fit` 可自动重配
- 输出 dub.wav + 每个角色等长分轨 stems/ + dub.srt / dub_roles.srt + cues.csv + report.md；改一句只重配一句

## 安装

把本文件夹 `ai-drama-dubbing/` 复制到 Agent 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`），或在技能市场一键安装。完整用法、选角与情绪写法、对轨和 FAQ 见 [SKILL.md](./SKILL.md)。

```bash
python3 scripts/drama_dub.py build examples/example.md -o out --dry-run   # 无需 Key，离线试跑
```

正式配音需要 Python 3.9+、环境变量 `MIRAGEA_API_KEY` 和账号里克隆好的音色（Miragea：https://miragea.ai）。
