import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SAMPLE_TEXT = """
Mock Paper Title

Abstract
This paper proposes a citation graph workflow for scientific papers.

Introduction
Prior work introduced attention mechanisms [1]. Existing systems face long-context limitations [2].

Method
We build on graph extraction methods [3] and use SciCite-style labels [4].

Experiments
We evaluate on a benchmark dataset [5] using macro-F1 [6] and compare against a baseline system [7].

References
[1] Attention Mechanisms for Sequence Modeling. 2014.
[2] Long Context Limitations in Neural Models. 2016.
[3] Graph Extraction for Papers. 2020.
[4] SciCite: A Dataset for Citation Intent. 2019.
[5] Paper Benchmark Dataset. 2021.
[6] Macro F1 Evaluation. 2018.
[7] Baseline Citation System. 2022.
""".strip()


class PaperTraceTests(unittest.TestCase):
    def test_config_cli_set_list_get_clear_and_path(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "PYTHONPATH": str(repo)}
            secret = "test-secret-123456"
            set_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "paper_trace",
                    "config",
                    "set",
                    "--provider",
                    "openai-compatible",
                    "--api-key",
                    secret,
                    "--base-url",
                    "https://example.invalid/v1",
                    "--model",
                    "fake-model",
                    "--stream",
                    "true",
                    "--timeout",
                    "300",
                ],
                cwd=tmp,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(set_result.returncode, 0, set_result.stderr)
            self.assertTrue((Path(tmp) / ".paper_trace" / "config.json").exists())

            list_result = subprocess.run(
                [sys.executable, "-m", "paper_trace", "config", "list"],
                cwd=tmp,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(list_result.returncode, 0, list_result.stderr)
            self.assertIn("openai-compatible", list_result.stdout)
            self.assertIn("te**************56", list_result.stdout)
            self.assertIn('"stream": "true"', list_result.stdout)
            self.assertIn('"timeout": "300"', list_result.stdout)
            self.assertNotIn(secret, list_result.stdout)

            get_result = subprocess.run(
                [sys.executable, "-m", "paper_trace", "config", "get", "--provider", "openai-compatible"],
                cwd=tmp,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(get_result.returncode, 0, get_result.stderr)
            self.assertIn("fake-model", get_result.stdout)
            self.assertNotIn(secret, get_result.stdout)

            path_result = subprocess.run(
                [sys.executable, "-m", "paper_trace", "config", "path"],
                cwd=tmp,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(path_result.returncode, 0, path_result.stderr)
            self.assertIn(".paper_trace", path_result.stdout)

            clear_result = subprocess.run(
                [sys.executable, "-m", "paper_trace", "config", "clear", "--provider", "openai-compatible"],
                cwd=tmp,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(clear_result.returncode, 0, clear_result.stderr)
            config_data = json.loads((Path(tmp) / ".paper_trace" / "config.json").read_text(encoding="utf-8"))
            self.assertNotIn("openai-compatible", config_data.get("providers", {}))

    def test_config_file_is_used_by_provider_and_bad_json_fails(self):
        from paper_trace.config import ConfigError, save_provider_config
        from paper_trace.providers import OpenAICompatibleProvider

        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {}, clear=True):
            config_path = Path(tmp) / ".paper_trace" / "config.json"
            save_provider_config(
                "openai-compatible",
                {
                    "api_key": "test-secret-abcdef",
                    "base_url": "https://example.invalid/v1",
                    "model": "configured-model",
                    "stream": "false",
                    "timeout": "120",
                },
                config_path,
            )

            class FakeClient:
                class chat:
                    class completions:
                        @staticmethod
                        def create(**kwargs):
                            raise AssertionError("request should not be called")

            provider = OpenAICompatibleProvider(client=FakeClient(), config_path=config_path)
            self.assertEqual(provider.api_key, "test-secret-abcdef")
            self.assertEqual(provider.base_url, "https://example.invalid/v1")
            self.assertEqual(provider.model, "configured-model")
            self.assertFalse(provider.stream)
            self.assertEqual(provider.timeout, 120)

            config_path.write_text("{bad json", encoding="utf-8")
            with self.assertRaises(ConfigError):
                OpenAICompatibleProvider(client=FakeClient(), config_path=config_path)

        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(
            os.environ,
            {
                "PAPER_TRACE_OPENAI_API_KEY": "env-secret",
                "PAPER_TRACE_OPENAI_STREAM": "false",
                "PAPER_TRACE_OPENAI_TIMEOUT": "120",
            },
            clear=True,
        ):
            provider = OpenAICompatibleProvider(client=FakeClient(), config_path=Path(tmp) / "missing.json")
            self.assertEqual(provider.api_key, "env-secret")
            self.assertFalse(provider.stream)
            self.assertEqual(provider.timeout, 120)

    def test_web_cli_debug_mode_defaults_on_and_can_be_disabled(self):
        from paper_trace import __main__ as cli

        class FakeApp:
            calls = []

            def run(self, **kwargs):
                self.calls.append(kwargs)

        fake_app = FakeApp()
        with mock.patch("paper_trace.web.app.create_app", return_value=fake_app):
            self.assertEqual(cli.main(["web", "--host", "127.0.0.1", "--port", "9999"]), 0)
            self.assertTrue(fake_app.calls[-1]["debug"])
            self.assertEqual(fake_app.calls[-1]["port"], 9999)

            self.assertEqual(cli.main(["web", "--no-debug"]), 0)
            self.assertFalse(fake_app.calls[-1]["debug"])

    def test_provider_routing_and_missing_config_errors(self):
        from paper_trace.providers import MockProvider, get_provider

        self.assertIsInstance(get_provider("mock"), MockProvider)
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {}, clear=True):
            original_cwd = Path.cwd()
            try:
                os.chdir(tmp)
                with self.assertRaisesRegex(ValueError, "PAPER_TRACE_OPENAI_API_KEY"):
                    get_provider("openai-compatible")
                with self.assertRaisesRegex(ValueError, "PAPER_TRACE_ZHIPU_API_KEY"):
                    get_provider("zhipu-glm")
            finally:
                os.chdir(original_cwd)
        with self.assertRaisesRegex(ValueError, "Unknown provider"):
            get_provider("bad-provider")

    def test_llm_json_parser_accepts_fenced_json_and_rejects_invalid(self):
        from paper_trace.providers import MockProvider, parse_llm_json
        from paper_trace.schema import ValidationError, validate_graph

        graph = MockProvider().extract_graph(SAMPLE_TEXT, "sample.txt")
        fenced = "```json\n" + json.dumps(graph, ensure_ascii=False) + "\n```"
        self.assertEqual(parse_llm_json(fenced), graph)

        with self.assertRaises(ValueError):
            parse_llm_json("not json")
        with self.assertRaises(ValueError):
            parse_llm_json("[]")

        graph["citations"][0]["intent"] = "bad"
        with self.assertRaises(ValidationError):
            validate_graph(parse_llm_json(json.dumps(graph, ensure_ascii=False)))

    def test_real_provider_paths_with_fake_clients(self):
        from paper_trace.providers import MockProvider, OpenAICompatibleProvider, ZhipuGLMProvider
        from paper_trace.schema import validate_graph

        graph = MockProvider().extract_graph(SAMPLE_TEXT, "sample.txt")
        incomplete_graph = json.loads(json.dumps(graph, ensure_ascii=False))
        incomplete_graph["paper"].pop("abstract")
        incomplete_graph["paper"].pop("core_contributions")

        class FakeOpenAIMessage:
            content = json.dumps(incomplete_graph, ensure_ascii=False)

        class FakeOpenAIChoice:
            message = FakeOpenAIMessage()

        class FakeOpenAIResponse:
            choices = [FakeOpenAIChoice()]

        class FakeOpenAICompletions:
            @staticmethod
            def create(**kwargs):
                self.assertEqual(kwargs["model"], "fake-openai-model")
                self.assertFalse(kwargs["stream"])
                return FakeOpenAIResponse()

        class FakeOpenAIClient:
            class chat:
                completions = FakeOpenAICompletions()

        openai_provider = OpenAICompatibleProvider(
            "test-key",
            "https://example.invalid/v1",
            "fake-openai-model",
            stream=False,
            timeout=120,
            client=FakeOpenAIClient(),
        )
        openai_graph = openai_provider.extract_graph(SAMPLE_TEXT, "sample.txt")
        validate_graph(openai_graph)
        self.assertTrue(openai_graph["paper"]["abstract"])
        self.assertEqual(openai_graph["paper"]["core_contributions"], [])

        json_text = json.dumps(incomplete_graph, ensure_ascii=False)

        class FakeDelta:
            def __init__(self, content):
                self.content = content

        class FakeStreamChoice:
            def __init__(self, content):
                self.delta = FakeDelta(content)

        class FakeStreamChunk:
            def __init__(self, content):
                self.choices = [FakeStreamChoice(content)]

        class FakeStreamingCompletions:
            @staticmethod
            def create(**kwargs):
                self.assertTrue(kwargs["stream"])
                midpoint = len(json_text) // 2
                return [FakeStreamChunk(json_text[:midpoint]), FakeStreamChunk(json_text[midpoint:])]

        class FakeStreamingClient:
            class chat:
                completions = FakeStreamingCompletions()

        streaming_provider = OpenAICompatibleProvider(
            "test-key",
            "https://example.invalid/v1",
            "fake-openai-model",
            stream=True,
            timeout=300,
            client=FakeStreamingClient(),
        )
        streaming_graph = streaming_provider.extract_graph(SAMPLE_TEXT, "sample.txt")
        validate_graph(streaming_graph)
        self.assertTrue(streaming_graph["paper"]["abstract"])
        self.assertEqual(streaming_graph["paper"]["core_contributions"], [])

        class FakeFailingCompletions:
            @staticmethod
            def create(**kwargs):
                raise RuntimeError("Connection error")

        class FakeFailingClient:
            class chat:
                completions = FakeFailingCompletions()

        failing_provider = OpenAICompatibleProvider(
            "test-key",
            "https://example.invalid/v1",
            "fake-openai-model",
            stream=False,
            timeout=120,
            client=FakeFailingClient(),
        )
        with self.assertRaisesRegex(RuntimeError, "stream=false.*timeout=120.*RuntimeError.*stream=true"):
            failing_provider.extract_graph(SAMPLE_TEXT, "sample.txt")

        class FakeGLMMessage:
            content = "```json\n" + json.dumps(incomplete_graph, ensure_ascii=False) + "\n```"

        class FakeGLMChoice:
            message = FakeGLMMessage()

        class FakeGLMResponse:
            choices = [FakeGLMChoice()]

        class FakeGLMCompletions:
            @staticmethod
            def create(**kwargs):
                self.assertEqual(kwargs["model"], "fake-glm-model")
                return FakeGLMResponse()

        class FakeGLMClient:
            class chat:
                completions = FakeGLMCompletions()

        glm_provider = ZhipuGLMProvider("test-key", "fake-glm-model", FakeGLMClient())
        glm_graph = glm_provider.extract_graph(SAMPLE_TEXT, "sample.txt")
        validate_graph(glm_graph)
        self.assertTrue(glm_graph["paper"]["abstract"])
        self.assertEqual(glm_graph["paper"]["core_contributions"], [])

    def test_schema_rejects_invalid_intent_and_missing_reference_state(self):
        from paper_trace.providers import MockProvider
        from paper_trace.schema import ValidationError, validate_graph

        graph = MockProvider().extract_graph(SAMPLE_TEXT, "sample.txt")
        validate_graph(graph)

        graph_missing_paper_meta = MockProvider().extract_graph(SAMPLE_TEXT, "sample.txt")
        graph_missing_paper_meta["paper"].pop("abstract")
        graph_missing_paper_meta["paper"].pop("core_contributions")
        with self.assertRaisesRegex(ValidationError, "paper missing field: abstract"):
            validate_graph(graph_missing_paper_meta)

        graph["citations"][0]["intent"] = "not-an-intent"
        with self.assertRaises(ValidationError):
            validate_graph(graph)

        graph = MockProvider().extract_graph(SAMPLE_TEXT, "sample.txt")
        graph["citations"][0]["reference_id"] = None
        graph["citations"][0]["unmatched_reference"] = False
        with self.assertRaises(ValidationError):
            validate_graph(graph)

    def test_mock_provider_is_deterministic_and_complete(self):
        from paper_trace.providers import MockProvider
        from paper_trace.schema import validate_graph

        provider = MockProvider()
        first = provider.extract_graph(SAMPLE_TEXT, "sample.txt")
        second = provider.extract_graph(SAMPLE_TEXT, "sample.txt")

        self.assertEqual(first, second)
        self.assertGreaterEqual(len(first["citations"]), 5)
        self.assertGreaterEqual(len(first["entities"]), 3)
        self.assertTrue(first["visual_groups"])
        validate_graph(first)

    def test_render_outputs_svg_and_html(self):
        from paper_trace.providers import MockProvider
        from paper_trace.render import render_html, render_svg, write_render_outputs

        graph = MockProvider().extract_graph(SAMPLE_TEXT, "sample.txt")
        svg = render_svg(graph, visual_mode="current")
        example_svg = render_svg(graph, visual_mode="example")
        html = render_html(graph, svg, example_svg, visual_mode="all")

        self.assertIn("<svg", svg)
        self.assertIn("target-paper", svg)
        self.assertIn("legend", svg)
        self.assertIn("<svg", example_svg)
        self.assertIn("target-paper", example_svg)
        self.assertIn("问题链", example_svg)
        self.assertIn("方法链", example_svg)
        self.assertIn("数据链", example_svg)
        self.assertIn("基线链", example_svg)
        self.assertIn("citation-map", html)
        self.assertIn("Citation Map", html)
        self.assertIn("citation-map-example", html)

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "all"
            write_render_outputs(graph, out_dir, visual_mode="all")
            self.assertTrue((out_dir / "citation_map.svg").exists())
            self.assertTrue((out_dir / "citation_map_example.svg").exists())
            self.assertTrue((out_dir / "citation_map.html").exists())

            example_dir = Path(tmp) / "example"
            write_render_outputs(graph, example_dir, visual_mode="example")
            self.assertTrue((example_dir / "citation_map.svg").exists())
            self.assertTrue((example_dir / "citation_map.html").exists())
            self.assertFalse((example_dir / "citation_map_example.svg").exists())
            self.assertIn("问题链", (example_dir / "citation_map.svg").read_text(encoding="utf-8"))

            with self.assertRaisesRegex(ValueError, "hybrid visual mode"):
                write_render_outputs(graph, Path(tmp) / "hybrid", visual_mode="hybrid")

    def test_cli_analyze_validate_and_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sample = root / "sample.txt"
            out_dir = root / "out"
            render_dir = root / "rendered"
            sample.write_text(SAMPLE_TEXT, encoding="utf-8")

            analyze = subprocess.run(
                [sys.executable, "-m", "paper_trace", "analyze", str(sample), "--out", str(out_dir), "--provider", "mock"],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
            )
            self.assertEqual(analyze.returncode, 0, analyze.stderr)

            for name in ["analysis.md", "citation_graph.json", "citation_map.svg", "citation_map.html", "source.txt"]:
                self.assertTrue((out_dir / name).exists(), name)
            self.assertTrue((out_dir / "citation_map_example.svg").exists())

            validate = subprocess.run(
                [sys.executable, "-m", "paper_trace", "validate", str(out_dir / "citation_graph.json")],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
            )
            self.assertEqual(validate.returncode, 0, validate.stderr)

            render = subprocess.run(
                [sys.executable, "-m", "paper_trace", "render", str(out_dir / "citation_graph.json"), "--out", str(render_dir)],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
            )
            self.assertEqual(render.returncode, 0, render.stderr)
            self.assertTrue((render_dir / "citation_map.svg").exists())
            self.assertTrue((render_dir / "citation_map_example.svg").exists())
            self.assertTrue((render_dir / "citation_map.html").exists())

            example_render_dir = root / "rendered-example"
            render_example = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "paper_trace",
                    "render",
                    str(out_dir / "citation_graph.json"),
                    "--out",
                    str(example_render_dir),
                    "--visual-mode",
                    "example",
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
            )
            self.assertEqual(render_example.returncode, 0, render_example.stderr)
            self.assertTrue((example_render_dir / "citation_map.svg").exists())
            self.assertFalse((example_render_dir / "citation_map_example.svg").exists())

            render_hybrid = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "paper_trace",
                    "render",
                    str(out_dir / "citation_graph.json"),
                    "--out",
                    str(root / "rendered-hybrid"),
                    "--visual-mode",
                    "hybrid",
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(render_hybrid.returncode, 0)
            self.assertIn("hybrid visual mode", render_hybrid.stderr)

    def test_flask_upload_and_edit_flow(self):
        from paper_trace.web.app import create_app

        with tempfile.TemporaryDirectory() as tmp:
            app = create_app(output_root=Path(tmp) / "web", config_path=Path(tmp) / ".paper_trace" / "config.json")
            client = app.test_client()
            index = client.get("/")
            self.assertEqual(index.status_code, 200)
            self.assertIn("图像模式".encode("utf-8"), index.data)

            upload = client.post(
                "/analyze",
                data={"visual_mode": "all", "file": (self._bytes_file(SAMPLE_TEXT), "sample.txt")},
                content_type="multipart/form-data",
                follow_redirects=True,
            )
            self.assertEqual(upload.status_code, 200)
            self.assertIn(b"citation-workspace", upload.data)
            self.assertIn("例图引用链视图".encode("utf-8"), upload.data)

            graph_path = next((Path(tmp) / "web").glob("*/citation_graph.json"))
            graph = json.loads(graph_path.read_text(encoding="utf-8"))
            citation_id = graph["citations"][0]["citation_id"]

            invalid = client.post(
                f"/edit/{graph_path.parent.name}/{citation_id}",
                data={"intent": "bad", "confidence": "0.5", "evidence": "x", "notes": "", "show_on_map": "on"},
            )
            self.assertEqual(invalid.status_code, 400)
            unchanged = json.loads(graph_path.read_text(encoding="utf-8"))
            self.assertEqual(unchanged["citations"][0]["intent"], graph["citations"][0]["intent"])

            valid = client.post(
                f"/edit/{graph_path.parent.name}/{citation_id}",
                data={"intent": "dataset", "confidence": "0.77", "evidence": "Updated evidence", "notes": "curated", "show_on_map": "on"},
                follow_redirects=True,
            )
            self.assertEqual(valid.status_code, 200)
            updated = json.loads(graph_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["citations"][0]["intent"], "dataset")
            self.assertEqual(updated["citations"][0]["notes"], "curated")
            self.assertTrue((graph_path.parent / "citation_map.svg").exists())
            self.assertTrue((graph_path.parent / "citation_map_example.svg").exists())

            hybrid = client.post(
                "/analyze",
                data={"visual_mode": "hybrid", "file": (self._bytes_file(SAMPLE_TEXT), "hybrid.txt")},
                content_type="multipart/form-data",
            )
            self.assertEqual(hybrid.status_code, 400)
            self.assertIn("混合可展开知识图谱模式暂未实现".encode("utf-8"), hybrid.data)

    def test_flask_run_id_with_dots_and_suffix_opens(self):
        from paper_trace.providers import MockProvider
        from paper_trace.render import write_render_outputs
        from paper_trace.web.app import create_app

        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "web"
            run_dir = output_root / "2024.emnlp-main.726-17"
            run_dir.mkdir(parents=True)
            graph = MockProvider().extract_graph(SAMPLE_TEXT, "2024.emnlp-main.726.pdf")
            (run_dir / "citation_graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
            write_render_outputs(graph, run_dir)

            app = create_app(output_root=output_root, config_path=Path(tmp) / ".paper_trace" / "config.json")
            client = app.test_client()

            response = client.get("/run/2024.emnlp-main.726-17")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"citation-workspace", response.data)

            self.assertEqual(client.get("/run/../bad").status_code, 404)
            self.assertEqual(client.get("/run/bad%5Cname").status_code, 404)

    def test_flask_real_provider_missing_config_is_reported(self):
        from paper_trace.web.app import create_app

        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(
            os.environ,
            {"PAPER_TRACE_OPENAI_API_KEY": "", "PAPER_TRACE_OPENAI_BASE_URL": "", "PAPER_TRACE_OPENAI_MODEL": ""},
            clear=False,
        ):
            app = create_app(output_root=Path(tmp) / "web", config_path=Path(tmp) / ".paper_trace" / "config.json")
            client = app.test_client()
            response = client.post(
                "/analyze",
                data={"provider": "openai-compatible", "file": (self._bytes_file(SAMPLE_TEXT), "sample.txt")},
                content_type="multipart/form-data",
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn(b"PAPER_TRACE_OPENAI_API_KEY", response.data)
            self.assertFalse(list((Path(tmp) / "web").glob("*/citation_graph.json")))

    def test_flask_settings_save_mask_retain_and_clear_key(self):
        from paper_trace.config import load_config
        from paper_trace.web.app import create_app

        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".paper_trace" / "config.json"
            app = create_app(output_root=Path(tmp) / "web", config_path=config_path)
            client = app.test_client()

            index = client.get("/")
            self.assertEqual(index.status_code, 200)
            self.assertIn("settings-button".encode(), index.data)

            secret = "test-secret-abcdef"
            save = client.post(
                "/settings",
                data={
                    "provider": "openai-compatible",
                    "api_key": secret,
                    "base_url": "https://example.invalid/v1",
                    "model": "configured-model",
                    "stream": "on",
                    "timeout": "300",
                },
                follow_redirects=True,
            )
            self.assertEqual(save.status_code, 200)
            self.assertIn("te**************ef".encode(), save.data)
            self.assertNotIn(secret.encode(), save.data)
            stored = load_config(config_path)
            self.assertEqual(stored["providers"]["openai-compatible"]["api_key"], secret)
            self.assertEqual(stored["providers"]["openai-compatible"]["stream"], "true")
            self.assertEqual(stored["providers"]["openai-compatible"]["timeout"], "300")

            retain = client.post(
                "/settings",
                data={
                    "provider": "openai-compatible",
                    "api_key": "",
                    "base_url": "https://example.invalid/v2",
                    "model": "new-model",
                    "timeout": "120",
                },
                follow_redirects=True,
            )
            self.assertEqual(retain.status_code, 200)
            stored = load_config(config_path)
            self.assertEqual(stored["providers"]["openai-compatible"]["api_key"], secret)
            self.assertEqual(stored["providers"]["openai-compatible"]["model"], "new-model")
            self.assertEqual(stored["providers"]["openai-compatible"]["stream"], "false")
            self.assertEqual(stored["providers"]["openai-compatible"]["timeout"], "120")

            clear = client.post(
                "/settings",
                data={"provider": "openai-compatible", "clear_api_key": "on", "api_key": "", "base_url": "", "model": ""},
                follow_redirects=True,
            )
            self.assertEqual(clear.status_code, 200)
            stored = load_config(config_path)
            self.assertNotIn("api_key", stored["providers"]["openai-compatible"])

    @staticmethod
    def _bytes_file(text):
        from io import BytesIO

        return BytesIO(text.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
