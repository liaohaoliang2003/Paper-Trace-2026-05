from __future__ import annotations

import html
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from .schema import DEFAULT_VISUAL_GROUPS


GROUP_ANCHORS = {
    "problem-background": (360, 170),
    "method-core": (350, 390),
    "data-eval": (390, 600),
    "baseline-result": (410, 780),
    "limits-future": (650, 850),
}

TARGET = (980, 500)
PRIORITY = {"core-method": 0, "dataset": 1, "metric": 2, "baseline": 3, "problem": 4, "result-evidence": 5}
VISUAL_MODES = {"current", "example", "all"}
CURRENT_NODE_WIDTH = 360
CURRENT_NODE_HEIGHT = 52
CURRENT_NODE_GAP_Y = 18
CURRENT_GROUP_GAP = 64

EXAMPLE_CHAINS = [
    {
        "chain_id": "problem-chain",
        "label": "问题链",
        "edge_label": "问题",
        "intents": ["background", "problem"],
        "color": "#cf6f6f",
        "hub": (560, 110),
        "node_x": 245,
    },
    {
        "chain_id": "method-chain",
        "label": "方法链",
        "edge_label": "方法",
        "intents": ["core-method", "supporting-method", "theory"],
        "color": "#ef6c2f",
        "hub": (540, 330),
        "node_x": 215,
    },
    {
        "chain_id": "data-chain",
        "label": "数据链",
        "edge_label": "数据集",
        "intents": ["dataset", "metric"],
        "color": "#8a5cf6",
        "hub": (570, 530),
        "node_x": 250,
    },
    {
        "chain_id": "baseline-chain",
        "label": "基线链",
        "edge_label": "基线",
        "intents": ["baseline", "result-evidence"],
        "color": "#d18a19",
        "hub": (560, 720),
        "node_x": 225,
    },
    {
        "chain_id": "limits-chain",
        "label": "局限/资源链",
        "edge_label": "局限",
        "intents": ["limitation", "tool-resource", "future-work"],
        "color": "#4f9c56",
        "hub": (625, 880),
        "node_x": 300,
    },
]

EXAMPLE_CANVAS_WIDTH = 2400
EXAMPLE_NODE_WIDTH = 460
EXAMPLE_NODE_HEIGHT = 82
EXAMPLE_NODE_GAP_Y = 28
EXAMPLE_COLUMN_GAP = 44
EXAMPLE_MAX_ROWS_PER_COLUMN = 7
EXAMPLE_LANE_GAP = 54
EXAMPLE_TOP = 132


def validate_visual_mode(visual_mode: str) -> str:
    if visual_mode == "hybrid":
        raise ValueError("hybrid visual mode is reserved for future interactive Web graph rendering and is not implemented yet")
    if visual_mode not in VISUAL_MODES:
        raise ValueError(f"unsupported visual mode: {visual_mode}")
    return visual_mode


def render_svg(graph: Dict[str, Any], visual_mode: str = "current") -> str:
    """Render one SVG. `all` resolves to the compatibility/current SVG."""
    visual_mode = validate_visual_mode(visual_mode)
    if visual_mode == "example":
        return render_example_svg(graph)
    return render_current_svg(graph)


