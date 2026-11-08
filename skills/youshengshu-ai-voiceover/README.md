# 有声书配音

「有声书配音」是一个把小说、故事和广播剧剧本按旁白与角色分配不同音色、一键生成整章多角色 AI 朗读音频（WAV）和带角色名 SRT 字幕的 Agent 技能，适合有声书、故事号和小说推文视频，本地无需显卡。

- 旁白 + 每个角色一个音色，整章一条命令生成多角色朗读
- 段落 / 场景 / 章节停顿可控；SRT 字幕自带角色名，适合小说推文视频
- 声音克隆固定旁白声线；10 种语言做外语有声书

## 安装

```bash
npx skills add yanghhu/miragea-voiceover-skills
```

也可以把本文件夹 `youshengshu-ai-voiceover/` 直接复制到 Agent 的 skills 目录（如 `~/.claude/skills/`）。完整用法、写稿方法和 FAQ 见 [SKILL.md](./SKILL.md)。

需要 Python 3.9+ 和环境变量 `MIRAGEA_API_KEY`（在 https://miragea.ai/workspace/api 生成）；没有 Key 可先加 `--dry-run` 离线试跑。MIT License。
