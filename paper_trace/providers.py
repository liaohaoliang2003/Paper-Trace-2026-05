from __future__ import annotations

import hashlib
import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from .config import resolve_openai_config, resolve_zhipu_config
from .schema import ALLOWED_INTENTS, DEFAULT_VISUAL_GROUPS, coarse_intent, validate_graph


OPENAI_DEFAULT_MODEL = "gpt-4o-mini"
ZHIPU_DEFAULT_MODEL = "glm-4-flash"
MAX_PROMPT_CHARS = 60000


class BaseProvider(ABC):
    @abstractmethod
    def extract_graph(self, text: str, source_name: str) -> Dict[str, Any]:
        """Extract a citation graph from paper text."""


class MockProvider(BaseProvider):
    """Deterministic no-network provider for CLI/Web workflow validation."""

    intents = ["background", "problem", "core-method", "dataset", "metric", "baseline", "result-evidence"]

    def extract_graph(self, text: str, source_name: str) -> Dict[str, Any]:
        title = _guess_title(text, source_name)
        sentences = _candidate_sentences(text)
        references = _references_from_text(text)
        citations = self._build_citations(sentences, references)
        entities = self._build_entities(citations)
        relations = self._build_relations(citations, entities)
        groups = self._build_groups(citations, entities)
        digest = hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()[:10]

        return {
            "schema_version": "0.1.0",
            "paper": {
                "paper_id": "target-paper",
                "title": title,
                "authors": [],
                "year": "unknown",
                "abstract": _guess_abstract(text),
                "core_contributions": [
                    "构建论文引用意图图谱工作流",
                    "输出结构化 citation_graph.json 与中心论文放射图",
                ],
            },
            "references": references,
            "citations": citations,
            "entities": entities,
            "relations": relations,
            "visual_groups": groups,
            "metadata": {
                "source_file": Path(source_name).name,
                "extraction_method": "mock",
                "coverage_notes": f"Deterministic mock extraction for workflow validation; text_sha1={digest}.",
            },
        }

    def _build_citations(self, sentences: List[str], references: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        citations: List[Dict[str, Any]] = []
        fallback_sentences = [
            "Prior work provides background for this paper [1].",
            "Existing approaches expose a problem that motivates this work [2].",
            "The method builds on a graph extraction technique [3].",
            "Experiments use a benchmark dataset [4].",
            "Evaluation follows a macro-F1 metric and compares a baseline [5].",
        ]
        pool = sentences or fallback_sentences
        while len(pool) < 5:
            pool.append(fallback_sentences[len(pool) % len(fallback_sentences)])

        for index, sentence in enumerate(pool[:7], start=1):
            intent = self.intents[(index - 1) % len(self.intents)]
            ref = references[(index - 1) % len(references)] if references else None
            citations.append(
                {
                    "citation_id": f"cit-{index:03d}",
                    "reference_id": ref["reference_id"] if ref else None,
                    "unmatched_reference": ref is None,
                    "marker": ref["marker"] if ref else f"[{index}]",
                    "section": _guess_section(sentence, index),
                    "citation_sentence": sentence,
                    "context": sentence,
                    "intent": intent,
                    "confidence": round(0.92 - min(index, 6) * 0.03, 2),
                    "evidence": f"MockProvider 根据句子内容将该引用归为 {intent}，用于验证完整工作流。",
                    "secondary_intents": [],
                    "entity_ids": [f"ent-{min(index, 3):03d}"],
                    "coarse_intent": coarse_intent(intent),
                    "show_on_map": True,
                    "notes": "mock extraction",
                }
            )
        return citations

    def _build_entities(self, citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "entity_id": "ent-001",
                "name": "citation intent map",
                "type": "method",
                "description": "将论文引用转换为结构化意图图谱的方法实体。",
                "source_citation_ids": [citations[0]["citation_id"]],
            },
            {
                "entity_id": "ent-002",
                "name": "benchmark dataset",
                "type": "dataset",
                "description": "用于验证抽取与可视化流程的数据集实体。",
                "source_citation_ids": [citations[min(3, len(citations) - 1)]["citation_id"]],
            },
            {
                "entity_id": "ent-003",
                "name": "macro-F1",
                "type": "metric",
                "description": "用于评价引用意图分类质量的指标实体。",
                "source_citation_ids": [citations[min(4, len(citations) - 1)]["citation_id"]],
            },
        ]

    def _build_relations(self, citations: List[Dict[str, Any]], entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        relation_types = ["cites-for", "uses-method", "uses-dataset"]
        return [
            {
                "relation_id": f"rel-{index:03d}",
                "source_id": "target-paper",
                "target_id": entity["entity_id"],
                "relation_type": relation_types[(index - 1) % len(relation_types)],
                "intent": citations[index - 1]["intent"],
                "evidence": f"目标论文通过 {entity['name']} 与相关引用建立关系。",
            }
            for index, entity in enumerate(entities, start=1)
        ]

    def _build_groups(self, citations: List[Dict[str, Any]], entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        groups = []
        for group in DEFAULT_VISUAL_GROUPS:
            node_ids = [c["citation_id"] for c in citations if c["intent"] in group["intent_filters"]]
            node_ids.extend(
                e["entity_id"]
                for e in entities
                if any(citation_id in node_ids for citation_id in e.get("source_citation_ids", []))
            )
            groups.append({**group, "node_ids": node_ids})
        return groups


class OpenAICompatibleProvider(BaseProvider):
    """Provider for OpenAI-compatible chat completions APIs."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        stream: bool | str | None = None,
        timeout: int | float | str | None = None,
        client: Any | None = None,
        config_path: Path | None = None,
    ) -> None:
        resolved = resolve_openai_config(api_key, base_url, model, stream, timeout, config_path)
        self.api_key = resolved["api_key"]
        if not self.api_key:
            raise ValueError(
                "Missing PAPER_TRACE_OPENAI_API_KEY for openai-compatible provider. "
                "Configure it with `C:\\ProgramData\\anaconda3\\Python.exe -m paper_trace config set`, "
                "Web settings, or an environment variable."
            )
        self.base_url = resolved["base_url"]
        self.model = resolved["model"] or OPENAI_DEFAULT_MODEL
        self.stream = bool(resolved["stream"])
        self.timeout = float(resolved["timeout"])
        self.client = client or self._create_client()

    def extract_graph(self, text: str, source_name: str) -> Dict[str, Any]:
        messages = build_llm_messages(text, source_name)
        kwargs: Dict[str, Any] = {"model": self.model, "messages": messages, "temperature": 0, "stream": self.stream}
        try:
            response = self.client.chat.completions.create(**kwargs)
            content = _stream_content(response) if self.stream else _message_content(response)
        except Exception as exc:
            raise RuntimeError(self._request_error_message(exc)) from exc
        if not content.strip():
            raise RuntimeError(
                "OpenAI-compatible provider returned an empty response. "
                "If stream=true is enabled, check whether the relay supports OpenAI Chat Completions streaming."
            )
        graph = normalize_llm_graph(parse_llm_json(content), source_name, text)
        validate_graph(graph)
        graph.setdefault("metadata", {})["extraction_method"] = "openai-compatible"
        graph["metadata"].setdefault("provider_model", self.model)
        return graph

    def _create_client(self) -> Any:
        try:
            from openai import OpenAI
        except Exception as exc:
            raise ValueError("openai-compatible provider requires optional dependency 'openai'. Install it first.") from exc
        kwargs = {"api_key": self.api_key, "timeout": self.timeout}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return OpenAI(**kwargs)

    def _request_error_message(self, exc: Exception) -> str:
        parts = [
            "OpenAI-compatible provider request failed",
            f"model={self.model}",
            f"base_url={self.base_url or 'default'}",
            f"stream={str(self.stream).lower()}",
            f"timeout={int(self.timeout) if self.timeout.is_integer() else self.timeout}",
            f"error_type={type(exc).__name__}",
            f"error={exc}",
        ]
        if exc.__cause__:
            parts.append(f"cause_type={type(exc.__cause__).__name__}")
            parts.append(f"cause={exc.__cause__}")
        message = "; ".join(parts)
        if not self.stream:
            message += "; non-stream request failed, try setting openai-compatible stream=true"
        return message


class ZhipuGLMProvider(BaseProvider):
    """Provider for the native ZhipuAI GLM SDK."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        client: Any | None = None,
        config_path: Path | None = None,
    ) -> None:
        resolved = resolve_zhipu_config(api_key, model, config_path)
        self.api_key = resolved["api_key"]
        if not self.api_key:
            raise ValueError(
                "Missing PAPER_TRACE_ZHIPU_API_KEY for zhipu-glm provider. "
                "Configure it with `python -m paper_trace config set`, Web settings, or an environment variable."
            )
        self.model = resolved["model"] or ZHIPU_DEFAULT_MODEL
        self.client = client or self._create_client()

    def extract_graph(self, text: str, source_name: str) -> Dict[str, Any]:
        messages = build_llm_messages(text, source_name)
        try:
            response = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0)
        except Exception as exc:
            raise RuntimeError(f"Zhipu GLM provider request failed: {exc}") from exc
        graph = normalize_llm_graph(parse_llm_json(_message_content(response)), source_name, text)
        validate_graph(graph)
        graph.setdefault("metadata", {})["extraction_method"] = "zhipu-glm"
        graph["metadata"].setdefault("provider_model", self.model)
        return graph

    def _create_client(self) -> Any:
        try:
            from zhipuai import ZhipuAI
        except Exception as exc:
            raise ValueError("zhipu-glm provider requires optional dependency 'zhipuai'. Install it first.") from exc
        return ZhipuAI(api_key=self.api_key)


