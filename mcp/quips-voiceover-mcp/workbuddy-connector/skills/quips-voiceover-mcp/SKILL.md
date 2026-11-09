---
name: quips-voiceover-mcp
description: AI配音 MCP 使用指南：用 quips-voiceover-mcp 的工具做文字转语音、双人播客/多角色对话配音（输出 WAV+SRT+时间轴）和音视频字幕生成；包含选音色、写对话稿、断点续跑和额度确认的步骤。
version: "1.0.0"
author: Quips
---

# 灵声妙语 AI配音 MCP（文字转语音·播客生成·字幕生成） 使用指南

工具由 MCP 服务器 `quips-voiceover-mcp` 提供（灵声妙语（Quips） 官方 API）。生成类工具会消耗账号额度。

## 步骤
1. `get_capabilities`：确认可用模式（model）、语气标签、单次字数上限。
2. `list_voices`：按名字找到每个角色的 `actor_id`；同名时让用户选。用户要用自己的声音时，请他提供公网可访问的参考音频 URL 和音频原文，并确认有授权。
3. 写稿：双人播客/多人配音写成每行 `[角色] 台词`，章节间 `[pause 0.8]`；可用提示词 `two_host_podcast` / `multi_character_dubbing`。
4. 把稿子、角色与音色对应关系给用户确认后再生成。
5. 调用：单段文字 `text_to_speech`（长文加 `subtitles: true`）；对话稿 `dialogue_voiceover`（style: podcast / dubbing / audiobook）；音视频转字幕 `generate_subtitles`。
6. 汇报：返回的 `audio_wav`、`subtitles_srt`、`manifest_json` 绝对路径和时长。提醒发布时标注 AI 生成内容。

## 出错处理
- `missing_api_key`：请用户设置环境变量 `QUIPS_API_KEY`；或用 `dry_run: true` 先离线试跑。
- `speaker_without_voice`：给缺音色的角色补 `actor_id` 或参考音频。
- `wait_timeout` / 客户端超时：用相同参数再次调用 `dialogue_voiceover` 续跑；单任务用 `get_task` 取结果，不要重新提交。
- 400 修正参数（字数、标签、语速）；401 检查 Key；403 检查 API 权限；429 等待或补充额度。
