# 引用图谱 Schema

本文档定义 `citation_graph.json` 的中文说明版 schema。字段名与英文版保持一致，便于未来 CLI、SVG 渲染器和 Web 工具共用。

`citation_graph.json` 是本 Skill 的最低必需文件产物。只要工作区可写，即使 `citation_map.svg` 暂时无法生成，也必须保存该 JSON。图谱应包含足够的 `visual_groups`、citation `intent`、`evidence` 和可选 `show_on_map` 提示，便于渲染器或后续 Agent 继续生成 SVG。

## 顶层对象

```json
{
  "schema_version": "0.1.0",
  "paper": {},
  "references": [],
  "citations": [],
  "entities": [],
  "relations": [],
  "visual_groups": [],
  "metadata": {}
}
```

## `paper`

目标论文信息。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `paper_id` | string | 稳定 ID，通常为 `target-paper` |
| `title` | string | 目标论文标题；无法获得时写 `unknown` |
| `authors` | array[string] | 作者列表，无法获得时为空数组 |
| `year` | string or number | 发表年份，无法获得时写 `unknown` |
| `abstract` | string | 摘要或简短概述 |
| `core_contributions` | array[string] | 基于论文文本归纳的核心贡献 |

## `references[]`

参考文献条目。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `reference_id` | string | 稳定 ID，例如 `ref-001` |
| `marker` | string | 文中引用标记，例如 `[1]` 或 `Smith et al., 2020` |
| `title` | string | 参考文献标题；无法恢复时写 `unknown` |
| `authors` | array[string] | 参考文献作者列表 |
| `year` | string or number | 参考文献年份 |
| `raw_reference` | string | 原始参考文献条目或最可靠文本 |

可选字段：`venue`、`doi`、`url`、`notes`。

## `citations[]`

引用上下文及其意图分类。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `citation_id` | string | 稳定 ID，例如 `cit-001` |
| `reference_id` | string or null | 匹配到的参考文献 ID；未匹配时为 null |
| `unmatched_reference` | boolean | 无法可靠匹配参考文献时为 true |
| `marker` | string | 原文中的引用标记 |
| `section` | string | 引用所在章节 |
| `citation_sentence` | string | 包含引用的原句 |
| `context` | string | 引用句及其局部上下文 |
| `intent` | string | 一个允许的引用意图标签 |
| `confidence` | number | 0.0 到 1.0 的置信度 |
| `evidence` | string | 中文证据解释 |

可选字段：

- `secondary_intents`：次要引用意图标签数组。
- `entity_ids`：关联实体 ID。
- `coarse_intent`：`background`、`method` 或 `result`。
- `notes`：不确定性或抽取说明。
- `show_on_map`：布尔值；对应该展示到 `citation_map.svg` 的引用设置为 `true`，尤其是 `core-method`、`dataset`、`metric`、`baseline` 引用。
- `target_claim`：该引用支撑的目标论文论点、方法选择、数据选择或结果解释。
- `cited_work_role`：被引工作的角色，例如问题来源、方法组件、数据集来源、基线、工具、理论、结果证据或局限。
- `intent_rationale`：为什么当前 intent 比相近标签更合适。
- `confidence_reason`：为什么置信度是高、中或低。

这些解释字段是可选质量字段，用于增强 `analysis.md` 的分析深度；它们不替代必需的 `intent`、`evidence`、`confidence` 和参考文献链接字段。

校验规则：每条 citation 必须包含 `intent`、`evidence`，并且必须有非空 `reference_id` 或 `unmatched_reference: true`。不要输出既无参考文献链接、也未明确标记 unmatched 的 citation。

允许的 `intent`：

```text
background
problem
core-method
supporting-method
dataset
metric
baseline
tool-resource
theory
result-evidence
limitation
future-work
```

## `entities[]`

论文图谱中的概念实体。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `entity_id` | string | 稳定 ID，例如 `ent-001` |
| `name` | string | 实体名称 |
| `type` | string | 实体类型 |
| `description` | string | 基于证据的中文说明 |
| `source_citation_ids` | array[string] | 支持该实体的 citation ID |

允许的 `type`：

```text
problem
method
component
dataset
metric
task
baseline
tool-resource
theory
result
limitation
future-work
```

## `relations[]`

