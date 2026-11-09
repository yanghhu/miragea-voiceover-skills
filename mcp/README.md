# MCP 服务器 · MCP Servers

AI配音 MCP / 文字转语音 MCP / 播客生成 MCP / 字幕生成 MCP — AI voiceover, text to speech, two-host podcast & multi-speaker dubbing (WAV + SRT), subtitle generation.

| 目录 Folder | 服务 Service | 环境变量 Env | 说明 |
|---|---|---|---|
| [quips-voiceover-mcp](quips-voiceover-mcp) | 灵声妙语 Quips（国内，https://www.quips.cn） | `QUIPS_API_KEY` | 中文文档；国内用户使用 |
| [miragea-voiceover-mcp](miragea-voiceover-mcp) | Miragea（海外，https://miragea.ai） | `MIRAGEA_API_KEY` | English docs; for users outside mainland China |

两者工具相同：`get_capabilities`、`list_voices`、`text_to_speech`、`dialogue_voiceover`、`generate_subtitles`、`get_task`，以及提示词 `two_host_podcast`、`multi_character_dubbing`。Python 3.9+ 标准库，stdio 传输。

Both expose the same tools and prompts. Python 3.9+ standard library, stdio transport. Install via `uvx --from "git+https://github.com/yanghhu/miragea-voiceover-skills#subdirectory=mcp/<folder>" <folder>`, the `.mcpb` bundles in `mcp/dist/`, or as a WorkBuddy / CodeBuddy / Claude Code plugin (`/plugin marketplace add yanghhu/miragea-voiceover-skills`).
