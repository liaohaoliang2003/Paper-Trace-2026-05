from __future__ import annotations

import html
from pathlib import Path
from typing import Any, Dict, List

from .schema import DEFAULT_VISUAL_GROUPS


GROUP_ANCHORS = {
    "problem-background": (360, 170),
    "method-core": (350, 390),
    "data-eval": (390, 600),
    "baseline-result": (410, 780),
    "limits-future": (650, 850),
}

TARGET = (980, 500)
PRIORITY = {"core-method": 0, "dataset": 1, "metric": 2, "baseline": 3}


def render_svg(graph: Dict[str, Any]) -> str:
    paper = graph.get("paper", {})
    title = _shorten(paper.get("title", "Target Paper"), 64)
    groups = _groups_with_defaults(graph)
    citations = graph.get("citations", [])
    edges: List[str] = []
    nodes: List[str] = []

    for group in groups:
        group_id = group["group_id"]
        color = group.get("color", "#9aa3ad")
        x, y = GROUP_ANCHORS.get(group_id, (360, 500))
        visible = _visible_citations_for_group(citations, group)
        edges.append(_curve(TARGET[0] - 120, TARGET[1], x + 130, y, color, group.get("label", group_id)))
        nodes.append(_rounded_node(x, y, 230, 50, group.get("label", group_id), color, "#ffffff", group_id))
        for offset, citation in enumerate(visible[:5]):
            node_y = y + 80 + offset * 54
            label = _shorten(citation.get("citation_sentence", citation["citation_id"]), 48)
            nodes.append(_rounded_node(x - 90, node_y, 330, 38, label, color, "#fffaf7", citation["citation_id"], 13))
            edges.append(_curve(x + 35, y + 50, x + 20, node_y, color, citation.get("intent", ""), dashed=False, opacity="0.55"))
        overflow = len(visible) - 5
        if overflow > 0:
            nodes.append(f'<text x="{x - 70}" y="{y + 80 + 5 * 54}" fill="#667085" font-size="13">+{overflow} citations</text>')

    legend = _legend(groups)
    svg = f'''<svg id="citation-map" width="1400" height="1000" viewBox="0 0 1400 1000" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Citation Map">
  <defs>
    <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#8b98a8" flood-opacity="0.18"/></filter>
  </defs>
  <rect width="1400" height="1000" fill="#fbfbfa"/>
  <text x="60" y="70" fill="#1f2937" font-size="30" font-weight="700">Citation Map</text>
  <text x="60" y="100" fill="#667085" font-size="15">Mock-provider workflow view · intent grouped radial graph</text>
  <g id="edges">{''.join(edges)}</g>
  <g id="groups">{''.join(nodes)}</g>
  <g id="target-paper" filter="url(#soft-shadow)">
    <rect x="820" y="455" width="330" height="90" rx="32" fill="#eaf1f4"/>
    <text x="985" y="492" text-anchor="middle" fill="#243447" font-size="22" font-weight="700">{html.escape(title)}</text>
    <text x="985" y="522" text-anchor="middle" fill="#667085" font-size="14">target-paper</text>
  </g>
  <g id="legend">{legend}</g>
</svg>'''
    return svg


def render_html(graph: Dict[str, Any], svg: str) -> str:
    title = html.escape(graph.get("paper", {}).get("title", "Citation Map"))
    citations = graph.get("citations", [])
    rows = "".join(
        f"<tr><td>{html.escape(c.get('citation_id',''))}</td><td>{html.escape(c.get('intent',''))}</td><td>{html.escape(c.get('evidence',''))}</td></tr>"
        for c in citations
    )
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title} · Citation Map</title>
  <style>
    body {{ margin: 0; font-family: Inter, "Segoe UI", Arial, sans-serif; background: #f6f7f8; color: #172033; }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 28px; }}
    .map {{ overflow: auto; background: white; border-radius: 24px; box-shadow: 0 20px 60px rgba(31,41,55,.08); }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 24px; background: white; border-radius: 16px; overflow: hidden; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #edf0f2; text-align: left; vertical-align: top; }}
    th {{ background: #f2f4f7; }}
  </style>
</head>
<body><main>
  <h1>{title}</h1>
  <section class="map">{svg}</section>
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


def write_render_outputs(graph: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    svg = render_svg(graph)
    (out_dir / "citation_map.svg").write_text(svg, encoding="utf-8")
    (out_dir / "citation_map.html").write_text(render_html(graph, svg), encoding="utf-8")
    (out_dir / "analysis.md").write_text(render_analysis_markdown(graph), encoding="utf-8")


def _groups_with_defaults(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    by_id = {group.get("group_id"): group for group in graph.get("visual_groups", [])}
    groups = []
    for default in DEFAULT_VISUAL_GROUPS:
        groups.append({**default, **by_id.get(default["group_id"], {})})
    return groups


def _visible_citations_for_group(citations: List[Dict[str, Any]], group: Dict[str, Any]) -> List[Dict[str, Any]]:
    filters = set(group.get("intent_filters", []))
    visible = [c for c in citations if c.get("intent") in filters and c.get("show_on_map", True)]
    return sorted(visible, key=lambda c: (PRIORITY.get(c.get("intent"), 9), -float(c.get("confidence", 0))))


def _rounded_node(x: int, y: int, width: int, height: int, label: str, stroke: str, fill: str, node_id: str, font_size: int = 16) -> str:
    return f'<g id="{html.escape(node_id)}"><rect x="{x - width/2:.1f}" y="{y - height/2:.1f}" width="{width}" height="{height}" rx="18" fill="{fill}" stroke="{stroke}" stroke-width="2"/><text x="{x}" y="{y + 5}" text-anchor="middle" fill="#344054" font-size="{font_size}" font-weight="600">{html.escape(label)}</text></g>'


def _curve(x1: int, y1: int, x2: int, y2: int, color: str, label: str, dashed: bool = False, opacity: str = "0.78") -> str:
    mid = (x1 + x2) / 2
    dash = ' stroke-dasharray="8 7"' if dashed else ""
    text_x = (x1 + x2) / 2
    text_y = (y1 + y2) / 2 - 10
    return f'<path d="M{x1},{y1} C{mid},{y1} {mid},{y2} {x2},{y2}" fill="none" stroke="{color}" stroke-width="3" opacity="{opacity}"{dash}/><text x="{text_x:.1f}" y="{text_y:.1f}" fill="{color}" font-size="13">{html.escape(label)}</text>'


def _legend(groups: List[Dict[str, Any]]) -> str:
    items = []
    for index, group in enumerate(groups):
        y = 880 + index * 22
        items.append(f'<rect x="1040" y="{y - 12}" width="14" height="14" rx="3" fill="{group.get("color", "#9aa3ad")}"/><text x="1062" y="{y}" fill="#475467" font-size="13">{html.escape(group.get("label", ""))}</text>')
    return "".join(items)


def _shorten(text: str, length: int) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= length else text[: length - 1] + "…"
