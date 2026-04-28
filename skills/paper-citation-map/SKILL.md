---
name: paper-citation-map
description: Use when a user provides an academic paper PDF, extracted paper text, citation contexts, or references and asks for citation intent extraction, entity/relation extraction, paper contribution mapping, or a visual citation graph.
---

# Paper Citation Map

## Overview

Use this skill to turn one academic paper into a grounded citation-intent map: a Chinese analysis, a machine-readable `citation_graph.json`, and a center-paper radial SVG. It follows this repository's two existing lines of work: `CitePrompt` for citation intent taxonomy and `sci_glm` for LLM-first structured JSON extraction.

## Inputs

Accept one of these input forms:

- A single paper PDF path or attachment.
- Extracted full text from one paper.
- Citation contexts plus a reference list.
- A partial analysis that needs normalization into the graph schema.

If the PDF text is noisy, ask for extracted text or operate only on reliable sections. Do not invent missing references, titles, or citation contexts.

## Required Outputs

Default to saving artifacts whenever the current workspace is writable. Do not stop at a chat-only summary unless file writing is unavailable.

- `analysis.md`: Required Chinese reading-oriented report with target paper summary, citation-intent findings, entity/relation notes, graph interpretation, coverage limits, and uncertainty notes.
- `citation_graph.json`: Required structured graph data following `references/schema.md`. This is the minimum file artifact and must exist even when SVG rendering fails.
- `citation_map.svg`: Preferred center-paper radial visualization following `references/visual.md`. If reliable SVG generation is not possible, still write `citation_graph.json` and explain the gap in `analysis.md`.
- `citation_map_spec.md`: Optional fallback only when SVG cannot be generated; include SVG-ready layout instructions and the reason SVG was not written.

Default output directory priority:

1. Use the user-specified output directory when provided.
2. Otherwise use `outputs/paper-citation-map/<safe-paper-stem>/` inside the current workspace.
3. If that path is not writable but the source file directory is writable, use `<safe-paper-stem>-citation-map/` beside the source file.
4. If no writable location is available, state this explicitly in the final response and inline the Markdown, JSON, and SVG-ready content.

## Structured Analysis Template Mode

Use the fixed `analysis.md` template only when the user explicitly asks for a template or compliance format, for example: `使用模板`, `按模板`, `符合规范`, `标准格式`, `固定结构`, `规范化报告`, `template`, or `standard format`.

- When template mode is triggered, read `references/analysis_template.md` and write `analysis.md` with the exact section order and required tables from that file.
- When template mode is not triggered, do not force the fixed template; still include the required content areas listed above.
- Never fill template rows with invented citations. If an intent has no reliable evidence, say so in the relevant section.

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

Map these to coarse CitePrompt-style classes when useful:

- `background`: `background`, `problem`, `theory`, `future-work`
- `method`: `core-method`, `supporting-method`, `tool-resource`
- `result`: `dataset`, `metric`, `baseline`, `result-evidence`, `limitation`

## Workflow

1. **Extract reliable paper text**
   - Identify title, authors, abstract, sections, references, and citation markers.
   - Keep citation marker style unchanged, such as `[12]`, `(Smith et al., 2020)`, or `Smith et al. [7]`.

2. **Locate citation contexts**
   - Extract the sentence containing each citation and one neighboring sentence on each side when available.
   - Preserve section name and citation marker.
   - If one sentence cites multiple references, create one citation record per matched reference while sharing the same context.

3. **Match references**
   - Link citation markers to reference entries.
   - If matching is uncertain, set `unmatched_reference: true` and explain the uncertainty in `evidence`.

4. **Extract entities and relations**
   - Extract methods, datasets, metrics, tasks, problems, components, results, and resources.
   - Link entities to citation records only when supported by evidence text.

5. **Classify citation intent**
   - Use the intent labels above.
   - Prefer specific labels over broad labels: choose `dataset` instead of `background` when a cited work supplies a dataset.
   - For ambiguous cases, include `confidence < 0.7` and explain the ambiguity.

6. **Build graph groups**
   - Group nodes by semantic role: problem/background, method, data/evaluation, baseline/result, limitation/future.
   - Mark `core-method`, `dataset`, `metric`, and `baseline` as graph-priority intents.

7. **Generate outputs**
   - Create the output directory using the default priority above.
   - Write `analysis.md` with concise Chinese explanations and evidence anchors; if template mode is triggered, follow `references/analysis_template.md`.
   - Write `citation_graph.json` according to `references/schema.md`; do not omit this file.
   - Render `citation_map.svg` using `references/visual.md` whenever possible.
   - If SVG cannot be generated, write `citation_map_spec.md` and describe the SVG limitation in `analysis.md`.

## LLM Extraction Rules

Read `references/prompts.md` before writing extraction prompts or calling an LLM.

Hard rules:

- Request JSON only; no Markdown code fences in model output.
- Validate JSON with a parser; never use unsafe code evaluation.
- Reject labels outside the allowed intent list.
- Do not expose API keys, model-private traces, or provider-specific raw metadata in final artifacts.
- Keep all claims grounded in citation context, abstract, section text, or reference entries.

## Quality Checks

Before finalizing, verify:

- Every `citation` has `intent`, `evidence`, and either `reference_id` or `unmatched_reference: true`.
- Every `intent` belongs to the allowed taxonomy.
- Every high-priority visual node has at least one evidence sentence.
- The graph can be understood without reading the full paper.
- `analysis.md` and `citation_graph.json` are saved when a writable location exists.
- `citation_map.svg` is saved when SVG rendering is available, or `citation_map_spec.md` documents the fallback.
- The output does not include hardcoded API keys, private absolute paths, or invented bibliographic metadata.

## Common Failure Handling

- **PDF extraction is broken**: ask for extracted text or analyze only reliable text spans; mark coverage limits in `analysis.md`.
- **References cannot be matched**: keep citation marker and context, set `unmatched_reference: true`, and avoid guessing titles.
- **Citation has multiple intents**: choose the primary intent and place secondary intents in `secondary_intents`.
- **LLM returns invalid JSON**: retry with the repair prompt from `references/prompts.md`; never parse with unsafe code evaluation.
- **Graph is too crowded**: keep all records in JSON but visualize only priority citations and summarize the rest by group.
- **Filesystem is not writable**: do not silently skip artifacts; explain the write failure and inline `analysis.md`, `citation_graph.json`, and SVG-ready layout content in the response.

## Reference Files

- `references/schema.md`: canonical `citation_graph.json` schema and minimal example.
- `references/prompts.md`: LLM prompts for extraction, classification, repair, and quality review.
- `references/visual.md`: radial SVG layout rules, color palette, edge types, and SVG-ready structure.
- `references/analysis_template.md`: fixed `analysis.md` template for explicit template/compliance requests.
