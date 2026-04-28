# Visual Citation Map Modes

The Skill supports three declared visual modes. Only two static SVG modes are implemented now.

## Mode Decision

| User request | Output behavior |
| --- | --- |
| `current`, `current mode`, `original SVG`, `原 SVG`, `当前模式` | Generate only current mode as `citation_map.svg` |
| `example`, `reference image`, `mind map`, `例图`, `参考图`, `思维导图` | Generate only example mode as `citation_map.svg` |
| `hybrid`, `expandable knowledge graph`, `混合`, `可展开知识图谱` | Explain that hybrid is reserved for future interactive Web graph rendering; do not output fixed SVG |
| No explicit mode and asking is possible | Ask which mode the user wants |
| No explicit mode and asking is not possible | Generate both current and example |

File convention:

- `visual_mode=current`: `citation_map.svg` and `citation_map.html`.
- `visual_mode=example`: `citation_map.svg` and `citation_map.html`; SVG content is the example layout.
- `visual_mode=all`: `citation_map.svg` for current mode, `citation_map_example.svg` for example mode, and `citation_map.html` containing both.
- `visual_mode=hybrid`: no static SVG. Record the limitation in `analysis.md` if relevant.

## Current Mode: Grouped Radial SVG

Keep the existing layout unchanged when the user selects current mode.

- Target paper stays in the center.
- Citation intent groups are arranged around the target paper.
- Group hubs use stable colors and deterministic positions.
- Group nodes show high-priority citations first.
- `show_on_map=false` citations are omitted from SVG but retained in JSON.
- Dense groups render 3 to 5 high-priority nodes and summarize overflow as `+N citations`.

Recommended group positions:

| Group | Position | Intents |
| --- | --- | --- |
| Problem/background | Upper left | `background`, `problem` |
| Core/supporting methods | Upper right | `core-method`, `supporting-method`, `theory` |
| Data/evaluation | Right or middle | `dataset`, `metric` |
| Baselines/results | Lower left | `baseline`, `result-evidence` |
| Limits/resources/future | Bottom or far left | `limitation`, `tool-resource`, `future-work` |

## Example Mode: Reference-Image Mind Map

Use this mode to imitate the user's reference image: a right-side target paper with left-side layered citation chains.

Canvas recommendation: `1400 x 1000`.

Required structure:

- Target paper node on the right side, vertically centered.
- Left-side first-level chain hubs:
  - `问题链`: `background`, `problem`
  - `方法链`: `core-method`, `supporting-method`, `theory`
  - `数据链`: `dataset`, `metric`
  - `基线链`: `baseline`, `result-evidence`
  - `局限/资源链`: `limitation`, `tool-resource`, `future-work`
- Main edge labels in Chinese: `问题`, `方法`, `数据集`, `基线`, `局限`.
- Second-level nodes show method components, datasets, baselines, or key author-year references.
- Dashed cross-links can show secondary roles, for example a method that is both a baseline and a method reference.
- If a chain has too many citations, render up to 5 key nodes and add a `+N citations` summary.

Node text priority:

1. `target_claim`
2. `cited_work_role`
3. Shortened `evidence`
4. Shortened `citation_sentence`
5. Reference label from `reference_id`

## Shared Color Palette

| Intent group | Color |
| --- | --- |
| Problem/background | `#cf6f6f` |
| Core/supporting methods | `#ef6c2f` |
| Data/metrics | `#8a5cf6` |
| Baselines/results | `#d18a19` |
| Limits/resources/future | `#4f9c56` |
| Unmatched/uncertain | `#9aa3ad` |

## SVG Requirements

- Include a visible target paper node labeled with the paper title or short title.
- Include an explicit legend explaining color-to-intent mapping.
- Use deterministic layout; do not use random force-directed placement.
- Use text labels in addition to color; do not rely on color alone.
- Keep main labels at least `16px` and secondary labels at least `12px`.
- Avoid long verbatim citation sentences in nodes; use short evidence labels.

## Hybrid Mode Reservation

Hybrid means an expandable, interactive knowledge graph that can reveal details on demand. It is not a fixed SVG mode yet. When requested now:

- Do not generate a fake static hybrid SVG.
- Explain that the mode is reserved for future Web integration.
- Still provide `citation_graph.json`, because it is the data source for the future hybrid graph.
