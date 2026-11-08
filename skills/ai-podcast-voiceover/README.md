# AI播客

「AI播客」是一个把文章、笔记或对谈稿做成单人或双人播客音频的 Agent 技能：逐句配音拼成整期节目，同时输出 SRT 字幕、带时间戳的节目章节和完整文字稿，本地无需显卡。

- 单人主播或两位主持人各用一个音色，一条命令出整期节目 WAV + SRT
- 稿件里的 `## 章节` 自动变成带时间戳的 chapters.txt / chapters.json 和 shownotes.md 文字稿
- 改一句只重配一句；支持账号角色或本人授权的参考音频声音

## 安装

把本文件夹 `ai-podcast-voiceover/` 复制到 Agent 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`）即可，也可以在技能市场一键安装。完整用法、写稿方法和 FAQ 见 [SKILL.md](./SKILL.md)。

需要 Python 3.9+ 和环境变量 `MIRAGEA_API_KEY`（在 https://miragea.ai/workspace/api 生成）；没有 Key 可先加 `--dry-run` 离线试跑。配音与字幕由 Miragea（https://miragea.ai）提供。
