# 数字人配音

「数字人配音」是一个用本人克隆声音把口播稿生成干净人声驱动音频（WAV）、SRT 字幕和逐句时间轴的 Agent 技能，生成的音频可导入各类数字人、虚拟主播、AI 分身工具驱动口型，本地无需显卡。

- 本人 5–10 秒样本克隆声音，形象和声音都是“你”
- 输出无背景音乐的干净人声 WAV，适合驱动数字人口型；附 SRT 和逐句时间轴
- 一段一镜头分文件生成；10 种语言做数字人多语种口播

## 安装

```bash
npx skills add yanghhu/miragea-voiceover-skills
```

也可以把本文件夹 `shuziren-ai-voiceover/` 直接复制到 Agent 的 skills 目录（如 `~/.claude/skills/`）。完整用法、写稿方法和 FAQ 见 [SKILL.md](./SKILL.md)。

需要 Python 3.9+ 和环境变量 `MIRAGEA_API_KEY`（在 https://miragea.ai/workspace/api 生成）；没有 Key 可先加 `--dry-run` 离线试跑。MIT License。
