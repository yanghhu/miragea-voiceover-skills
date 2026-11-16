# 彩铃制作

「彩铃制作」是一个批量生成企业彩铃和 IVR 语音导航提示音的 Agent 技能：话术一行一条，用你自己的克隆音色生成，按 id 命名导出 8k / 16k、PCM 或 A-law / μ-law 电话格式，并能拼出循环彩铃，本地无需显卡。

- `id: 文本` 一行一条 → `phone/id.wav`（电话格式）+ `hq/id.wav`（24 kHz 母版）+ `prompts.csv`
- 8000 / 16000 Hz，16 位 PCM 或 8 位 G.711 A-law / μ-law；`inspect` 核对任意 WAV 的格式
- `--ringback welcome,slogan --ringback-seconds 30` 拼出彩铃

## 安装

把本文件夹 `ringback-ivr-prompts/` 复制到 Agent 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`），或在技能市场一键安装。完整用法、工作流和 FAQ 见 [SKILL.md](./SKILL.md)。

```bash
python3 scripts/phone_prompts.py selftest     # 离线自检，不需要 Key
python3 scripts/phone_prompts.py build examples/company_ivr.txt -o out --codec alaw --ringback welcome,slogan --ringback-seconds 30 --dry-run
```

正式生成需要 Python 3.9+、环境变量 `MIRAGEA_API_KEY` 和账号里你自己的角色（Miragea：https://miragea.ai）。