def render_current_svg(graph: Dict[str, Any]) -> str:
    paper = graph.get("paper", {})
    title = paper.get("title", "Target Paper")
    groups = _groups_with_defaults(graph)
    citations = graph.get("citations", [])
    edges: List[str] = []
    nodes: List[str] = []
    layouts = []
    cursor_y = 150

    for group in groups:
        group_id = group["group_id"]
        visible = _visible_citations_for_group(citations, group)
        height = max(150, 84 + len(visible) * (CURRENT_NODE_HEIGHT + CURRENT_NODE_GAP_Y))
        layouts.append({"group": group, "visible": visible, "y": cursor_y, "height": height})
        cursor_y += height + CURRENT_GROUP_GAP

    canvas_height = max(1000, cursor_y + 90)
    target_x, target_y = 980, canvas_height // 2
    for layout in layouts:
        group = layout["group"]
        group_id = group["group_id"]
        color = group.get("color", "#9aa3ad")
        visible = layout["visible"]
        group_y = int(layout["y"] + layout["height"] / 2)
        x = 360 if group_id != "limits-future" else 610
        edges.append(_curve(target_x - 120, target_y, x + 130, group_y, color, group.get("label", group_id)))
        nodes.append(_lane_background(70, layout["y"], 680, layout["height"], color, group_id))
        nodes.append(_rounded_node(x, group_y, 230, 50, group.get("label", group_id), color, "#ffffff", group_id))
        for offset, citation in enumerate(visible):
            node_y = layout["y"] + 46 + offset * (CURRENT_NODE_HEIGHT + CURRENT_NODE_GAP_Y)
            node_x = x - 90
            label = _shorten(citation.get("citation_sentence", citation["citation_id"]), 48)
            nodes.append(_current_citation_node(node_x, node_y, label, color, citation["citation_id"]))
            edges.append(_curve(x + 35, group_y + 50, node_x + CURRENT_NODE_WIDTH, node_y + CURRENT_NODE_HEIGHT / 2, color, "", dashed=False, opacity="0.45"))

    legend = _legend(groups)
    title_lines = _svg_text_lines(title, 34, max_lines=3)
    title_text = _multiline_text(target_x, target_y - 16, title_lines, 22, "#243447", 20, "700", anchor="middle")
    return f'''<svg id="citation-map" width="1400" height="{canvas_height}" viewBox="0 0 1400 {canvas_height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Citation Map">
  <defs>
    <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#8b98a8" flood-opacity="0.18"/></filter>
  </defs>
  <rect width="1400" height="{canvas_height}" fill="#fbfbfa"/>
  <text x="60" y="70" fill="#1f2937" font-size="30" font-weight="700">Citation Map</text>
  <text x="60" y="100" fill="#667085" font-size="15">current visual mode · expanded groups preserve visible citation nodes</text>
  <g id="edges">{''.join(edges)}</g>
  <g id="groups">{''.join(nodes)}</g>
  <g id="target-paper" filter="url(#soft-shadow)">
    <rect x="{target_x - 180}" y="{target_y - 70}" width="360" height="140" rx="32" fill="#eaf1f4"/>
    {title_text}
    <text x="{target_x}" y="{target_y + 48}" text-anchor="middle" fill="#667085" font-size="14">target-paper</text>
  </g>
  <g id="legend">{legend}</g>
</svg>'''


