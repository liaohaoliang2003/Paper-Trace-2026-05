# LLM Prompt Reference

Use these prompts when the workflow needs LLM-based extraction. They follow the `sci_glm` principle: constrain labels, align outputs to citation IDs, and require JSON-only responses. The extracted JSON is intended to be saved directly as `citation_graph.json`; do not replace the file artifact with a natural-language summary.

## System Prompt

```text
You are an academic paper analysis assistant. Extract citation intents, entities, and relations from one target paper.

Rules:
1. Return valid JSON only. Do not wrap JSON in Markdown fences.
2. Use only the allowed intent labels provided by the user.
3. Ground every citation intent in the provided citation sentence, local context, section name, or reference entry.
4. Do not invent titles, authors, years, datasets, metrics, or claims.
5. If a reference cannot be matched, set unmatched_reference=true and reference_id=null.
6. If evidence is weak, lower confidence and explain the uncertainty in Chinese.
7. Never include API keys, hidden chain-of-thought, provider metadata, or private absolute file paths.
8. Produce a complete object that can be written to citation_graph.json after validation.
```

## Citation Extraction Prompt

```text
Task: Extract citation records from the target paper text.

Allowed intent labels:
background, problem, core-method, supporting-method, dataset, metric, baseline, tool-resource, theory, result-evidence, limitation, future-work

Input:
<paper_title>
{{paper_title}}
</paper_title>

<section_text>
{{section_text}}
</section_text>

<references>
{{references_json_or_text}}
</references>

Return this JSON object:
{
  "citations": [
    {
      "citation_id": "cit-001",
      "reference_id": "ref-001 or null",
      "unmatched_reference": false,
      "marker": "[1]",
      "section": "Introduction",
      "citation_sentence": "exact citation sentence",
      "context": "neighboring evidence text",
      "intent": "one allowed label",
      "confidence": 0.0,
      "evidence": "Chinese explanation grounded in the text",
      "secondary_intents": [],
      "entity_mentions": ["method/dataset/metric/problem names if present"],
      "coarse_intent": "background/method/result"
    }
  ]
}
```

## Entity and Relation Prompt

```text
Task: Convert citation records into graph entities and relations.

Use only evidence from the citation records and target paper summary.

Input:
<paper_summary>
{{paper_summary_json}}
</paper_summary>

<citations>
{{citations_json}}
</citations>

Return this JSON object:
{
  "entities": [
    {
      "entity_id": "ent-001",
      "name": "entity name",
      "type": "problem/method/component/dataset/metric/task/baseline/tool-resource/theory/result/limitation/future-work",
      "description": "Chinese grounded description",
      "source_citation_ids": ["cit-001"]
    }
  ],
  "relations": [
    {
      "relation_id": "rel-001",
      "source_id": "target-paper",
      "target_id": "ent-001",
      "relation_type": "cites-for/uses-method/uses-dataset/evaluates-with/compares-against/extends/contrasts-with/supports-claim/reveals-limitation/motivates",
      "intent": "one allowed intent label or null",
      "evidence": "Chinese grounded explanation"
    }
  ]
}
```

## Graph Grouping Prompt

```text
Task: Group graph nodes for a center-paper radial citation map.

Default groups:
- problem-background: background, problem, theory
- method-core: core-method, supporting-method, tool-resource
- data-eval: dataset, metric
- baseline-result: baseline, result-evidence
- limits-future: limitation, future-work

Input:
<citation_graph>
{{citation_graph_json}}
</citation_graph>

Return this JSON object:
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
  "visual_notes": "Chinese explanation of what the graph emphasizes"
}
```

## JSON Repair Prompt

Use only after a model response fails JSON parsing.

```text
The previous response was not valid JSON. Repair it without adding new facts.

Rules:
1. Return valid JSON only.
2. Preserve all factual fields from the previous response when possible.
3. Remove Markdown fences, comments, trailing commas, and explanatory prose.
4. Do not invent new citations, references, entities, or labels.

Invalid response:
{{invalid_response}}
```

## Quality Review Prompt

```text
Task: Review the citation graph for schema and grounding problems.

Check:
1. Every citation has intent, evidence, confidence, and either reference_id or unmatched_reference=true.
2. Every intent is in the allowed label list.
3. Every entity is supported by at least one citation.
4. No bibliographic facts are invented when references are missing.
5. No API keys, private absolute paths, or provider metadata appear.
6. The graph contains enough visual_groups and show_on_map cues to render citation_map.svg or a deterministic SVG-ready fallback.

Return this JSON object:
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "suggested_repairs": []
}
```
