from __future__ import annotations

import re
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

from ..config import ConfigError, get_provider_config, list_masked_config, save_provider_config
from ..io import InputReadError, read_json, safe_stem, write_json
from ..render import write_render_outputs
from ..schema import ALLOWED_INTENTS, ValidationError, validate_citation_edit, validate_graph
from ..workflow import analyze_input


PROVIDER_OPTIONS = ["mock", "openai-compatible", "zhipu-glm"]


def create_app(output_root: Path | str = Path("outputs") / "web", config_path: Path | str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["OUTPUT_ROOT"] = Path(output_root)
    app.config["PAPER_TRACE_CONFIG_PATH"] = Path(config_path) if config_path else None
    app.config["OUTPUT_ROOT"].mkdir(parents=True, exist_ok=True)

    @app.get("/")
    def index():
        return _render_index(app, None, "mock")

    @app.post("/analyze")
    def analyze_upload():
        provider_name = request.form.get("provider", "mock")
        if provider_name not in PROVIDER_OPTIONS:
            return _render_index(app, "不支持的 provider", "mock"), 400

        uploaded = request.files.get("file")
        if not uploaded or not uploaded.filename:
            return _render_index(app, "请选择 .txt、.md 或 .pdf 文件", provider_name), 400

        stem = safe_stem(uploaded.filename)
        run_dir = _unique_run_dir(app.config["OUTPUT_ROOT"], stem)
        input_path = run_dir / uploaded.filename
        run_dir.mkdir(parents=True, exist_ok=True)
        uploaded.save(input_path)
        try:
            analyze_input(input_path, run_dir, provider_name, config_path=_config_path(app))
        except (InputReadError, ValidationError, ValueError, RuntimeError) as exc:
            return _render_index(app, str(exc), provider_name), 400
        return redirect(url_for("view_run", run_id=run_dir.name))

    @app.post("/settings")
    def save_settings():
        provider_name = request.form.get("provider", "")
        if provider_name not in PROVIDER_OPTIONS or provider_name == "mock":
            return _render_index(app, "请选择可配置的真实 provider", "mock"), 400

        try:
            current = get_provider_config(provider_name, _config_path(app))
            values = {"model": request.form.get("model", "").strip()}
            if provider_name == "openai-compatible":
                values["base_url"] = request.form.get("base_url", "").strip()
                values["stream"] = "true" if request.form.get("stream") == "on" else "false"
                values["timeout"] = request.form.get("timeout", "").strip()
            if request.form.get("clear_api_key") == "on":
                values["api_key"] = ""
            else:
                submitted_key = request.form.get("api_key", "").strip()
                values["api_key"] = submitted_key if submitted_key else current.get("api_key")
            save_provider_config(provider_name, values, _config_path(app))
        except ConfigError as exc:
            return _render_index(app, str(exc), provider_name), 400
        return redirect(url_for("index"))

    @app.get("/run/<run_id>")
    def view_run(run_id: str):
        run_dir = _safe_run_dir(app.config["OUTPUT_ROOT"], run_id)
        graph = _load_graph_or_404(run_dir)
        svg = (run_dir / "citation_map.svg").read_text(encoding="utf-8") if (run_dir / "citation_map.svg").exists() else ""
        analysis = (run_dir / "analysis.md").read_text(encoding="utf-8") if (run_dir / "analysis.md").exists() else ""
        return render_template(
            "run.html",
            run_id=run_id,
            graph=graph,
            svg=svg,
            analysis=analysis,
            intents=ALLOWED_INTENTS,
            error=None,
        )

    @app.post("/edit/<run_id>/<citation_id>")
    def edit_citation(run_id: str, citation_id: str):
        run_dir = _safe_run_dir(app.config["OUTPUT_ROOT"], run_id)
        graph_path = run_dir / "citation_graph.json"
        graph = _load_graph_or_404(run_dir)
        citation = next((item for item in graph.get("citations", []) if item.get("citation_id") == citation_id), None)
        if citation is None:
            abort(404)
        try:
            confidence = float(request.form.get("confidence", "0"))
        except ValueError:
            confidence = -1
        intent = request.form.get("intent", "")
        evidence = request.form.get("evidence", "")
        errors = validate_citation_edit(intent, confidence, evidence)
        if errors:
            return "\n".join(errors), 400

        citation["intent"] = intent
        citation["confidence"] = confidence
        citation["evidence"] = evidence
        citation["notes"] = request.form.get("notes", "")
        citation["show_on_map"] = request.form.get("show_on_map") == "on"
        validate_graph(graph)
        write_json(graph_path, graph)
        write_render_outputs(graph, run_dir)
        return redirect(url_for("view_run", run_id=run_id))

    return app


def _render_index(app: Flask, error: str | None, selected_provider: str):
    return render_template(
        "index.html",
        runs=_list_runs(app.config["OUTPUT_ROOT"]),
        error=error,
        providers=PROVIDER_OPTIONS,
        configurable_providers=[provider for provider in PROVIDER_OPTIONS if provider != "mock"],
        provider_settings=_provider_settings(app),
        selected_provider=selected_provider if selected_provider in PROVIDER_OPTIONS else "mock",
    )


def _provider_settings(app: Flask):
    try:
        return list_masked_config(_config_path(app)).get("providers", {})
    except ConfigError:
        return {}


def _config_path(app: Flask):
    return app.config.get("PAPER_TRACE_CONFIG_PATH")


def _list_runs(root: Path):
    runs = []
    if root.exists():
        for child in sorted(root.iterdir()):
            if child.is_dir() and (child / "citation_graph.json").exists():
                runs.append(child.name)
    return runs


def _unique_run_dir(root: Path, stem: str) -> Path:
    candidate = root / stem
    counter = 2
    while candidate.exists():
        candidate = root / f"{stem}-{counter}"
        counter += 1
    return candidate


def _safe_run_dir(root: Path, run_id: str) -> Path:
    clean = safe_run_id(run_id)
    if clean != run_id:
        abort(404)
    run_dir = root / clean
    if not run_dir.exists():
        abort(404)
    return run_dir


def safe_run_id(run_id: str) -> str:
    normalized = (run_id or "").strip().lower()
    normalized = normalized.replace("\\", "/")
    if "/" in normalized:
        return ""
    normalized = re.sub(r"[^a-z0-9._-]+", "-", normalized).strip("-._")
    return normalized


def _load_graph_or_404(run_dir: Path):
    graph_path = run_dir / "citation_graph.json"
    if not graph_path.exists():
        abort(404)
    return read_json(graph_path)
