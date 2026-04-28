# Radial Citation Map Visual Reference

The default visualization is a center-paper radial SVG: the target paper is the main node, semantic groups sit around it, and citation/reference/entity nodes branch outward. Save this visualization as `citation_map.svg` whenever SVG generation is available. If SVG cannot be generated, save `citation_map_spec.md` with the same layout decisions and keep `citation_graph.json` complete.

## Visual Thesis

Show how the target paper builds its contribution from cited problems, methods, datasets, metrics, baselines, and evidence. The graph should be readable as a visual abstract, not a dense bibliography network.

## Layout

Canvas defaults:

| Property | Default |
| --- | --- |
| Width | `1400` |
| Height | `1000` |
| Center node | Right-center at `(980, 500)` |
| Left-side groups | Problem, method, evaluation, baseline/result |
| Bottom group | Limitations/future if present |

Recommended group placement:

| Group | Position | Purpose |
| --- | --- | --- |
| 问题背景 | upper-left | Background, problem, theory citations |
| 核心方法 | middle-left | Core and supporting method citations |
| 数据与评估 | upper/middle | Dataset and metric citations |
| 基线与结果 | lower-left | Baselines and result evidence |
| 局限与未来 | lower or far-left | Limitations and future work |

If there are more than 25 citation nodes, visualize only graph-priority nodes and summarize the rest as small count badges.

## Node Types

| Node | Shape | Style |
| --- | --- | --- |
| Target paper | large rounded rectangle | light blue-gray fill, dark text |
| Group hub | rounded rectangle | white fill, colored stroke |
| Entity | small rounded rectangle | light fill matching group color |
| Reference | text label or pill | gray text, optional short author-year |
| Evidence note | small side text | muted gray |

## Edge Types

| Relation | Edge style |
| --- | --- |
| Direct citation intent | solid curved line from target paper to group hub |
| Entity derived from citation | solid or short curved line from group hub to entity |
| Indirect support or secondary intent | dashed curved line |
| Uncertain match | dotted curved line with low opacity |

Use arrowheads sparingly. The main reading direction is from target paper outward to cited concepts.

## Intent Colors

| Intent group | Color |
| --- | --- |
| Problem/background | `#cf6f6f` |
| Core/supporting method | `#ef6c2f` |
| Dataset/metric | `#8a5cf6` |
| Baseline/result | `#d18a19` |
| Limitation/future | `#4f9c56` |
| Unmatched/uncertain | `#9aa3ad` |

## SVG Structure

Use this high-level SVG order:

```xml
<svg width="1400" height="1000" viewBox="0 0 1400 1000" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- gradients, shadows, arrowheads -->
  </defs>
  <rect width="1400" height="1000" fill="#fbfbfa"/>
  <g id="edges">
    <!-- curved paths first, so nodes sit above edges -->
  </g>
  <g id="groups">
    <!-- group hubs and grouped nodes -->
  </g>
  <g id="target-paper">
    <!-- center target paper node -->
  </g>
  <g id="legend">
    <!-- intent color legend -->
  </g>
</svg>
```

Minimum SVG content:

- One visible target-paper node labeled with the paper title.
- At least one group hub derived from `visual_groups`.
- At least one citation/entity/reference node for each populated priority group when data exists.
- Curved edges from the target paper to group hubs and from group hubs to displayed nodes.
- A legend mapping colors to intent groups.
- Short evidence labels or node subtitles grounded in `citation_graph.json`.

## Labeling Rules

- Target paper label: title, shortened if longer than 60 characters.
- Group hub label: Chinese semantic label, such as `核心方法`.
- Reference label: prefer `Short Title (Author, Year)`; use `unknown reference [marker]` when unmatched.
- Edge label: use short Chinese intent names, such as `核心方法`, `数据集`, `评价指标`.
- Evidence labels should be short fragments, not full sentences.

## Rendering Strategy

For the first CLI renderer, use deterministic SVG generation:

1. Sort groups by default order.
2. Sort nodes inside each group by priority: `core-method`, `dataset`, `metric`, `baseline`, then confidence descending.
3. Place group hubs on fixed anchor coordinates.
4. Place nodes in vertical stacks around each hub.
5. Draw cubic Bezier curves from target paper to hubs and from hubs to nodes.

Avoid force-directed random layouts in V1 because they are harder to reproduce and test.

## Graph Simplification

When graph density is high:

- Keep all records in `citation_graph.json`.
- Render top 3 to 5 nodes per visual group.
- Add a group badge such as `+12 background citations`.
- Prefer concept/entity nodes over raw reference nodes when multiple citations support the same concept.

## Accessibility

- Maintain contrast between text and background.
- Use color plus text labels; do not rely on color alone.
- Include a legend mapping colors to intent groups.
- Keep font size at least `16px` for primary labels and `13px` for secondary labels.
