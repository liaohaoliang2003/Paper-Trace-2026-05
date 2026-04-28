from __future__ import annotations

from typing import Any, Dict, Iterable, List


ALLOWED_INTENTS = [
    "background",
    "problem",
    "core-method",
    "supporting-method",
    "dataset",
    "metric",
    "baseline",
    "tool-resource",
    "theory",
    "result-evidence",
    "limitation",
    "future-work",
]

ALLOWED_INTENT_SET = set(ALLOWED_INTENTS)

COARSE_INTENT_MAPPING = {
    "background": "background",
    "problem": "background",
    "theory": "background",
    "future-work": "background",
    "core-method": "method",
    "supporting-method": "method",
    "tool-resource": "method",
    "dataset": "result",
    "metric": "result",
    "baseline": "result",
    "result-evidence": "result",
    "limitation": "result",
}

DEFAULT_VISUAL_GROUPS = [
    {
        "group_id": "problem-background",
        "label": "问题背景",
        "intent_filters": ["background", "problem", "theory"],
        "color": "#cf6f6f",
    },
    {
        "group_id": "method-core",
        "label": "核心方法",
        "intent_filters": ["core-method", "supporting-method", "tool-resource"],
        "color": "#ef6c2f",
    },
    {
        "group_id": "data-eval",
        "label": "数据与评估",
        "intent_filters": ["dataset", "metric"],
        "color": "#8a5cf6",
    },
    {
        "group_id": "baseline-result",
        "label": "基线与结果",
        "intent_filters": ["baseline", "result-evidence"],
        "color": "#d18a19",
    },
    {
        "group_id": "limits-future",
        "label": "局限与未来",
        "intent_filters": ["limitation", "future-work"],
        "color": "#4f9c56",
    },
]


class ValidationError(ValueError):
    """Raised when a citation graph does not satisfy the V1 schema."""

    def __init__(self, errors: Iterable[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def coarse_intent(intent: str) -> str:
    return COARSE_INTENT_MAPPING.get(intent, "background")


def validate_graph(graph: Dict[str, Any]) -> None:
    errors = collect_validation_errors(graph)
    if errors:
        raise ValidationError(errors)


def collect_validation_errors(graph: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not isinstance(graph, dict):
        return ["graph must be an object"]

    for key in ["paper", "references", "citations", "entities", "relations", "visual_groups", "metadata"]:
        if key not in graph:
            errors.append(f"missing top-level field: {key}")

    if not isinstance(graph.get("paper"), dict):
        errors.append("paper must be an object")
    else:
        for key in ["paper_id", "title", "authors", "year", "abstract", "core_contributions"]:
            if key not in graph["paper"]:
                errors.append(f"paper missing field: {key}")

    citations = graph.get("citations", [])
    if not isinstance(citations, list):
        errors.append("citations must be a list")
        citations = []
    for index, citation in enumerate(citations):
        prefix = f"citations[{index}]"
        if not isinstance(citation, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for key in ["citation_id", "marker", "section", "citation_sentence", "context", "intent", "confidence", "evidence"]:
            if key not in citation:
                errors.append(f"{prefix} missing field: {key}")
        intent = citation.get("intent")
        if intent not in ALLOWED_INTENT_SET:
            errors.append(f"{prefix} has invalid intent: {intent}")
        if not str(citation.get("evidence", "")).strip():
            errors.append(f"{prefix} missing non-empty evidence")
        if not (citation.get("reference_id") or citation.get("unmatched_reference") is True):
            errors.append(f"{prefix} needs reference_id or unmatched_reference=true")
        confidence = citation.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
            errors.append(f"{prefix} confidence must be between 0 and 1")
        for secondary in citation.get("secondary_intents", []) or []:
            if secondary not in ALLOWED_INTENT_SET:
                errors.append(f"{prefix} has invalid secondary intent: {secondary}")

    for list_key in ["references", "entities", "relations", "visual_groups"]:
        if list_key in graph and not isinstance(graph[list_key], list):
            errors.append(f"{list_key} must be a list")

    return errors


def validate_citation_edit(intent: str, confidence: float, evidence: str) -> List[str]:
    errors: List[str] = []
    if intent not in ALLOWED_INTENT_SET:
        errors.append(f"invalid intent: {intent}")
    if not 0 <= confidence <= 1:
        errors.append("confidence must be between 0 and 1")
    if not evidence.strip():
        errors.append("evidence is required")
    return errors
