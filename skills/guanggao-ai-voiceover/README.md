# 广告片配音

「广告片配音」是一个把品牌广告、企业宣传片、产品介绍和 App 演示视频脚本一键生成旁白与对白 AI 配音（WAV）和 SRT 字幕的 Agent 技能，停顿和语速可精细控制，同一品牌声音可出 10 种语言版本，本地无需显卡。

- 旁白 + 对白多角色，停顿精确到小数秒，给画面和音乐留白
- 同一品牌声音一份脚本出 10 种语言版本，适合多市场投放
- 输出配音 WAV + SRT + 逐句时间轴，按时间轴剪辑和对字幕

## 安装

```bash
npx skills add yanghhu/miragea-voiceover-skills
```

也可以把本文件夹 `guanggao-ai-voiceover/` 直接复制到 Agent 的 skills 目录（如 `~/.claude/skills/`）。完整用法、写稿方法和 FAQ 见 [SKILL.md](./SKILL.md)。

需要 Python 3.9+ 和环境变量 `MIRAGEA_API_KEY`（在 https://miragea.ai/workspace/api 生成）；没有 Key 可先加 `--dry-run` 离线试跑。MIT License。