节点之间的关系边。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `relation_id` | string | 稳定 ID，例如 `rel-001` |
| `source_id` | string | 源节点 ID，可为论文、引用、参考文献或实体 |
| `target_id` | string | 目标节点 ID |
| `relation_type` | string | 关系类型 |
| `intent` | string or null | 与引用相关时填写意图标签 |
| `evidence` | string | 基于文本的中文证据说明 |

推荐的 `relation_type`：

```text
cites-for
uses-method
uses-dataset
evaluates-with
compares-against
extends
contrasts-with
supports-claim
reveals-limitation
motivates
```

## `visual_groups[]`

可视化图中的语义分组。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `group_id` | string | 稳定分组 ID |
| `label` | string | 中文显示名称 |
| `intent_filters` | array[string] | 该组包含的引用意图 |
| `node_ids` | array[string] | 该组展示的节点 ID |
| `color` | string | 分组颜色，使用 hex |

默认分组：

| `group_id` | 显示名 | 意图 |
| --- | --- | --- |
| `problem-background` | 问题背景 | `background`, `problem`, `theory` |
| `method-core` | 核心方法 | `core-method`, `supporting-method`, `tool-resource` |
| `data-eval` | 数据与评估 | `dataset`, `metric` |
| `baseline-result` | 基线与结果 | `baseline`, `result-evidence` |
| `limits-future` | 局限与未来 | `limitation`, `future-work` |

## `metadata`

抽取元信息。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `source_file` | string | 相对输入文件名；避免私有绝对路径 |
| `created_at` | string | 可用时填写 ISO 风格时间戳 |
| `extraction_method` | string | `manual`、`llm`、`cli` 或 `hybrid` |
| `coverage_notes` | string | 缺失章节、PDF 噪声或匹配不确定性说明 |

## 最小示例

```json
{
  "schema_version": "0.1.0",
  "paper": {
    "paper_id": "target-paper",
    "title": "Attention Is All You Need",
    "authors": ["Ashish Vaswani", "Noam Shazeer"],
    "year": 2017,
    "abstract": "A sequence transduction model based entirely on attention mechanisms.",
    "core_contributions": ["提出 Transformer 架构", "用自注意力替代循环结构"]
  },
  "references": [
    {
      "reference_id": "ref-001",
      "marker": "[1]",
      "title": "Neural Machine Translation by Jointly Learning to Align and Translate",
      "authors": ["Dzmitry Bahdanau", "Kyunghyun Cho", "Yoshua Bengio"],
      "year": 2014,
      "raw_reference": "Bahdanau et al. Neural Machine Translation by Jointly Learning to Align and Translate. 2014."
    }
  ],
  "citations": [
    {
      "citation_id": "cit-001",
      "reference_id": "ref-001",
      "unmatched_reference": false,
      "marker": "[1]",
      "section": "Introduction",
      "citation_sentence": "Attention mechanisms have become an integral part of sequence modeling and transduction models [1].",
      "context": "Attention mechanisms have become an integral part of sequence modeling and transduction models [1].",
      "intent": "core-method",
      "confidence": 0.86,
      "evidence": "该引用为目标论文的自注意力机制提供直接方法来源。",
      "secondary_intents": ["background"],
      "entity_ids": ["ent-001"],
      "coarse_intent": "method"
    }
  ],
  "entities": [
    {
      "entity_id": "ent-001",
      "name": "attention mechanism",
      "type": "method",
      "description": "序列建模中的注意力机制，是 Transformer 的核心方法基础。",
      "source_citation_ids": ["cit-001"]
    }
  ],
  "relations": [
    {
      "relation_id": "rel-001",
      "source_id": "target-paper",
      "target_id": "ent-001",
      "relation_type": "uses-method",
      "intent": "core-method",
      "evidence": "目标论文围绕 attention mechanism 构建主要架构。"
    }
  ],
  "visual_groups": [
    {
      "group_id": "method-core",
      "label": "核心方法",
      "intent_filters": ["core-method", "supporting-method", "tool-resource"],
      "node_ids": ["cit-001", "ent-001"],
      "color": "#ef5b45"
    }
  ],
  "metadata": {
    "source_file": "attention-is-all-you-need.pdf",
    "extraction_method": "manual",
    "coverage_notes": "仅用于展示 schema 的最小示例。"
  }
}
```
