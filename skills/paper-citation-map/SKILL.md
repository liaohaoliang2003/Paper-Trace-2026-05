---
name: paper-citation-map
description: Use when a user provides an academic paper PDF, extracted paper text, citation contexts, or references and asks for citation intent extraction, entity/relation extraction, paper contribution mapping, or a visual citation graph.
---

# Paper Citation Map

## Overview

Use this skill to turn one academic paper into a grounded citation-intent map: a Chinese `analysis.md`, a machine-readable `citation_graph.json`, and one or more SVG citation maps. Do not stop at a chat-only summary when a writable workspace is available.

## Required Outputs

Default output directory priority:

1. User-specified output directory.
2. `outputs/paper-citation-map/<safe-paper-stem>/` in the current workspace.
3. `<safe-paper-stem>-citation-map/` beside the source file if the workspace path is not writable.
4. If no filesystem target is writable, explain that in the final response and inline Markdown/JSON/SVG-ready content.

Standard artifacts:

- `analysis.md`: Required Chinese report covering the target paper, citation-intent groups, evidence chains, entity/relation interpretation, coverage limits, and uncertainty.
- `citation_graph.json`: Required structured graph following `references/schema.md`. This is the minimum artifact and must exist even if SVG generation fails.
- `citation_map.svg`: Required when SVG generation is possible. The content depends on the selected visual mode.
- `citation_map_example.svg`: Required only when visual mode is `all`.
- `citation_map_spec.md`: Optional fallback when SVG cannot be generated; include render-ready layout notes and the reason SVG was not written.

## Visual Mode Selection

Before generating SVG, infer whether the user explicitly requested a mode:

- Current mode only: phrases such as `current`, `current mode`, `original SVG`, `original layout`, `当前模式`, `原 SVG`, `原编排`.
- Example mode only: phrases such as `example`, `reference image`, `mind map`, `参考图`, `例图`, `思维导图`.
- Hybrid mode: phrases such as `hybrid`, `expandable knowledge graph`, `混合`, `可展开知识图谱`. This mode is reserved for future interactive Web rendering; do not output a fixed SVG for it.
- If no explicit mode is requested and you can ask the user, ask which mode to use.
- If no explicit mode is requested and asking is not possible, generate both `current` and `example`.

Output naming:

- `current`: write `citation_map.svg` using the existing grouped radial layout.
- `example`: write `citation_map.svg` using the reference-image mind-map layout.
- `all`: write `citation_map.svg` for current mode and `citation_map_example.svg` for example mode.
- `hybrid`: explain that it is reserved and do not invent a static SVG.

Read `references/visual.md` before drawing SVG.

## Structured Analysis Template Mode

Use the fixed `analysis.md` template only when the user explicitly asks for a template or compliance format, for example: `使用模板`, `按模板`, `符合规范`, `标准格式`, `固定结构`, `规范化报告`, `template`, or `standard format`.

- When triggered, read `references/analysis_template.md` and write `analysis.md` with the exact section order and required tables.
- When not triggered, do not force the fixed template; still include the required content areas.
- Never fill template rows with invented citations. If an intent has no reliable evidence, write `未发现可靠证据`.

## Citation Intent Labels

Use only these labels unless the user explicitly extends the taxonomy:

| Intent | Use when the citation supports |
| --- | --- |
| `background` | Related work, general context, motivation, or domain facts |
| `problem` | Problem definition, challenge, bottleneck, or known limitation |
| `core-method` | A key method or idea that directly forms the target paper's method |
| `supporting-method` | Auxiliary method, component, algorithm, or implementation technique |
| `dataset` | Dataset, corpus, benchmark, testbed, or data source |
| `metric` | Evaluation metric, scoring method, protocol, or measurement setup |
| `baseline` | Compared method, prior system, SOTA result, or ablation reference |
| `tool-resource` | Library, toolkit, pretrained model, annotation tool, or external resource |
| `theory` | Theoretical definition, formula, framework, or formal analysis |
| `result-evidence` | Empirical result, observed phenomenon, evidence, or conclusion |
| `limitation` | Failure case, weakness, caveat, or negative evidence |
| `future-work` | Open question, future direction, or unresolved opportunity |

## Workflow

1. Extract reliable paper text: title, authors, abstract, sections, references, and citation markers.
2. Locate citation contexts: citation sentence plus neighboring sentences when available.
3. Build evidence chains using `references/evidence_protocol.md`: citation context, section, target claim, cited-work role, intent rationale, confidence reason, and uncertainty.
4. Classify each citation intent with one of the 12 labels.
5. Extract entities and relations that help explain the target paper.
6. Write `citation_graph.json` using `references/schema.md`; keep optional depth fields such as `section`, `target_claim`, `cited_work_role`, `intent_rationale`, and `confidence_reason` when useful.
7. Write `analysis.md`; use template mode only when explicitly triggered.
8. Generate SVG according to the selected visual mode and `references/visual.md`.
9. Validate artifacts before the final reply.

## Reference Files

- `references/evidence_protocol.md`: evidence-chain requirements and uncertainty rules.
- `references/schema.md`: required JSON schema and optional depth fields.
- `references/prompts.md`: extraction/review prompts for LLM-assisted workflows.
- `references/visual.md`: current, example, and reserved hybrid visual rules.
- `references/analysis_template.md`: fixed report template for explicit template mode.

## Quality Checks

- Every citation has `intent`, `evidence`, `confidence`, and either `reference_id` or `unmatched_reference: true`.
- Key citations trace back to a citation sentence or context; if not, lower confidence and mark uncertainty.
- Do not use domain knowledge to fabricate missing citation evidence.
- Keep `citation_graph.json` complete even when Markdown summarizes.
- If SVG fails, still write `citation_graph.json` and document the gap in `analysis.md`.
