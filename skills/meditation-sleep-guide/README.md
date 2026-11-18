# 冥想引导

「冥想引导」是一个把引导语稿子做成冥想 / 助眠音频的 Agent 技能：用你自己的克隆音色慢语速朗读，按目标分钟数自动排布段间长停顿，输出音频、字幕和时间表，本地无需显卡。

- 引导语 TXT（空行分段，`[停顿 8]` 固定停顿）→ `guide.wav` + `guide.srt` + `guide.lrc` + `plan.txt`
- `--minutes 10`：把剩余时间平均分给段间停顿（`--gap` 基础停顿、`--max-gap` 单处上限）；先 `plan` 离线预估
- 默认慢语速 0.85（`--speed` 可调 0.25–4）；按句缓存，断点续跑，改一段只重配一段

## 安装

把本文件夹 `meditation-sleep-guide/` 复制到 Agent 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`），或在技能市场一键安装。完整用法、工作流和 FAQ 见 [SKILL.md](./SKILL.md)。

```bash
python3 scripts/sleep_guide.py selftest     # 离线自检，不需要 Key
python3 scripts/sleep_guide.py build examples/body_scan.txt -o guide --minutes 5 --voice 默认 --dry-run
```

正式生成需要 Python 3.9+、环境变量 `MIRAGEA_API_KEY` 和账号里你自己的角色（Miragea：https://miragea.ai）。
