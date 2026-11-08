# 口播配音神器

「口播配音神器」是一个把口播稿一键变成本人克隆声音配音（WAV）和竖屏字幕（SRT）的 Agent 技能，适合每天更新的知识、财经、情感口播博主，只需 5–10 秒录音克隆音色，改一句只重配一句。

- 5–10 秒样本克隆你的口播音色，之后只写稿不录音
- 一条命令输出配音 WAV + 竖屏 SRT 字幕 + 逐句时间轴 JSON
- 改一句只重配一句；10 种语言；本地无需显卡

## 安装

```bash
npx skills add yanghhu/miragea-voiceover-skills
```

也可以把本文件夹 `koubo-ai-voiceover/` 直接复制到 Agent 的 skills 目录（如 `~/.claude/skills/`）。完整用法、写稿方法和 FAQ 见 [SKILL.md](./SKILL.md)。

需要 Python 3.9+ 和环境变量 `MIRAGEA_API_KEY`（在 https://miragea.ai/workspace/api 生成）；没有 Key 可先加 `--dry-run` 离线试跑。MIT License。