def get_provider(name: str, config_path: Path | None = None) -> BaseProvider:
    provider_name = (name or "mock").strip().lower()
    if provider_name == "mock":
        return MockProvider()
    if provider_name == "openai-compatible":
        return OpenAICompatibleProvider(config_path=config_path)
    if provider_name == "zhipu-glm":
        return ZhipuGLMProvider(config_path=config_path)
    raise ValueError("Unknown provider. Supported providers: mock, openai-compatible, zhipu-glm")


def build_llm_messages(text: str, source_name: str) -> List[Dict[str, str]]:
    clipped_text = text[:MAX_PROMPT_CHARS]
    truncation_note = "" if len(text) <= MAX_PROMPT_CHARS else "\n注意：论文文本已截断，请优先覆盖可见文本中的引用。"
    return [
        {
            "role": "system",
            "content": (
                "你是论文引用意图、实体和关系抽取助手。必须只返回一个 JSON 对象，不要返回 Markdown、解释或多余文本。"
                "禁止编造不可从输入文本支持的论文信息。"
            ),
        },
        {
            "role": "user",
            "content": _build_user_prompt(clipped_text, source_name, truncation_note),
        },
    ]


def parse_llm_json(content: str) -> Dict[str, Any]:
    candidate = _strip_fenced_json(content).strip()
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM response is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("LLM response must be a JSON object")
    return data


