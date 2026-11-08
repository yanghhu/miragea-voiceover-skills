# 带货视频配音

「带货视频配音」是一个把卖点文案一键生成快节奏 AI 配音（WAV）和竖屏大字字幕（SRT）的 Agent 技能，同一款商品可快速做出多个版本测试，适合抖音、快手、视频号、TikTok 带货短视频，本地无需显卡。

- 卖点文案逐行生成快节奏配音 + 每条最多 12 字的竖屏大字字幕
- 同一商品多个开头、多个版本，一稿一文件批量生成做测试
- 改价格、改卖点只重配一句；声音克隆；10 种语言做跨境带货

## 安装

```bash
npx skills add yanghhu/miragea-voiceover-skills
```

也可以把本文件夹 `daihuo-ai-voiceover/` 直接复制到 Agent 的 skills 目录（如 `~/.claude/skills/`）。完整用法、写稿方法和 FAQ 见 [SKILL.md](./SKILL.md)。

需要 Python 3.9+ 和环境变量 `MIRAGEA_API_KEY`（在 https://miragea.ai/workspace/api 生成）；没有 Key 可先加 `--dry-run` 离线试跑。MIT License。