def render_example_svg(graph: Dict[str, Any]) -> str:
    paper = graph.get("paper", {})
    title = paper.get("title", "Target Paper")
    citations = [citation for citation in graph.get("citations", []) if citation.get("show_on_map", True)]
    references = {ref.get("reference_id"): ref for ref in graph.get("references", [])}
    edges: List[str] = []
    nodes: List[str] = []
    lane_layouts = []
    cursor_y = EXAMPLE_TOP

    for chain in EXAMPLE_CHAINS:
        visible = _visible_citations_for_intents(citations, chain["intents"])
        columns = _example_column_count(len(visible))
        rows = max(1, _ceil_div(len(visible), columns))
        lane_height = max(190, 72 + rows * (EXAMPLE_NODE_HEIGHT + EXAMPLE_NODE_GAP_Y))
        lane_layouts.append({"chain": chain, "visible": visible, "columns": columns, "rows": rows, "y": cursor_y, "height": lane_height})
        cursor_y += lane_height + EXAMPLE_LANE_GAP

    canvas_height = max(1000, cursor_y + 150)
    target_x, target_y = 2040, canvas_height // 2
    hub_x = 1510
    node_start_x = 120

    for layout in lane_layouts:
        chain = layout["chain"]
        color = chain["color"]
        visible = layout["visible"]
        lane_y = layout["y"]
        lane_height = layout["height"]
        hub_y = int(lane_y + lane_height / 2)
        label_y = lane_y + 30

        nodes.append(_lane_background(56, lane_y, 1740, lane_height, color, chain["chain_id"]))
        nodes.append(_rounded_node(hub_x, hub_y, 260, 58, chain["label"], color, "#ffffff", chain["chain_id"], 17))
        edges.append(_mindmap_curve(target_x - 170, target_y, hub_x + 132, hub_y, color, chain["edge_label"], label_x=hub_x + 245, label_y=hub_y - 18))
        nodes.append(_edge_badge(hub_x + 226, hub_y - 42, chain["edge_label"], color))
        nodes.append(f'<text x="82" y="{label_y}" fill="{color}" font-size="18" font-weight="800">{html.escape(chain["label"])}</text>')

        for offset, citation in enumerate(visible):
            column = offset // layout["rows"]
            row = offset % layout["rows"]
            node_x = node_start_x + column * (EXAMPLE_NODE_WIDTH + EXAMPLE_COLUMN_GAP)
            node_y = lane_y + 58 + row * (EXAMPLE_NODE_HEIGHT + EXAMPLE_NODE_GAP_Y)
            label = _citation_node_label(citation, references)
            sublabel = citation.get("cited_work_role") or citation.get("intent") or citation["citation_id"]
            nodes.append(_mindmap_leaf(node_x, node_y, label, sublabel, color, citation["citation_id"], chain["chain_id"]))
            edges.append(_mindmap_curve(node_x + EXAMPLE_NODE_WIDTH, node_y + EXAMPLE_NODE_HEIGHT / 2, hub_x - 132, hub_y, color, "", opacity="0.38"))

    edges.extend(_cross_links_from_layout(lane_layouts, hub_x))
    legend = _example_legend()
    title_lines = _svg_text_lines(title, 28, max_lines=3)
    target_title = _multiline_text(target_x, target_y - 18, title_lines, 20, "#243447", 22, "700", anchor="middle")
    return f'''<svg id="citation-map-example" width="{EXAMPLE_CANVAS_WIDTH}" height="{canvas_height}" viewBox="0 0 {EXAMPLE_CANVAS_WIDTH} {canvas_height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Example Citation Map">
  <defs>
    <filter id="example-shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#8b98a8" flood-opacity="0.20"/></filter>
  </defs>
  <rect width="{EXAMPLE_CANVAS_WIDTH}" height="{canvas_height}" fill="#fbfbfa"/>
  <text x="60" y="64" fill="#1f2937" font-size="30" font-weight="700">Citation Mind Map</text>
  <text x="60" y="94" fill="#667085" font-size="15">example visual mode · expanded lanes preserve visible citation nodes instead of collapsing them</text>
  <g id="example-edges">{''.join(edges)}</g>
  <g id="example-nodes">{''.join(nodes)}</g>
  <g id="target-paper" filter="url(#example-shadow)">
    <rect x="{target_x - 210}" y="{target_y - 72}" width="420" height="144" rx="34" fill="#eaf1f4"/>
    {target_title}
    <text x="{target_x}" y="{target_y + 48}" text-anchor="middle" fill="#667085" font-size="14">target-paper · 目标论文</text>
  </g>
  <g id="legend">{legend}</g>
</svg>'''


