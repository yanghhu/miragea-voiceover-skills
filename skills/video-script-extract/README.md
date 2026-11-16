# 视频文案提取

「视频文案提取」是一个把本地视频或音频里的口播变成可编辑文稿的 Agent 技能：识别语音，输出 TXT 文字稿、SRT 字幕和按句拆好的改写表；你改写成原创文案后，再用自己克隆的音色重新配音，本地无需显卡。

- 本地视频 / 音频 → transcript.txt 文字稿 + transcript.srt 时间轴字幕 + rewrite.md 按句改写表
- 改写由你或 Agent 完成（只写原创表达），rewrite.md 一键重新配音，输出 WAV 和 SRT 字幕
- 无 Key 时 --dry-run 离线跑通；本地只用 Python 3.9+ 标准库

## 安装

把本文件夹 `video-script-extract/` 复制到 Agent 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`），或在技能市场一键安装。完整用法、工作流和 FAQ 见 [SKILL.md](./SKILL.md)。

```bash
python3 scripts/video_copy.py extract -o out --dry-run   # 无需 Key，离线试跑
```

正式配音需要 Python 3.9+、环境变量 `MIRAGEA_API_KEY` 和账号里克隆好的音色（Miragea：https://miragea.ai）。