def normalize_llm_graph(graph: Dict[str, Any], source_name: str, text: str) -> Dict[str, Any]:
    paper = graph.get("paper")
    if not isinstance(paper, dict):
        return graph
    if not str(paper.get("paper_id", "")).strip():
        paper["paper_id"] = "target-paper"
    if not str(paper.get("title", "")).strip():
        paper["title"] = _guess_title(text, source_name)
    if not isinstance(paper.get("authors"), list):
        paper["authors"] = []
    if not str(paper.get("year", "")).strip():
        paper["year"] = "unknown"
    if not str(paper.get("abstract", "")).strip():
        paper["abstract"] = _guess_abstract(text) or "unknown"
    if not isinstance(paper.get("core_contributions"), list):
        paper["core_contributions"] = []
    return graph


def _build_user_prompt(text: str, source_name: str, truncation_note: str) -> str:
    visual_groups = [
        {
            "group_id": group["group_id"],
            "label": group["label"],
            "intent_filters": group["intent_filters"],
            "color": group["color"],
        }
        for group in DEFAULT_VISUAL_GROUPS
    ]
    return f"""
请从下面论文文本中抽取引用意图、参考文献、实体和关系，输出 citation_graph.json。

硬性要求：
1. 只返回 JSON 对象，不要使用 Markdown 代码块。
2. intent 只能从以下标签中选择：{', '.join(ALLOWED_INTENTS)}。
3. 顶层字段必须包含 paper、references、citations、entities、relations、visual_groups、metadata。
4. paper 必须包含 paper_id、title、authors、year、abstract、core_contributions；paper.paper_id 固定为 target-paper。
5. 如果作者、年份、摘要或核心贡献无法从输入文本确认，authors 使用 []，year 使用 "unknown"，abstract 使用可见摘要或 "unknown"，core_contributions 使用 []。
6. 每条 citation 必须包含 citation_id、reference_id、unmatched_reference、marker、section、citation_sentence、context、intent、confidence、evidence、secondary_intents、entity_ids、coarse_intent、show_on_map、notes。
7. 每条 citation 必须有 evidence；如果无法匹配参考文献，reference_id 使用 null 且 unmatched_reference 使用 true。
8. confidence 是 0 到 1 之间的小数；show_on_map 是布尔值。
9. references 使用 reference_id、marker、title、authors、year、raw_reference。
10. entities 至少覆盖方法、数据集、指标、任务、问题、结果或组件中的可见实体。
11. relations 使用 relation_id、source_id、target_id、relation_type、intent、evidence。
12. citation_id 使用 cit-001 格式；reference_id 使用 ref-001 格式；entity_id 使用 ent-001 格式；relation_id 使用 rel-001 格式。

默认 visual_groups 可直接复用或按抽取结果补充 node_ids：
{json.dumps(visual_groups, ensure_ascii=False, indent=2)}

输入文件名：{Path(source_name).name}{truncation_note}

论文文本：
{text}
""".strip()


