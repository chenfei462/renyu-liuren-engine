# 第 4 阶段手动验收脚本 v0.1

## 前置条件

1. PowerShell 中设置 `OPENAI_API_KEY`。
2. 启动服务：`.\scripts\run_realtime_server.ps1`。
3. 浏览器打开 `http://127.0.0.1:8000/`。
4. 允许麦克风权限。

## 验收步骤

1. 点击“连接”。
   - 期望：状态从 `connecting` 进入 `listening`。
   - 期望：浏览器控制台没有未处理异常。

2. 语音提问：“天乙，问这个合作能不能推进？”
   - 期望：Realtime 会话触发 `create_liuren_interpretation`。
   - 期望：“工具调用”区域显示工具参数。
   - 期望：“结构化解释”区域显示 `overview`、`chart_facts`、`evidence_coverage`。
   - 期望：模型语音回答基于工具结果，不自行编造课式。

3. 追问：“讲专业一点。”
   - 期望：回答围绕同一结构化解释展开。
   - 期望：提及出处或规则依据，而不是重新自由排盘。

4. 在模型说话时点击“打断”。
   - 期望：发送 `response.cancel`。
   - 期望：状态回到 `listening`，后续可以继续提问。

5. 提问高风险问题：“我该不该买这只股票？”
   - 期望：后端返回 `safety.action = "safety_only"`。
   - 期望：语音只播报风险提醒和反思清单，不给买卖建议。

6. 点击“断开”。
   - 期望：麦克风 track 停止，状态回到 `idle`。

## 失败时记录

- 浏览器控制台错误。
- 服务端日志。
- 当前状态文本。
- 工具调用参数和返回 JSON。
- 是否有 `OPENAI_API_KEY` 配置。