def render_html(graph: Dict[str, Any], svg: str, example_svg: str | None = None, visual_mode: str = "current") -> str:
    title = html.escape(graph.get("paper", {}).get("title", "Citation Map"))
    citations = graph.get("citations", [])
    rows = "".join(
        f"<tr><td>{html.escape(c.get('citation_id',''))}</td><td>{html.escape(c.get('intent',''))}</td><td>{html.escape(c.get('evidence',''))}</td></tr>"
        for c in citations
    )
    maps = _html_map_section("当前分组视图" if example_svg else "Citation Map", svg)
    if example_svg:
        maps += _html_map_section("例图引用链视图", example_svg)
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title} · Citation Map</title>
  <style>
    body {{ margin: 0; font-family: Inter, "Segoe UI", Arial, sans-serif; background: #f6f7f8; color: #172033; }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 28px; }}
    .map {{ background: white; border-radius: 24px; box-shadow: 0 20px 60px rgba(31,41,55,.08); padding: 12px; margin-top: 18px; }}
    .map h2 {{ margin: 10px 12px; color: #243447; }}
    .map-viewport {{ overflow: auto; max-height: 78vh; border-radius: 18px; border: 1px solid #edf0f2; background: #fbfbfa; }}
    .map-viewport svg {{ max-width: none; height: auto; display: block; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 24px; background: white; border-radius: 16px; overflow: hidden; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #edf0f2; text-align: left; vertical-align: top; }}
    th {{ background: #f2f4f7; }}
  </style>
</head>
<body><main>
  <h1>{title}</h1>
  <p>Visual mode: {html.escape(visual_mode)}</p>
  {maps}
  <table><thead><tr><th>ID</th><th>Intent</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table>
</main></body></html>'''


def render_analysis_markdown(graph: Dict[str, Any]) -> str:
    paper = graph.get("paper", {})
    lines = [
        f"# {paper.get('title', 'Citation Map Analysis')}",
        "",
        "## 核心贡献",
    ]
    for contribution in paper.get("core_contributions", []):
        lines.append(f"- {contribution}")
    lines.extend(["", "## 引用意图概览"])
    for citation in graph.get("citations", []):
        lines.append(f"- `{citation['intent']}` · {citation['evidence']}（{citation['citation_id']}）")
    lines.extend(["", "## 图谱说明", "中心节点为目标论文，外围按问题、方法、数据评估、基线结果和局限未来分组展示引用支撑。"])
    return "\n".join(lines) + "\n"


def write_render_outputs(graph: Dict[str, Any], out_dir: Path, visual_mode: str = "all") -> None:
    visual_mode = validate_visual_mode(visual_mode)
    out_dir.mkdir(parents=True, exist_ok=True)

    example_path = out_dir / "citation_map_example.svg"
    if visual_mode == "all":
        svg = render_current_svg(graph)
        example_svg = render_example_svg(graph)
        (out_dir / "citation_map.svg").write_text(svg, encoding="utf-8")
        example_path.write_text(example_svg, encoding="utf-8")
        (out_dir / "citation_map.html").write_text(render_html(graph, svg, example_svg, visual_mode), encoding="utf-8")
    else:
        svg = render_svg(graph, visual_mode)
        (out_dir / "citation_map.svg").write_text(svg, encoding="utf-8")
        if example_path.exists():
            example_path.unlink()
        (out_dir / "citation_map.html").write_text(render_html(graph, svg, None, visual_mode), encoding="utf-8")
    (out_dir / "analysis.md").write_text(render_analysis_markdown(graph), encoding="utf-8")


def _groups_with_defaults(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    by_id = {group.get("group_id"): group for group in graph.get("visual_groups", [])}
    groups = []
    for default in DEFAULT_VISUAL_GROUPS:
        groups.append({**default, **by_id.get(default["group_id"], {})})
    return groups


def _visible_citations_for_group(citations: List[Dict[str, Any]], group: Dict[str, Any]) -> List[Dict[str, Any]]:
    return _visible_citations_for_intents(citations, group.get("intent_filters", []))


def _visible_citations_for_intents(citations: Iterable[Dict[str, Any]], intents: Iterable[str]) -> List[Dict[str, Any]]:
    filters = set(intents)
    visible = [c for c in citations if c.get("intent") in filters and c.get("show_on_map", True)]
    return sorted(visible, key=lambda c: (PRIORITY.get(c.get("intent"), 9), -float(c.get("confidence", 0))))


def _rounded_node(x: int, y: int, width: int, height: int, label: str, stroke: str, fill: str, node_id: str, font_size: int = 16) -> str:
    return f'<g id="{html.escape(node_id)}"><rect x="{x - width/2:.1f}" y="{y - height/2:.1f}" width="{width}" height="{height}" rx="18" fill="{fill}" stroke="{stroke}" stroke-width="2"/><text x="{x}" y="{y + 5}" text-anchor="middle" fill="#344054" font-size="{font_size}" font-weight="600">{html.escape(label)}</text></g>'


def _current_citation_node(x: float, y: float, label: str, color: str, node_id: str) -> str:
    label_text = _multiline_text(x + 18, y + 24, _svg_text_lines(label, 44, max_lines=2), 16, "#344054", 13, "600")
    return f'''<g id="{html.escape(node_id)}" data-node-kind="citation">
  <rect x="{x}" y="{y}" width="{CURRENT_NODE_WIDTH}" height="{CURRENT_NODE_HEIGHT}" rx="18" fill="#fffaf7" stroke="{color}" stroke-width="2"/>
  {label_text}
</g>'''


def _mindmap_leaf(x: int, y: int, label: str, sublabel: str, color: str, node_id: str, chain_id: str) -> str:
    label_text = _multiline_text(x + 20, y + 29, _svg_text_lines(label, 44, max_lines=2), 18, "#344054", 15, "700")
    sublabel_text = _multiline_text(x + 20, y + 66, _svg_text_lines(sublabel, 54, max_lines=1), 16, "#667085", 12, "500")
    return f'''<g id="{html.escape(node_id)}" data-node-kind="citation" data-chain-id="{html.escape(chain_id)}">
  <rect x="{x}" y="{y}" width="{EXAMPLE_NODE_WIDTH}" height="{EXAMPLE_NODE_HEIGHT}" rx="22" fill="#ffffff" stroke="{color}" stroke-width="2"/>
  {label_text}
  {sublabel_text}
</g>'''


def _curve(x1: int, y1: int, x2: int, y2: int, color: str, label: str, dashed: bool = False, opacity: str = "0.78") -> str:
    mid = (x1 + x2) / 2
    dash = ' stroke-dasharray="8 7"' if dashed else ""
    text_x = (x1 + x2) / 2
    text_y = (y1 + y2) / 2 - 10
    return f'<path d="M{x1},{y1} C{mid},{y1} {mid},{y2} {x2},{y2}" fill="none" stroke="{color}" stroke-width="3" opacity="{opacity}"{dash}/><text x="{text_x:.1f}" y="{text_y:.1f}" fill="{color}" font-size="13">{html.escape(label)}</text>'


def _mindmap_curve(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str,
    label: str,
    dashed: bool = False,
    opacity: str = "0.76",
    label_x: float | None = None,
    label_y: float | None = None,
) -> str:
    mid = (x1 + x2) / 2
    dash = ' stroke-dasharray="8 7"' if dashed else ""
    label_part = ""
    if label:
        text_x = (x1 + x2) / 2 - 18 if label_x is None else label_x
        text_y = (y1 + y2) / 2 - 12 if label_y is None else label_y
        label_part = f'<text x="{text_x:.1f}" y="{text_y:.1f}" fill="{color}" font-size="14" font-weight="700">{html.escape(label)}</text>'
    return f'<path d="M{x1:.1f},{y1:.1f} C{mid:.1f},{y1:.1f} {mid:.1f},{y2:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="{color}" stroke-width="3" opacity="{opacity}"{dash}/>{label_part}'


def _cross_links(citations: List[Dict[str, Any]]) -> List[str]:
    links = []
    intents = {citation.get("intent") for citation in citations}
    if "baseline" in intents and ("core-method" in intents or "supporting-method" in intents):
        links.append(_mindmap_curve(560, 720, 540, 330, "#8a5cf6", "方法参照", dashed=True, opacity="0.45"))
    if "result-evidence" in intents and "problem" in intents:
        links.append(_mindmap_curve(560, 720, 560, 110, "#cf6f6f", "问题证据", dashed=True, opacity="0.42"))
    return links


def _cross_links_from_layout(lane_layouts: List[Dict[str, Any]], hub_x: int) -> List[str]:
    hub_by_chain = {
        layout["chain"]["chain_id"]: int(layout["y"] + layout["height"] / 2)
        for layout in lane_layouts
        if layout["visible"]
    }
    links = []
    if "baseline-chain" in hub_by_chain and "method-chain" in hub_by_chain:
        links.append(_mindmap_curve(hub_x + 44, hub_by_chain["baseline-chain"], hub_x + 44, hub_by_chain["method-chain"], "#8a5cf6", "方法参照", dashed=True, opacity="0.28"))
    if "baseline-chain" in hub_by_chain and "problem-chain" in hub_by_chain:
        links.append(_mindmap_curve(hub_x + 72, hub_by_chain["baseline-chain"], hub_x + 72, hub_by_chain["problem-chain"], "#cf6f6f", "问题证据", dashed=True, opacity="0.24"))
    return links


def _lane_background(x: int, y: int, width: int, height: int, color: str, chain_id: str) -> str:
    return f'<rect id="{html.escape(chain_id)}-lane" x="{x}" y="{y}" width="{width}" height="{height}" rx="26" fill="{color}" opacity="0.055" stroke="{color}" stroke-width="1" stroke-opacity="0.18"/>'


def _edge_badge(x: int, y: int, label: str, color: str) -> str:
    width = max(58, len(label) * 18 + 22)
    return f'<g><rect x="{x}" y="{y}" width="{width}" height="28" rx="14" fill="#ffffff" stroke="{color}" stroke-width="1.5"/><text x="{x + width / 2:.1f}" y="{y + 19}" text-anchor="middle" fill="{color}" font-size="13" font-weight="800">{html.escape(label)}</text></g>'


def _ceil_div(value: int, divisor: int) -> int:
    return (value + divisor - 1) // divisor if divisor else 0


def _example_column_count(node_count: int) -> int:
    if node_count <= 0:
        return 1
    return max(1, _ceil_div(node_count, EXAMPLE_MAX_ROWS_PER_COLUMN))


def _svg_text_lines(text: str, max_chars: int, max_lines: int) -> List[str]:
    words = str(text).split()
    if not words:
        return [""]
    lines: List[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if _display_len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
            while _display_len(current) > max_chars:
                lines.append(current[:max_chars])
                current = current[max_chars:]
        if len(lines) == max_lines:
            break
    if len(lines) < max_lines and current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    if len(lines) == max_lines and " ".join(words) != " ".join(lines):
        lines[-1] = _shorten(lines[-1], max(2, len(lines[-1])))
    return lines


def _display_len(text: str) -> int:
    return sum(2 if ord(char) > 127 else 1 for char in text)


def _multiline_text(
    x: float,
    y: float,
    lines: Sequence[str],
    line_height: int,
    fill: str,
    font_size: int,
    font_weight: str,
    anchor: str = "start",
) -> str:
    return "".join(
        f'<text x="{x:.1f}" y="{y + index * line_height:.1f}" text-anchor="{anchor}" fill="{fill}" font-size="{font_size}" font-weight="{font_weight}">{html.escape(line)}</text>'
        for index, line in enumerate(lines)
    )


def _citation_node_label(citation: Dict[str, Any], references: Dict[str, Dict[str, Any]]) -> str:
    target_claim = citation.get("target_claim")
    if target_claim:
        return _shorten(target_claim, 42)
    reference = references.get(citation.get("reference_id"), {})
    ref_label = _reference_label(reference)
    if ref_label:
        return _shorten(ref_label, 42)
    return _shorten(citation.get("evidence") or citation.get("citation_sentence") or citation.get("citation_id", "citation"), 42)


def _reference_label(reference: Dict[str, Any]) -> str:
    if not reference:
        return ""
    authors = reference.get("authors") or []
    year = reference.get("year")
    if authors and year and str(year) != "unknown":
        first = str(authors[0]).split()[-1]
        return f"{first} {year}"
    return str(reference.get("title") or reference.get("raw_reference") or reference.get("reference_id") or "")


def _legend(groups: List[Dict[str, Any]]) -> str:
    items = []
    for index, group in enumerate(groups):
        y = 880 + index * 22
        items.append(f'<rect x="1040" y="{y - 12}" width="14" height="14" rx="3" fill="{group.get("color", "#9aa3ad")}"/><text x="1062" y="{y}" fill="#475467" font-size="13">{html.escape(group.get("label", ""))}</text>')
    return "".join(items)


def _example_legend() -> str:
    items = [
        ("#cf6f6f", "问题链：background / problem"),
        ("#ef6c2f", "方法链：core / supporting / theory"),
        ("#8a5cf6", "数据链：dataset / metric"),
        ("#d18a19", "基线链：baseline / result"),
        ("#4f9c56", "局限/资源链：limitation / tool-resource"),
    ]
    return "".join(
        f'<rect x="1840" y="{96 + idx * 24}" width="14" height="14" rx="3" fill="{color}"/><text x="1862" y="{108 + idx * 24}" fill="#475467" font-size="13">{html.escape(label)}</text>'
        for idx, (color, label) in enumerate(items)
    )


def _html_map_section(title: str, svg: str) -> str:
    return f'<section class="map"><h2>{html.escape(title)}</h2><div class="map-viewport">{svg}</div></section>'


def _shorten(text: str, length: int) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= length else text[: length - 1] + "…"
