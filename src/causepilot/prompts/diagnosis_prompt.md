# Diagnosis prompt template

给定告警事件和必要观测数据，输出结构化的诊断结果。输出格式应符合 `DiagnosisResult` 模型，至少包含 `top_causes` 三项，每项包含置信度与摘要证据。

示例：

1. 请先判断告警类型（latency_spike / error_spike / resource_exhaustion / other）
2. 决定需要调用的观测工具（metrics / logs / traces）
3. 汇总证据并输出 Top 3 候选原因
