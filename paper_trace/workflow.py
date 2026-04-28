from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .io import ensure_output_dir, read_input_text, read_json, safe_stem, write_json
from .providers import get_provider
from .render import write_render_outputs
from .schema import validate_graph


def analyze_input(
    input_path: Path,
    out_dir: Path | None = None,
    provider_name: str = "mock",
    config_path: Path | None = None,
    visual_mode: str = "all",
) -> Path:
    input_path = Path(input_path)
    out_dir = ensure_output_dir(Path(out_dir) if out_dir else Path("outputs") / safe_stem(input_path.name))
    text = read_input_text(input_path)
    (out_dir / "source.txt").write_text(text, encoding="utf-8")

    provider = get_provider(provider_name, config_path=config_path)
    graph = provider.extract_graph(text, input_path.name)
    graph.setdefault("metadata", {})["visual_mode"] = visual_mode
    validate_graph(graph)
    write_json(out_dir / "citation_graph.json", graph)
    write_render_outputs(graph, out_dir, visual_mode=visual_mode)
    return out_dir


def render_graph_file(graph_path: Path, out_dir: Path, visual_mode: str = "all") -> Path:
    graph = read_json(graph_path)
    graph.setdefault("metadata", {})["visual_mode"] = visual_mode
    validate_graph(graph)
    out_dir = ensure_output_dir(out_dir)
    write_render_outputs(graph, out_dir, visual_mode=visual_mode)
    return out_dir


def validate_graph_file(graph_path: Path) -> Dict[str, Any]:
    graph = read_json(graph_path)
    validate_graph(graph)
    return graph
