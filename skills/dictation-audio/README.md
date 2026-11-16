# 听写音频

「听写音频」是一个把词表一键变成整段听写音频的 Agent 技能：自动编号、每词读两遍、留出书写时间，用老师或家长自己的克隆音色朗读，附按播放顺序编号的答案和 LRC 时间轴，本地无需显卡。

- 词表一行一个 → `dictation.wav`（编号 + 重复 + 书写停顿）+ `answer_key.txt` + `dictation.lrc` / `.srt`
- `--say word|hint|both`：读词、只读提示（如中文意思写英文）、两者都读；`== 第一单元 ==` 分节
- `--shuffle --seed 7` 每节内打乱顺序，同一种子顺序固定，答案和音频一致

## 安装

把本文件夹 `dictation-audio/` 复制到 Agent 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`），或在技能市场一键安装。完整用法、工作流和 FAQ 见 [SKILL.md](./SKILL.md)。

```bash
python3 scripts/dictation.py selftest     # 离线自检，不需要 Key
python3 scripts/dictation.py build examples/chinese_words.txt -o out_zh --gap 8 --dry-run
```

正式生成需要 Python 3.9+、环境变量 `MIRAGEA_API_KEY` 和账号里你自己的角色（Miragea：https://miragea.ai）。
