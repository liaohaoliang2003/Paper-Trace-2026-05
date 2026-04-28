# 中文 LLM Prompt 参考

在需要使用 LLM 进行引用意图、实体和关系抽取时使用这些模板。原则与 `sci_glm` 一致：标签受限、输出对齐 citation/reference ID、只返回 JSON。抽取出的 JSON 预期会直接保存为 `citation_graph.json`；不要用自然语言总结替代该文件产物。

## System Prompt

```text
你是一个学术论文分析助手。你的任务是从单篇目标论文中抽取引用意图、实体和关系。

规则：
1. 只返回合法 JSON，不要使用 Markdown 代码块包裹。
2. 只能使用用户提供的允许意图标签。
3. 每个引用意图必须由引用句、局部上下文、章节名或参考文献条目支撑。
4. 不要编造标题、作者、年份、数据集、指标或论文结论。
5. 如果参考文献无法匹配，设置 unmatched_reference=true 且 reference_id=null。
6. 如果证据较弱，降低 confidence，并用中文解释不确定性。
7. 对关键 citation，尽量写出意图判据、被引工作角色、目标论文论点和置信度理由。
8. 不要输出 API Key、隐藏推理过程、供应商元数据或私有绝对路径。
9. 生成完整对象，确保校验后可直接写入 citation_graph.json。
```

## 引用抽取 Prompt

```text
任务：从目标论文文本中抽取 citation 记录。

允许的 intent 标签：
background, problem, core-method, supporting-method, dataset, metric, baseline, tool-resource, theory, result-evidence, limitation, future-work

输入：
<paper_title>
{{paper_title}}
</paper_title>

<section_text>
{{section_text}}
</section_text>

<references>
{{references_json_or_text}}
</references>

返回以下 JSON 对象：
{
  "citations": [
    {
      "citation_id": "cit-001",
      "reference_id": "ref-001 or null",
      "unmatched_reference": false,
      "marker": "[1]",
      "section": "Introduction",
      "citation_sentence": "包含引用的原句",
      "context": "相邻上下文证据",
      "intent": "一个允许标签",
      "confidence": 0.0,
      "evidence": "基于文本的中文解释",
      "target_claim": "该引用支撑的目标论文论点；无法确认时写 unknown",
      "cited_work_role": "问题来源 / 方法组件 / 数据集来源 / 基线 / 工具 / 理论 / 结果证据 / 局限",
      "intent_rationale": "为什么该 intent 比相近标签更合适",
      "confidence_reason": "为什么置信度是高、中或低",
      "secondary_intents": [],
      "entity_mentions": ["出现的方法/数据集/指标/问题名称"],
      "coarse_intent": "background/method/result"
    }
  ]
}
```

## 实体与关系抽取 Prompt

```text
任务：将 citation 记录转换为图谱实体和关系。

只能使用 citation 记录和目标论文摘要中的证据。

输入：
<paper_summary>
{{paper_summary_json}}
</paper_summary>

<citations>
{{citations_json}}
</citations>

返回以下 JSON 对象：
{
  "entities": [
    {
      "entity_id": "ent-001",
      "name": "实体名称",
      "type": "problem/method/component/dataset/metric/task/baseline/tool-resource/theory/result/limitation/future-work",
      "description": "基于证据的中文说明",
      "source_citation_ids": ["cit-001"]
    }
  ],
  "relations": [
    {
      "relation_id": "rel-001",
      "source_id": "target-paper",
      "target_id": "ent-001",
      "relation_type": "cites-for/uses-method/uses-dataset/evaluates-with/compares-against/extends/contrasts-with/supports-claim/reveals-limitation/motivates",
      "intent": "一个允许 intent 或 null",
      "evidence": "基于文本的中文解释"
    }
  ]
}
```

## 图谱分组 Prompt

```text
任务：为中心论文放射图分组节点。

默认分组：
- problem-background: background, problem, theory
- method-core: core-method, supporting-method, tool-resource
- data-eval: dataset, metric
- baseline-result: baseline, result-evidence
- limits-future: limitation, future-work

输入：
<citation_graph>
{{citation_graph_json}}
</citation_graph>

返回以下 JSON 对象：
{
  "visual_groups": [
    {
      "group_id": "method-core",
      "label": "核心方法",
      "intent_filters": ["core-method", "supporting-method", "tool-resource"],
      "node_ids": ["cit-001", "ent-001"],
      "color": "#ef5b45"
    }
  ],
  "visual_notes": "用中文解释这张图强调了什么"
}
```

## JSON 修复 Prompt

仅在模型返回无法被 JSON 解析时使用。

```text
上一次响应不是合法 JSON。请在不新增事实的前提下修复它。

规则：
1. 只返回合法 JSON。
2. 尽量保留上一次响应中的事实字段。
3. 移除 Markdown 代码块、注释、尾随逗号和解释性文字。
4. 不要新增引用、参考文献、实体或标签。

非法响应：
{{invalid_response}}
```

## 质量审查 Prompt

```text
任务：检查 citation graph 是否存在 schema 或证据问题。

检查项：
1. 每条 citation 都有 intent、evidence、confidence，并且有 reference_id 或 unmatched_reference=true。
2. 每个 intent 都在允许标签列表中。
3. 每个 entity 至少被一条 citation 支撑。
4. 参考文献缺失时，不编造文献信息。
5. 不出现 API Key、私有绝对路径或供应商元数据。
6. 图谱包含足够的 visual_groups 和 show_on_map 信息，能够渲染 citation_map.svg 或确定性 SVG-ready 替代方案。
7. 关键 citation 不能只有空泛总结；应包含意图判据、被引工作角色、目标论文论点，或明确的不确定性说明。
8. 证据较弱、来自噪声文本或表格残片时，不得给高置信度。

返回以下 JSON 对象：
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "suggested_repairs": []
}
```
