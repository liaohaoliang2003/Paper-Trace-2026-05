from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import ConfigError, clear_provider_config, default_config_path, list_masked_config, save_provider_config
from .io import InputReadError
from .schema import ValidationError
from .workflow import analyze_input, render_graph_file, validate_graph_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="paper_trace", description="Paper citation intent graph CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a PDF/text input and write graph outputs")
    analyze.add_argument("input", type=Path)
    analyze.add_argument("--out", type=Path, default=None)
    analyze.add_argument("--provider", default="mock")

    render = subparsers.add_parser("render", help="Render SVG/HTML from citation_graph.json")
    render.add_argument("graph_json", type=Path)
    render.add_argument("--out", type=Path, required=True)

    validate = subparsers.add_parser("validate", help="Validate citation_graph.json")
    validate.add_argument("graph_json", type=Path)

    web = subparsers.add_parser("web", help="Start Flask web UI")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8765)
    web_debug = web.add_mutually_exclusive_group()
    web_debug.add_argument("--debug", dest="debug", action="store_true", default=True, help="Run Flask with debug mode enabled")
    web_debug.add_argument("--no-debug", dest="debug", action="store_false", help="Run Flask with debug mode disabled")

    config = subparsers.add_parser("config", help="Manage local Paper Trace API configuration")
    config_subparsers = config.add_subparsers(dest="config_command", required=True)

    config_subparsers.add_parser("list", help="List masked local provider configuration")
    config_subparsers.add_parser("path", help="Print the local configuration path")

    config_get = config_subparsers.add_parser("get", help="Show one provider configuration")
    config_get.add_argument("--provider", required=True, choices=["openai-compatible", "zhipu-glm"])

    config_set = config_subparsers.add_parser("set", help="Set one provider configuration")
    config_set.add_argument("--provider", required=True, choices=["openai-compatible", "zhipu-glm"])
    config_set.add_argument("--api-key", default=None)
    config_set.add_argument("--base-url", default=None)
    config_set.add_argument("--model", default=None)
    config_set.add_argument("--stream", choices=["true", "false"], default=None)
    config_set.add_argument("--timeout", default=None)

    config_clear = config_subparsers.add_parser("clear", help="Clear one provider configuration")
    config_clear.add_argument("--provider", required=True, choices=["openai-compatible", "zhipu-glm"])

    args = parser.parse_args(argv)
    try:
        if args.command == "analyze":
            out_dir = analyze_input(args.input, args.out, args.provider)
            print(f"Wrote outputs to {out_dir}")
            return 0
        if args.command == "render":
            out_dir = render_graph_file(args.graph_json, args.out)
            print(f"Rendered outputs to {out_dir}")
            return 0
        if args.command == "validate":
            validate_graph_file(args.graph_json)
            print("citation_graph.json is valid")
            return 0
        if args.command == "web":
            from .web.app import create_app

            app = create_app()
            app.run(host=args.host, port=args.port, debug=args.debug)
            return 0
        if args.command == "config":
            return _handle_config(args)
    except (InputReadError, ValidationError, ValueError, ConfigError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 1


def _handle_config(args: argparse.Namespace) -> int:
    if args.config_command == "path":
        print(default_config_path())
        return 0
    if args.config_command == "list":
        print(json.dumps(list_masked_config(), ensure_ascii=False, indent=2))
        return 0
    if args.config_command == "get":
        data = list_masked_config().get("providers", {}).get(args.provider, {})
        print(json.dumps({args.provider: data}, ensure_ascii=False, indent=2))
        return 0
    if args.config_command == "set":
        values = {"api_key": args.api_key, "model": args.model}
        if args.provider == "openai-compatible":
            values["base_url"] = args.base_url
            values["stream"] = args.stream
            values["timeout"] = args.timeout
        save_provider_config(args.provider, values)
        masked = list_masked_config().get("providers", {}).get(args.provider, {})
        print(json.dumps({args.provider: masked}, ensure_ascii=False, indent=2))
        return 0
    if args.config_command == "clear":
        clear_provider_config(args.provider)
        print(f"Cleared local config for {args.provider}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
