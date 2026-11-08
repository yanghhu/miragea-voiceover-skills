# 电影解说配音

「电影解说配音」是一个把影视解说稿一键生成“解说旁白 + 多角色台词”多音色配音（WAV）、SRT 字幕和逐句时间轴的 Agent 技能，适合电影、电视剧、短剧解说号批量更新，本地无需显卡。

- 旁白 + 多个角色各用不同音色，一条命令出整段解说音轨
- 同时输出 SRT 字幕和逐句时间轴 JSON，剪映里按时间对画面
- 5–10 秒样本克隆解说号专属声线，10 种语言做海外解说

## 安装

```bash
npx skills add yanghhu/miragea-voiceover-skills
```

也可以把本文件夹 `movie-recap-ai-voiceover/` 直接复制到 Agent 的 skills 目录（如 `~/.claude/skills/`）。完整用法、写稿方法和 FAQ 见 [SKILL.md](./SKILL.md)。

需要 Python 3.9+ 和环境变量 `MIRAGEA_API_KEY`（在 https://miragea.ai/workspace/api 生成）；没有 Key 可先加 `--dry-run` 离线试跑。MIT License。
