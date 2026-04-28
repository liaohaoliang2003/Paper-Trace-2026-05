# Citation Graph Schema

This file defines the canonical `citation_graph.json` structure for the `paper-citation-map` skill, future CLI, and future visualization tools.

`citation_graph.json` is the minimum required artifact for this skill. When the workspace is writable, save it even if `citation_map.svg` cannot be generated. The graph should contain enough `visual_groups`, citation `intent`, `evidence`, and optional `show_on_map` hints for a renderer or future agent to produce the SVG later.

## Top-Level Object

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

Required fields:

| Field | Type | Description |
| --- | --- | --- |
| `paper_id` | string | Stable ID, usually `target-paper` |
| `title` | string | Target paper title; use `unknown` if unavailable |
| `authors` | array[string] | Authors when available |
| `year` | string or number | Publication year when available |
| `abstract` | string | Abstract or concise summary |
| `core_contributions` | array[string] | Main contributions grounded in paper text |

## `references[]`

Required fields:

| Field | Type | Description |
| --- | --- | --- |
| `reference_id` | string | Stable ID, e.g. `ref-001` |
| `marker` | string | In-text marker, e.g. `[1]` or `Smith et al., 2020` |
| `title` | string | Reference title; use `unknown` if not recoverable |
| `authors` | array[string] | Reference authors when available |
| `year` | string or number | Reference year when available |
| `raw_reference` | string | Original bibliography entry or best available text |

Optional fields: `venue`, `doi`, `url`, `notes`.

## `citations[]`

Required fields:

| Field | Type | Description |
| --- | --- | --- |
| `citation_id` | string | Stable ID, e.g. `cit-001` |
| `reference_id` | string or null | Matched reference ID; null only if unmatched |
| `unmatched_reference` | boolean | True when marker cannot be matched to a reference |
| `marker` | string | Citation marker in the text |
| `section` | string | Section where citation appears |
| `citation_sentence` | string | Sentence containing the citation |
| `context` | string | Citation sentence plus local neighboring evidence |
| `intent` | string | One allowed intent label |
| `confidence` | number | 0.0 to 1.0 confidence |
| `evidence` | string | Short grounded explanation in Chinese |

Optional fields:

- `secondary_intents`: array of allowed intent labels.
- `entity_ids`: linked entity IDs.
- `coarse_intent`: one of `background`, `method`, `result`.
- `notes`: uncertainty or extraction notes.
- `show_on_map`: boolean; set `true` for citations that should appear in `citation_map.svg`, especially `core-method`, `dataset`, `metric`, and `baseline` citations.

Validation rule: every citation must include `intent`, `evidence`, and either a non-empty `reference_id` or `unmatched_reference: true`. Do not emit a citation that lacks both reference linkage and an explicit unmatched status.

Allowed `intent` values:

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

Required fields:

| Field | Type | Description |
| --- | --- | --- |
| `entity_id` | string | Stable ID, e.g. `ent-001` |
| `name` | string | Entity surface name |
| `type` | string | Entity type |
| `description` | string | Chinese description grounded in text |
| `source_citation_ids` | array[string] | Supporting citation IDs |

Allowed `type` values:

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

Required fields:

| Field | Type | Description |
| --- | --- | --- |
| `relation_id` | string | Stable ID, e.g. `rel-001` |
| `source_id` | string | Paper, citation, reference, or entity ID |
| `target_id` | string | Paper, citation, reference, or entity ID |
| `relation_type` | string | Relationship category |
| `intent` | string or null | Citation intent when relation is citation-related |
| `evidence` | string | Grounded explanation |

Recommended `relation_type` values:

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

Required fields:

| Field | Type | Description |
| --- | --- | --- |
| `group_id` | string | Stable group ID |
| `label` | string | Chinese display label |
| `intent_filters` | array[string] | Intents included in this group |
| `node_ids` | array[string] | Citation/entity/reference IDs shown in this group |
| `color` | string | Hex color for the group |

Default groups:

| `group_id` | Label | Intents |
| --- | --- | --- |
| `problem-background` | 问题背景 | `background`, `problem`, `theory` |
| `method-core` | 核心方法 | `core-method`, `supporting-method`, `tool-resource` |
| `data-eval` | 数据与评估 | `dataset`, `metric` |
| `baseline-result` | 基线与结果 | `baseline`, `result-evidence` |
| `limits-future` | 局限与未来 | `limitation`, `future-work` |

## `metadata`

Recommended fields:

| Field | Type | Description |
| --- | --- | --- |
| `source_file` | string | Relative input filename only; avoid private absolute paths |
| `created_at` | string | ISO-like timestamp if available |
| `extraction_method` | string | `manual`, `llm`, `cli`, or `hybrid` |
| `coverage_notes` | string | Missing sections, noisy PDF text, or reference matching caveats |

## Minimal Example

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
    "coverage_notes": "Minimal schema example only."
  }
}
```
