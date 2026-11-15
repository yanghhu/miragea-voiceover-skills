# 电影解说配音

「电影解说配音」是一个给电影、电视剧、短剧和动漫解说号做配音的 Agent 技能：解说稿、分镜表或 SRT 字幕进，解说旁白和角色台词各用你克隆的音色逐句配音，按画面时长对轨并提示超时句，输出整段配音、旁白 / 台词分轨、SRT 字幕和逐句计划表，本地无需显卡。

- 解说稿（可带时间码）/ 分镜表 CSV / SRT 字幕三种输入；不写角色的行就是解说旁白
- 旁白和角色台词各用自己克隆的音色，（语气）逐句转成语气标签；有时间码就按画面对轨，超时句给出建议语速和要删的字数，`--fit` 自动重配
- 输出 voiceover.wav + stems/narration.wav + stems/dialogue.wav + voiceover.srt + cues.csv + report.md；改一句只重配一句；`selftest` 离线自检

## 安装

把本文件夹 `movie-recap-ai-voiceover/` 复制到 Agent 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`），或在技能市场一键安装。完整用法、稿件格式、对轨和 FAQ 见 [SKILL.md](./SKILL.md)。

```bash
python3 scripts/recap_dub.py selftest                                      # 离线自检，无需 Key、不联网
python3 scripts/recap_dub.py build examples/example.md -o out --dry-run    # 离线试跑示例
```

正式配音需要 Python 3.9+、环境变量 `MIRAGEA_API_KEY` 和账号里克隆好的音色（Miragea：https://miragea.ai）。
