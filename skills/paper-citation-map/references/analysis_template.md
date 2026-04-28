# Fixed `analysis.md` Template

Use this template only when the user explicitly asks for a template, compliance format, standard format, fixed structure, or similar wording. The generated report must be Chinese and must keep the section order below.

Do not invent citations to fill a section. If no reliable evidence supports an intent or table row, write `未发现可靠证据` and explain the gap briefly.

## Required Markdown Structure

```markdown
# 论文引用意图分析：<paper_title>

## 1. 结论先行

- **一句话总结**：<用 1-2 句话说明目标论文解决什么问题、提出什么方法、最核心贡献是什么。>
- **引用结构判断**：<说明参考文献主要支撑背景、核心方法、数据/评估、基线还是局限。>
- **读者应优先关注**：<列出 3-5 个最能帮助理解论文的引用或引用组。>

## 2. 目标论文核心内容

| 项目 | 内容 |
| --- | --- |
| 论文标题 | <paper_title> |
| 核心任务 | <任务或问题> |
| 核心方法 | <方法名与关键组件> |
| 主要贡献 | <贡献要点，优先来自摘要、引言或结论> |
| 主要实验对象 | <数据集、任务、评价对象> |

## 3. 引用意图总览

| 意图标签 | 引用数量 | 代表引用 | 对理解论文的作用 |
| --- | ---: | --- | --- |
| `background` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |
| `problem` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |
| `core-method` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |
| `supporting-method` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |
| `dataset` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |
| `metric` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |
| `baseline` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |
| `tool-resource` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |
| `theory` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |
| `result-evidence` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |
| `limitation` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |
| `future-work` | <n> | <reference_id/title or 未发现可靠证据> | <作用> |

## 4. 按意图分组的引用分析

### 4.1 `<intent>`：<中文组名>

| 字段 | 内容 |
| --- | --- |
| 判断依据 | <为什么这些引用属于该 intent> |
| 关键引用 | <reference_id/title list> |
| 证据片段 | <引用句或局部上下文短摘录；避免长篇复制> |
| 置信度/不确定性 | <high/medium/low 与原因> |

Repeat `### 4.x` only for intents with evidence. If an expected intent is absent, state `未发现可靠证据` in a short paragraph instead of inventing citations.

## 5. 核心方法引用链


| 方法组件 | 支撑引用 | 引用意图 | 证据与作用 |
| --- | --- | --- | --- |
| <component> | <reference_id/title> | `<intent>` | <how it supports the target method> |

## 6. 数据集、指标与基线引用

| 类型 | 名称 | 支撑引用 | 在论文中的作用 |
| --- | --- | --- | --- |
| 数据集 | <dataset> | <reference_id/title> | <evaluation role> |
| 指标 | <metric> | <reference_id/title or 未发现可靠证据> | <measurement role> |
| 基线 | <baseline> | <reference_id/title> | <comparison role> |

## 7. 实体与关系图谱解读


- **中心节点**：<target paper / method>。
- **关键实体**：<methods, datasets, metrics, tasks, problems, results>。
- **关键关系**：<paper -> method / dataset / baseline / result relationships>。
- **图谱阅读路径**：<how to read citation_map.svg from problem to method to evaluation>。

## 8. 覆盖范围、噪声与不确定性


- **覆盖范围**：<which sections/citation contexts were analyzed>。
- **PDF/文本噪声**：<if any table/figure/reference extraction noise exists>。
- **参考文献匹配不确定性**：<unmatched or ambiguous references>。
- **SVG 生成状态**：<whether citation_map.svg was generated; if not, why>。

## 9. 输出文件清单

| 文件 | 状态 | 说明 |
| --- | --- | --- |
| `analysis.md` | 已生成 | 当前规范化分析报告 |
| `citation_graph.json` | 已生成 | 结构化引用意图图谱，必须可被 JSON 解析 |
| `citation_map.svg` | <已生成/未生成> | 中心论文放射图；未生成时说明原因 |
| `citation_map_spec.md` | <可选/未使用> | 仅在 SVG 无法生成时作为替代说明 |
```

## Quality Rules

- Keep the section titles exactly as shown.
- Keep the required table columns exactly as shown.
- Preserve all records in `citation_graph.json`; the Markdown report may summarize dense groups.
- Use concise evidence excerpts, not long copied passages.
- Do not include API keys, private absolute paths, provider metadata, or hidden reasoning traces.
