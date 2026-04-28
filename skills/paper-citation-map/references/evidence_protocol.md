# Evidence Protocol for Citation Intent Analysis

Use this protocol before writing `analysis.md` and before finalizing `citation_graph.json`. The goal is to make every important citation traceable, interpretable, and useful for understanding the target paper.

## Evidence Sources

Use only information available in the supplied PDF text, extracted paper text, citation contexts, reference list, or user-provided notes. Do not fill gaps with domain knowledge, memory, or plausible bibliography guesses.

For each key citation, capture as many of these evidence anchors as possible:

| Anchor | Meaning |
| --- | --- |
| `citation_context` | The local sentence or short paragraph where the citation appears. Keep it concise. |
| `section` | The target paper section or nearby heading, if visible. |
| `target_claim` | The target-paper claim, method choice, dataset choice, or result that the citation supports. |
| `cited_work_role` | The role of the cited work, such as problem origin, method component, dataset source, baseline, tool, theory, result evidence, or limitation. |
| `intent_rationale` | The intent rationale: why this citation belongs to its selected intent label instead of a nearby label. |
| `confidence_reason` | Why the confidence is high, medium, or low. |

## Citation Context Rules

- Prefer citation sentences and adjacent context over abstract-level summaries.
- If a citation appears only in a table or noisy PDF extraction, mark the noise in `notes` and lower confidence when needed.
- If the cited title or reference entry cannot be matched reliably, use `unmatched_reference: true` and explain the uncertainty.
- Do not copy long source passages into `analysis.md`; summarize evidence and keep short anchors.

## Intent Rationale Rules

Each important citation should answer these questions:

1. What target-paper idea does this citation support?
2. What is the cited work's role in that idea?
3. Why is the chosen `intent` more appropriate than similar labels?
4. How strongly does the visible evidence support the judgment?

Examples:

- `core-method`: the cited work directly supplies or motivates a main method component used by the target paper.
- `supporting-method`: the cited work supports an auxiliary technique, implementation choice, or background mechanism.
- `dataset`: the cited work introduces or defines a dataset used in evaluation.
- `baseline`: the cited work is used as a comparison system, not merely as related work.
- `result-evidence`: the cited work or external model result is used to interpret target-paper performance.

## Confidence Policy

Use `confidence` consistently:

| Level | Range | Use when |
| --- | ---: | --- |
| high | `0.80-1.00` | Citation sentence, reference match, and target claim are all clear. |
| medium | `0.55-0.79` | Intent is likely but section context, reference match, or cited-work role is incomplete. |
| low | `0.10-0.54` | Evidence is noisy, table-derived, ambiguous, or weakly connected to the target claim. |

Do not use high confidence when only the reference title is known but the citation context is missing.

## No-Evidence Handling

If an expected intent, method chain, dataset link, or baseline link has no reliable evidence, write `未发现可靠证据`. Do not invent a citation to fill a template row.

When generating `analysis.md`, explicitly distinguish:

- evidence-backed conclusions,
- plausible but uncertain interpretations,
- missing or noisy evidence.

When generating `citation_graph.json`, preserve uncertainty in `notes`, `intent_rationale`, or `confidence_reason` instead of hiding it.
