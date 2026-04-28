from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


CONFIG_DIR = ".paper_trace"
CONFIG_FILE = "config.json"
PROVIDER_NAMES = ["openai-compatible", "zhipu-glm"]


class ConfigError(ValueError):
    pass


def default_config_path() -> Path:
    return Path.cwd() / CONFIG_DIR / CONFIG_FILE


def load_config(path: Path | None = None) -> Dict[str, Any]:
    config_path = Path(path) if path else default_config_path()
    if not config_path.exists():
        return {"providers": {}}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid Paper Trace config JSON at {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"Paper Trace config must be a JSON object: {config_path}")
    providers = data.setdefault("providers", {})
    if not isinstance(providers, dict):
        raise ConfigError("Paper Trace config field 'providers' must be an object")
    return data


def save_config(config: Dict[str, Any], path: Path | None = None) -> Path:
    config_path = Path(path) if path else default_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    return config_path


def get_provider_config(provider: str, path: Path | None = None) -> Dict[str, str]:
    config = load_config(path)
    raw = config.get("providers", {}).get(provider, {})
    if not isinstance(raw, dict):
        raise ConfigError(f"Provider config must be an object: {provider}")
    return {key: str(value) for key, value in raw.items() if value is not None and str(value) != ""}


def save_provider_config(provider: str, values: Dict[str, Any | None], path: Path | None = None) -> Path:
    _validate_provider(provider)
    config = load_config(path)
    providers = config.setdefault("providers", {})
    current = dict(providers.get(provider, {})) if isinstance(providers.get(provider, {}), dict) else {}
    for key, value in values.items():
        if value is None:
            continue
        if value == "":
            current.pop(key, None)
        else:
            current[key] = value
    providers[provider] = current
    return save_config(config, path)


def clear_provider_config(provider: str, path: Path | None = None) -> Path:
    _validate_provider(provider)
    config = load_config(path)
    config.setdefault("providers", {}).pop(provider, None)
    return save_config(config, path)


def list_masked_config(path: Path | None = None) -> Dict[str, Any]:
    config = load_config(path)
    masked = {"providers": {}}
    for provider, values in config.get("providers", {}).items():
        if not isinstance(values, dict):
            continue
        masked["providers"][provider] = mask_provider_config(values)
    return masked


def mask_provider_config(values: Dict[str, Any]) -> Dict[str, Any]:
    masked = dict(values)
    if masked.get("api_key"):
        masked["api_key"] = mask_secret(str(masked["api_key"]))
    return masked


def mask_secret(secret: str) -> str:
    if not secret:
        return ""
    if len(secret) <= 4:
        return "*" * len(secret)
    return f"{secret[:2]}{'*' * (len(secret) - 4)}{secret[-2:]}"


def resolve_openai_config(
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    stream: bool | str | None = None,
    timeout: int | float | str | None = None,
    config_path: Path | None = None,
) -> Dict[str, str | bool | float | None]:
    config = get_provider_config("openai-compatible", config_path)
    return {
        "api_key": api_key or config.get("api_key") or os.getenv("PAPER_TRACE_OPENAI_API_KEY"),
        "base_url": base_url or config.get("base_url") or os.getenv("PAPER_TRACE_OPENAI_BASE_URL"),
        "model": model or config.get("model") or os.getenv("PAPER_TRACE_OPENAI_MODEL"),
        "stream": _parse_bool(
            stream if stream is not None else config.get("stream") or os.getenv("PAPER_TRACE_OPENAI_STREAM"),
            default=True,
            field_name="openai-compatible stream",
        ),
        "timeout": _parse_timeout(
            timeout if timeout is not None else config.get("timeout") or os.getenv("PAPER_TRACE_OPENAI_TIMEOUT"),
            default=300,
        ),
    }


def resolve_zhipu_config(
    api_key: str | None = None,
    model: str | None = None,
    config_path: Path | None = None,
) -> Dict[str, str | None]:
    config = get_provider_config("zhipu-glm", config_path)
    return {
        "api_key": api_key or config.get("api_key") or os.getenv("PAPER_TRACE_ZHIPU_API_KEY"),
        "model": model or config.get("model") or os.getenv("PAPER_TRACE_ZHIPU_MODEL"),
    }


def _validate_provider(provider: str) -> None:
    if provider not in PROVIDER_NAMES:
        raise ConfigError(f"Unsupported configurable provider: {provider}")


def _parse_bool(value: bool | str | None, default: bool, field_name: str) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ConfigError(f"Invalid boolean value for {field_name}: {value}")


def _parse_timeout(value: int | float | str | None, default: float) -> float:
    if value is None or value == "":
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Invalid timeout value for openai-compatible provider: {value}") from exc
    if parsed <= 0:
        raise ConfigError("openai-compatible timeout must be greater than 0")
    return parsed
