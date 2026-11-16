# AI有声书

「AI有声书」是一个把整本小说或长篇文字变成分章节有声书的 Agent 技能：自动识别章节，用你自己的克隆音色逐章配音，每章一个音频文件，附 SRT / LRC 字幕和播放列表，断点续跑，本地无需显卡。

- 整本 TXT → 自动识别章节 → 每章一个 WAV + SRT + LRC，外加 playlist.m3u 和 chapters.json
- 先 `plan` 离线看分章结果、字数和预计时长，再 `build`；`--chapters 1-3` 先做试听章
- 引号对白可换第二个音色；按句缓存，断点续跑，改哪句只重配哪句

## 安装

把本文件夹 `ai-audiobook-maker/` 复制到 Agent 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`），或在技能市场一键安装。完整用法、工作流和 FAQ 见 [SKILL.md](./SKILL.md)。

```bash
python3 scripts/audiobook.py selftest     # 离线自检，不需要 Key
python3 scripts/audiobook.py build examples/sample_book.txt -o out --chapters 1-2 --dry-run
```

正式生成需要 Python 3.9+、环境变量 `MIRAGEA_API_KEY` 和账号里你自己的角色（Miragea：https://miragea.ai）。
