# 叫卖录音

「叫卖录音」是一个把叫卖词变成喇叭可循环播放音频的 Agent 技能：一行一句写好叫卖词，用你自己的克隆音色生成响亮的喊话录音，自动循环成 10 分钟等长音频，可加“叮咚”提示音，本地无需显卡。

- 叫卖词一行一句 → single.wav（单遍）+ loop.wav（自动循环到指定分钟数）
- `--chime` 每遍前加叮咚提示音（超市 / 门店广播），峰值归一更响亮；每句可写 `(语气标签)`
- 6 个原创场景模板：地摊清仓、水果摊、早餐铺、超市闭店、门店促销、旧物回收

## 安装

把本文件夹 `jiaomai-shout-recording/` 复制到 Agent 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`），或在技能市场一键安装。完整用法、工作流和 FAQ 见 [SKILL.md](./SKILL.md)。

```bash
python3 scripts/shout_loop.py selftest     # 离线自检，不需要 Key
python3 scripts/shout_loop.py build examples/stall_clearance.txt -o out --loop-minutes 3 --dry-run
```

正式生成需要 Python 3.9+、环境变量 `MIRAGEA_API_KEY` 和账号里你自己的角色（Miragea：https://miragea.ai）。
