# 视频配音神器

「视频配音神器」是一个把视频文字稿一键生成多角色 AI 配音（WAV）和带时间轴 SRT 字幕的 Agent 技能，支持 5–10 秒声音克隆和 10 种语言，覆盖口播、电影解说、带货、数字人、广告片和有声书，本地无需显卡。

- 文字稿 → 多角色配音 WAV + 带时间轴 SRT 字幕 + 逐句时间 JSON，一条命令
- 5–10 秒声音克隆；中英日韩德法俄葡西意 10 种语言；音视频转字幕
- 6 个场景预设（口播、解说、带货、数字人、广告片、有声书）；本地无需显卡

## 安装

```bash
npx skills add yanghhu/miragea-voiceover-skills
```

也可以把本文件夹 `miragea-video-voiceover/` 直接复制到 Agent 的 skills 目录（如 `~/.claude/skills/`）。完整用法、写稿方法和 FAQ 见 [SKILL.md](./SKILL.md)。

需要 Python 3.9+ 和环境变量 `MIRAGEA_API_KEY`（在 https://miragea.ai/workspace/api 生成）；没有 Key 可先加 `--dry-run` 离线试跑。MIT License。