def _strip_fenced_json(content: str) -> str:
    stripped = (content or "").strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, re.S | re.I)
    if match:
        return match.group(1)
    return stripped


def _message_content(response: Any) -> str:
    try:
        return response.choices[0].message.content
    except Exception as exc:
        raise ValueError("LLM response does not contain choices[0].message.content") from exc


def _stream_content(response: Any) -> str:
    parts: List[str] = []
    for chunk in response:
        try:
            content = chunk.choices[0].delta.content
        except Exception:
            content = None
        if content:
            parts.append(content)
    return "".join(parts)


def _guess_title(text: str, source_name: str) -> str:
    for line in text.splitlines():
        clean = line.strip()
        if clean and len(clean) < 140 and not clean.lower().startswith(("abstract", "introduction")):
            return clean
    return Path(source_name).stem or "unknown"


def _guess_abstract(text: str) -> str:
    compact = " ".join(text.split())
    return compact[:500] if compact else "unknown"


def _candidate_sentences(text: str) -> List[str]:
    normalized = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?。！？])\s+", normalized)
    cited = [part.strip() for part in parts if re.search(r"\[[0-9,\-\s]+\]|\([A-Z][A-Za-z]+ et al\.,? \d{4}\)", part)]
    return cited[:12]


def _references_from_text(text: str) -> List[Dict[str, Any]]:
    references: List[Dict[str, Any]] = []
    seen = set()
    for match in re.finditer(r"^\s*\[([0-9]+)\]\s*(.+)$", text, re.M):
        number, raw = match.groups()
        if number in seen:
            continue
        seen.add(number)
        references.append(
            {
                "reference_id": f"ref-{int(number):03d}",
                "marker": f"[{number}]",
                "title": _title_from_reference(raw),
                "authors": [],
                "year": _year_from_text(raw),
                "raw_reference": raw.strip(),
            }
        )
    if references:
        return references
    return [
        {
            "reference_id": f"ref-{index:03d}",
            "marker": f"[{index}]",
            "title": f"Mock Reference {index}",
            "authors": [],
            "year": "unknown",
            "raw_reference": f"Mock Reference {index}",
        }
        for index in range(1, 8)
    ]


def _title_from_reference(raw: str) -> str:
    title = raw.strip().split(".")[0].strip()
    return title or "unknown"


def _year_from_text(raw: str) -> str:
    match = re.search(r"(19|20)\d{2}", raw)
    return match.group(0) if match else "unknown"


def _guess_section(sentence: str, index: int) -> str:
    lower = sentence.lower()
    if "experiment" in lower or "evaluate" in lower:
        return "Experiments"
    if "method" in lower or "build" in lower:
        return "Method"
    if index <= 2:
        return "Introduction"
    return "Related Work"
