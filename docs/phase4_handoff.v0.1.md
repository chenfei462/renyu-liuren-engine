# 第 4 阶段交接说明 v0.1

阶段：实时语音原型 MVP  
目标：用 FastAPI + 静态 WebRTC 页面，把第 2 阶段排盘引擎和第 3 阶段解释器包装成 OpenAI Realtime 可调用的浏览器语音原型。

## 已交付

| 项目 | 文件 | 说明 |
|---|---|---|
| FastAPI 应用 | `src/liuren_engine/webapp.py` | 提供 `/health`、`/api/liuren/interpret`、`/api/realtime/session` |
| Realtime 客户端 | `src/liuren_engine/realtime.py` | 构造 `gpt-realtime` 会话配置并调用 `/v1/realtime/calls` |
| WebRTC 原型页 | `static/realtime/` | 麦克风、远端音频、data channel、工具调用日志、解释预览 |
| Schema | `schemas/` | 新增 Realtime session 和本地工具调用请求/响应契约 |
| 测试 | `tests/test_realtime_service.py`、`tests/test_realtime_frontend.py` | Mock OpenAI SDP 请求，不真实调用外部 API |
| 启动脚本 | `scripts/run_realtime_server.ps1` | 设置 `PYTHONPATH` 并启动 uvicorn |
| 手动验收脚本 | `docs/phase4_manual_acceptance.v0.1.md` | 浏览器语音流程验收步骤 |

## 启动方式

```powershell
cd D:\Desktop\六壬
$env:OPENAI_API_KEY="sk-..."
.\scripts\run_realtime_server.ps1
```

打开：

```text
http://127.0.0.1:8000/
```

## API

- `GET /health`
  返回引擎、知识库、Realtime 模型和 API key 是否配置；不会返回密钥原文。

- `POST /api/liuren/interpret`
  接收 `question`、`datetime`、`timezone`、`location`、`category`、`mode`，返回 `chart`、`evidence`、`interpretation`、`safety`、`latency_ms`。

- `POST /api/realtime/session`
  接收浏览器 SDP offer，服务端使用 `OPENAI_API_KEY` 调 OpenAI Realtime `/v1/realtime/calls`，返回 SDP answer。

## Realtime 工具约束

Realtime 会话只暴露一个工具：`create_liuren_interpretation`。系统指令要求模型不得自行排盘、不得伪造出处，必须基于工具返回的 `chart`、`evidence`、`interpretation` 回答。高风险分类只允许播报 `safety_only` 内容。

## 验收状态

- FastAPI 工具接口通过单元测试。
- Realtime SDP 请求使用 mock 验证，不泄露 `OPENAI_API_KEY`。
- 前端静态文件包含 WebRTC、麦克风、data channel、function call output、`response.create` 和 `response.cancel` 流程。
- 全量测试包含第 2、3、4 阶段回归。

## 当前限制

- 测试环境不真实调用 OpenAI Realtime；真实语音体验需要有效 `OPENAI_API_KEY` 和浏览器麦克风权限。
- 前端是原型页，不含登录、持久化、移动端深度适配或生产级错误恢复。
- 工具调用由浏览器 data channel 转发到本地后端；后续生产化可改为服务端控制工具调用和审计日志。
