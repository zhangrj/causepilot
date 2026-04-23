# CausePilot Phase 1 项目开发目标文档（面向 Claude / Codex 的实现规范）

## 1. 文档目的

本文档用于约束 **CausePilot Phase 1** 的开发范围、技术方案、输入输出契约、系统架构、实现边界与验收标准。  
本文档的目标读者不是产品经理，而是 **Claude、Codex、Copilot、开发者本人**。因此文档强调：

*   明确范围
*   明确接口
*   明确输出格式
*   明确不做什么
*   明确完成标准

***

## 2. Phase 1 目标概述

Phase 1 仅实现一个核心能力：

> **接收告警 → 分析告警 → 通过外部部署的 observe-mcp-server 拉取必要的可观测数据 → 输出 Top 3 可能原因、置信度、推荐排查动作**

其中，`observe-mcp-server` 已由外部部署并通过 **HTTP** 提供访问，**端点地址在本项目中可配置**。  
本阶段不实现用户反馈闭环、不实现自动学习、不实现评测平台、不实现复杂工作流，仅在代码结构上为这些能力保留扩展位置。

`observe-mcp-server` 的目标是将 **Prometheus 指标、OpenObserve 日志、SkyWalking 调用链** 统一暴露为 MCP 能力，并且强调“**面向业务语义的观测入口**”，而不是只暴露底层技术对象。 [\[github.com\]](https://github.com/zhangrj/observe-mcp-server), [\[jishuzhan.net\]](https://jishuzhan.net/article/2043871595945590785), [\[mcpmarket.com\]](https://mcpmarket.com/zh/server/observe-1)

***

## 3. 本阶段范围（In Scope）

Phase 1 必须实现以下功能：

### 3.1 告警输入

系统能够接收一条标准化告警输入，至少包含：

*   告警标题
*   严重级别
*   服务名
*   环境
*   时间窗口
*   告警指标（如延迟 / 错误率 / CPU）
*   当前值与阈值
*   可选标签 / 注释

### 3.2 告警诊断 Agent

系统内部实现一个诊断 Agent，对输入告警进行分析，并决定需要调用哪些观测工具。

### 3.3 MCP 接入

系统通过 **HTTP 方式**连接外部部署的 `observe-mcp-server`，并调用其 MCP 工具获取必要观测数据。  
MCP 是一个开放协议，用于让 AI 应用以统一方式接入外部工具与数据；协议核心能力包括 Tools / Resources / Prompts，并基于 JSON-RPC 风格交互。 [\[pep8.org\]](https://pep8.org/?ref=w3use), [\[mcpcn.com\]](https://mcpcn.com/)

### 3.4 诊断输出

系统输出一个结构化诊断结果，至少包含：

*   Top 3 可能原因
*   每个原因的置信度
*   每个原因的核心证据摘要
*   推荐排查动作（推荐下一步调查项）

### 3.5 基础可配置能力

系统需支持以下配置项：

*   `observe_mcp_server_url`
*   LLM provider / model
*   request timeout
*   最大工具调用次数
*   日志级别

### 3.6 基础日志与可观测性

系统需记录最小必要运行日志，包括：

*   收到的告警 ID / 标题
*   调用了哪些 MCP 工具
*   诊断是否成功
*   失败原因（若失败）

***

## 4. 本阶段不做（Out of Scope）

以下内容在 Phase 1 **明确不实现**：

### 4.1 用户反馈闭环

不实现以下能力：

*   用户确认最终根因
*   用户选择 A/B/C 或“都不是”
*   保存反馈数据
*   根据反馈进行学习优化

### 4.2 自动学习 / 自主优化

不实现以下能力：

*   在线 prompt 自修改
*   自动 rerank 优化
*   离线训练集生成
*   DSPy 优化流程
*   自动经验更新

### 4.3 复杂工作流

不实现以下能力：

*   多 Agent 协作
*   人工审批工作流
*   长任务恢复
*   状态机 / Graph 编排

### 4.4 自动修复

不执行任何有副作用的动作，例如：

*   重启服务
*   回滚发布
*   修改配置
*   执行 kubectl / SQL / API 写操作

### 4.5 UI

本阶段不做 Web UI，仅允许：

*   CLI
*   API
*   代码内调用

***

## 5. 推荐技术栈

## 5.1 Agent 运行时：PydanticAI（推荐）

推荐使用 **PydanticAI** 实现 Phase 1 的诊断 Agent，原因如下：

*   支持 **MCP**
*   支持 **结构化输出**
*   支持 **类型安全**
*   支持 **可观测性 / OTel / Logfire**
*   后续容易扩展到 evals / durable execution / graph support。 [\[zhuanlan.zhihu.com\]](https://zhuanlan.zhihu.com/p/1953594370965115735)

> 注意：Phase 1 并不强制要求完整使用 PydanticAI 的全部能力，但推荐将其作为默认框架。

## 5.2 配置管理

推荐使用：

*   `pydantic-settings`

## 5.3 HTTP 客户端

推荐使用：

*   `httpx`

## 5.4 数据模型

推荐使用：

*   `pydantic`

## 5.5 测试

推荐使用：

*   `pytest`

***

## 6. 系统设计原则

## 6.1 必须结构化输出

诊断结果必须是**结构化对象**，禁止只返回一段无约束自然语言。

## 6.2 工具层与推理层解耦

系统必须把：

*   告警诊断推理
*   MCP 工具调用
*   输出模型

拆分为不同模块，避免全部逻辑堆在一个函数里。

## 6.3 配置与实现解耦

外部 MCP 端点、模型配置、超时等必须来自配置，而不是硬编码。

## 6.4 Phase 1 优先“能稳定跑通”

本阶段以**可用性与清晰性**优先，优先完成端到端闭环，不以“花哨推理链”作为目标。

## 6.5 未来扩展留好位置

尽管 Phase 1 不实现 feedback / eval / retrieval，但目录与接口要为它们预留扩展空间。

***

## 7. 外部依赖说明

## 7.1 observe-mcp-server

项目依赖外部部署的 `observe-mcp-server`。该服务用于统一访问：

*   Prometheus metrics
*   OpenObserve logs
*   SkyWalking traces。 [\[github.com\]](https://github.com/zhangrj/observe-mcp-server), [\[mcpmarket.com\]](https://mcpmarket.com/zh/server/observe-1)

该服务不只是简单暴露底层 API，还强调“**业务语义入口**”，例如：

*   stream 可以带业务描述与 alias
*   metrics 可以带语义别名
*   更适合 AI 从“业务问题”映射到“观测查询对象”。 [\[jishuzhan.net\]](https://jishuzhan.net/article/2043871595945590785), [\[gitcode.csdn.net\]](https://gitcode.csdn.net/69dc9ee154b52172bc693846.html)

### 约束

*   本项目**不重新实现 observe-mcp-server**
*   本项目只作为 MCP Client / HTTP Consumer 使用它
*   MCP 端点地址必须可配置
*   若外部服务不可用，系统需优雅失败并输出降级说明

***

## 8. 输入契约（Input Contract）

系统 Phase 1 至少支持如下输入模型：

```json
{
  "alert_id": "ALERT-001",
  "title": "checkout-service p95 latency high",
  "severity": "critical",
  "service": "checkout-service",
  "environment": "prod",
  "metric": "http_server_duration_p95",
  "current_value": 1850,
  "threshold": 800,
  "window_start": "2026-04-20T08:00:00Z",
  "window_end": "2026-04-20T08:15:00Z",
  "labels": {
    "cluster": "cn-east-1",
    "namespace": "payments"
  },
  "annotations": {
    "summary": "checkout-service latency p95 > 800ms for 15m"
  }
}
```

### 必填字段

*   `title`
*   `severity`
*   `service`
*   `environment`
*   `window_start`
*   `window_end`

### 推荐字段

*   `metric`
*   `current_value`
*   `threshold`
*   `labels`
*   `annotations`

***

## 9. 输出契约（Output Contract）

系统必须输出如下结构化结果模型。

## 9.1 DiagnosisResult

```json
{
  "incident_type": "latency_spike",
  "summary": "checkout-service 在告警窗口内出现明显延迟升高，下游依赖调用耗时占比增加。",
  "top_causes": [
    {
      "rank": 1,
      "cause_code": "downstream_dependency_slow",
      "title": "下游依赖响应变慢",
      "confidence": 0.82,
      "evidence": [
        "trace 中下游子调用耗时显著增加",
        "相关指标显示依赖服务延迟同步升高"
      ],
      "recommended_checks": [
        "检查下游服务最近发布记录",
        "检查下游服务资源使用情况"
      ]
    },
    {
      "rank": 2,
      "cause_code": "connection_pool_exhaustion",
      "title": "连接池等待导致请求排队",
      "confidence": 0.56,
      "evidence": [
        "日志中出现 acquire timeout 关键词"
      ],
      "recommended_checks": [
        "检查本服务连接池配置和等待队列"
      ]
    },
    {
      "rank": 3,
      "cause_code": "release_regression",
      "title": "最近发布引入性能回归",
      "confidence": 0.41,
      "evidence": [
        "异常开始时间与发布窗口接近"
      ],
      "recommended_checks": [
        "对比新旧版本实例表现"
      ]
    }
  ],
  "recommended_action": [
    "优先检查下游依赖服务延迟和错误率",
    "查看最近 30 分钟内相关发布变更"
  ]
}
```

***

## 10. Agent 行为要求

## 10.1 基本行为

Agent 必须：

1.  理解告警类型；
2.  判断需要调用哪些观测工具；
3.  从 MCP 拉取必要上下文；
4.  生成 Top 3 原因；
5.  给出推荐排查动作。

## 10.2 工具调用原则

Agent 调用观测工具时必须遵循：

*   尽量少调用，但保证足够证据；
*   优先查询与告警强相关的数据；
*   不做无边界全量扫描；
*   控制工具调用次数；
*   工具失败时允许降级，但必须说明证据不足。

## 10.3 输出原则

*   必须输出 3 个候选原因（不足时可降级为 1\~2 个，但要显式说明证据不足）
*   每个原因必须有置信度
*   每个原因必须有至少 1 条证据摘要
*   推荐排查动作必须可执行，而不是空泛语言

***

## 11. MCP 接入设计

## 11.1 接入方式

本项目通过 **HTTP** 调用外部部署的 `observe-mcp-server`。

## 11.2 端点配置

必须支持通过配置文件或环境变量设置：

```env
CAUSEPILOT_OBSERVE_MCP_SERVER_URL=http://your-mcp-server-endpoint
```

## 11.3 MCP 客户端模块职责

实现一个独立模块，例如：

*   `causepilot/mcp/client.py`

职责包括：

*   发起 HTTP 请求
*   管理请求超时
*   统一错误处理
*   返回结构化工具结果

## 11.4 不要把 MCP 协议处理散落到 Agent 内部

所有与外部 MCP Server 的协议交互必须封装到单独模块中，避免 Agent 逻辑直接操作原始 HTTP / JSON-RPC 细节。MCP 的核心设计就是把外部能力以统一协议暴露为标准工具入口。 [\[pep8.org\]](https://pep8.org/?ref=w3use), [\[mcpcn.com\]](https://mcpcn.com/)

***

## 12. 推荐目录结构

建议采用如下目录结构：

```text
causepilot/
├── pyproject.toml
├── README.md
├── src/
│   └── causepilot/
│       ├── __init__.py
│       ├── main.py
│       ├── config/
│       │   └── settings.py
│       ├── models/
│       │   ├── alert_event.py
│       │   └── diagnosis_result.py
│       ├── mcp/
│       │   ├── __init__.py
│       │   └── client.py
│       ├── agent/
│       │   ├── __init__.py
│       │   └── diagnosis_agent.py
│       ├── services/
│       │   └── diagnosis_service.py
│       └── prompts/
│           └── diagnosis_prompt.md
└── tests/
    ├── test_models.py
    ├── test_mcp_client.py
    └── test_diagnosis_service.py
```

***

## 13. 模块职责划分

## 13.1 `models/alert_event.py`

定义告警输入模型。

## 13.2 `models/diagnosis_result.py`

定义诊断输出模型。

## 13.3 `config/settings.py`

定义配置项：

*   MCP URL
*   模型名
*   timeout
*   max\_tool\_calls

## 13.4 `mcp/client.py`

封装 HTTP + MCP 请求。

## 13.5 `agent/diagnosis_agent.py`

定义 Agent 本身：

*   接收 alert context
*   调用 MCP 工具
*   返回结构化输出

## 13.6 `services/diagnosis_service.py`

作为业务编排入口，负责：

*   输入校验
*   调用 Agent
*   统一返回结果
*   错误包装

## 13.7 `main.py`

提供 CLI 或最小 API 入口。

***

## 14. CLI / API 要求

本阶段至少实现一种入口，推荐二选一：

### 方案 A：CLI

支持：

```bash
uv run causepilot diagnose --input alert.json
```

### 方案 B：最小 API

提供一个 POST 接口：

```http
POST /diagnose
Content-Type: application/json
```

请求体为 `AlertEvent`，响应体为 `DiagnosisResult`。

> 建议优先 CLI，再决定是否补 API。对于 Claude / Codex 开发来说，CLI 更容易快速验证。

***

## 15. 错误处理要求

系统必须显式处理以下错误：

### 15.1 MCP 连接失败

输出错误原因，例如：

*   MCP server unreachable
*   timeout
*   invalid response

### 15.2 工具返回为空

允许继续诊断，但必须在 summary 中说明“证据不足”。

### 15.3 模型输出不符合 schema

必须触发重试或显式报错，不允许吞掉错误。

### 15.4 输入不完整

必须做输入校验并返回字段级错误。

***

## 16. 日志与调试要求

至少记录以下信息：

*   alert\_id
*   service
*   environment
*   调用的工具列表
*   MCP 请求耗时
*   Agent 输出耗时
*   最终是否成功

不得在默认日志级别下输出过长原始日志全文，避免日志污染与敏感信息泄露。

***

## 17. 测试要求

Phase 1 最少要覆盖以下测试：

## 17.1 模型测试

*   `AlertEvent` 校验通过 / 失败
*   `DiagnosisResult` 校验通过 / 失败

## 17.2 MCP 客户端测试

*   正常响应
*   超时
*   连接失败
*   非法响应结构

## 17.3 诊断服务测试

*   输入完整时返回 Top 3
*   MCP 数据不足时能降级
*   输出结构始终满足 schema

> 如果外部 MCP 服务不稳定，测试中必须支持 mock MCP response。

***

## 18. 验收标准（Definition of Done）

当且仅当满足以下条件，Phase 1 视为完成：

1.  能接收一条标准化告警输入；
2.  能通过配置读取外部 `observe-mcp-server` 的 HTTP 端点；
3.  能调用 MCP 工具获取必要观测数据；
4.  能输出结构化诊断结果；
5.  能输出 Top 3 原因、置信度、推荐排查动作；
6.  有最小单元测试；
7.  有清晰 README；
8.  不实现超出 Phase 1 范围的额外复杂功能。

***

## 19. 未来扩展占位（只保留位置，不实现）

以下模块或目录可以留空或仅保留 TODO 占位：

*   `feedback/`
*   `retrieval/`
*   `evals/`
*   `storage/`
*   `taxonomy/`

这些仅用于告诉后续开发者：

> **Phase 1 之后会往这些方向扩展，但现在不要实现。**

***

## 20. 给 Claude / Codex 的实现约束（重要）

以下是给编码 Agent 的强约束：

1.  **不要实现 Phase 1 范围之外的功能**；
2.  **不要引入数据库**，除非只是为了 future placeholder；
3.  **不要实现用户反馈闭环**；
4.  **不要实现 LangGraph / 多 Agent / 持久化流程**；
5.  **不要实现自动修复动作**；
6.  **优先保证代码清晰、模块边界明确、可测试**；
7.  **输出模型必须严格类型化**；
8.  **所有外部访问都必须通过配置，不得硬编码 observe MCP 地址**。

***