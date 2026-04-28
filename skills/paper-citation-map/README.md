# paper-citation-map Skill

## Purpose

`paper-citation-map` is the project-local English Skill for turning one academic paper into a citation-intent map. It guides an agent from paper PDF or extracted text to three standard artifacts: `analysis.md`, `citation_graph.json`, and a radial `citation_map.svg` specification.

## When To Use

Use this Skill when the user provides a paper PDF, paper text, citation contexts, or a reference list and asks for:

- citation intent extraction;
- entity and relation extraction;
- paper contribution mapping;
- a visual citation graph similar to a center-paper radial map.

## File Structure

```text
skills/paper-citation-map/
├── SKILL.md
├── README.md
└── references/
    ├── analysis_template.md
    ├── prompts.md
    ├── schema.md
    └── visual.md
```

| File | Role |
| --- | --- |
| `SKILL.md` | Main Skill entry: triggers, workflow, labels, quality checks, and failure handling |
| `references/analysis_template.md` | Fixed `analysis.md` template for explicit template/compliance requests |
| `references/schema.md` | Canonical `citation_graph.json` schema and minimal valid example |
| `references/prompts.md` | LLM extraction, relation extraction, grouping, JSON repair, and quality-review prompts |
| `references/visual.md` | SVG radial graph layout, color, node, edge, and accessibility rules |

## Standard Outputs

| Output | Description |
| --- | --- |
| `analysis.md` | Chinese reading report with paper summary, citation-intent findings, and graph interpretation |
| `citation_graph.json` | Machine-readable graph data shared by Skill, future CLI, and future Web tools |
| `citation_map.svg` | Center-paper radial citation graph or an SVG-ready layout specification |

## Analysis Template Mode

The default report may use a flexible structure as long as it covers the required content. Use the fixed `references/analysis_template.md` structure only when the user explicitly asks for a template or compliance format, such as `使用模板`, `按模板`, `符合规范`, `标准格式`, `固定结构`, `规范化报告`, `template`, or `standard format`.

Template mode still requires `citation_graph.json` and should still produce `citation_map.svg` whenever possible. Do not invent citations to fill template rows; write `未发现可靠证据` when evidence is absent.

## Relation To Existing Work

- `CitePrompt`: provides the citation-intent classification background and the coarse `background` / `method` / `result` mapping.
- `sci_glm`: provides the LLM-first pattern of constrained prompts, JSON-only output, citation ID alignment, and safe parsing requirements.

## Validation Checklist

- `SKILL.md` has valid frontmatter with `name` and `description`.
- The 12 allowed intent labels are present and unchanged.
- The schema example in `references/schema.md` parses with `json.loads()`.
- Every citation example includes `intent`, `evidence`, and either `reference_id` or `unmatched_reference`.
- No API keys, private absolute paths, or unfinished placeholder markers are present.
- Template mode pressure scenarios pass: explicit template requests follow `analysis_template.md`, while ordinary analysis requests are not over-constrained.

## Future Extensions

The next engineering step is a CLI that reads paper PDF/text, calls an LLM or local extractor, validates `citation_graph.json`, and renders SVG/HTML. Web tooling is intentionally deferred until the schema and CLI outputs are stable.
