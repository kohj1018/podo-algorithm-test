"""Provider-agnostic LLM access with JSON parsing and one retry on invalid output."""
from __future__ import annotations

import json
import re
from typing import Any, Callable

from . import cache, config

JSON_SYSTEM = (
    "You are a careful, literal information-extraction and evaluation engine. "
    "You follow instructions exactly, never invent facts, and output ONLY valid JSON "
    "with no extra text, no markdown, and no code fences."
)


class LLMError(Exception):
    pass


def _get_client():
    provider = config.get_provider()
    if provider is None:
        raise LLMError(config.provider_help())
    if provider == "anthropic":
        try:
            import anthropic
        except ImportError as e:
            raise LLMError("anthropic SDK not installed. Run: pip install anthropic") from e
        return provider, anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY), config.ANTHROPIC_MODEL
    try:
        from openai import OpenAI
    except ImportError as e:
        raise LLMError("openai SDK not installed. Run: pip install openai") from e
    return provider, OpenAI(api_key=config.OPENAI_API_KEY), config.OPENAI_MODEL


def call_text(system: str, user: str, max_tokens: int = 4096, temperature: float = 0.0) -> str:
    provider, client, model = _get_client()
    try:
        if provider == "anthropic":
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
            return "".join(parts).strip()
        return _openai_chat(client, model, system, user, max_tokens, temperature)
    except LLMError:
        raise
    except Exception as e:  # noqa: BLE001 - surface provider errors cleanly
        raise LLMError(f"LLM request failed ({provider}/{model}): {e}") from e


def _openai_chat(client, model: str, system: str, user: str,
                 max_tokens: int, temperature: float) -> str:
    """Chat Completions call that adapts to model-family parameter differences.

    Newer OpenAI models (o-series / gpt-5 family) reject ``max_tokens`` (they require
    ``max_completion_tokens``) and only accept the default temperature. We try the
    common form first and adapt based on the API error, without hardcoding a model list.
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    token_param = "max_tokens"
    send_temperature = temperature != 1.0
    send_seed = True
    last_err = None
    for _ in range(5):
        kwargs = {"model": model, "messages": messages, token_param: max_tokens}
        if send_temperature:
            kwargs["temperature"] = temperature
        if send_seed:
            kwargs["seed"] = config.LLM_SEED  # reproducibility hint (cache is the main mechanism)
        try:
            resp = client.chat.completions.create(**kwargs)
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:  # noqa: BLE001
            msg = str(e).lower()
            if token_param == "max_tokens" and "max_completion_tokens" in msg:
                token_param = "max_completion_tokens"
                last_err = e
                continue
            if send_seed and "seed" in msg:
                send_seed = False
                last_err = e
                continue
            if send_temperature and "temperature" in msg:
                send_temperature = False  # fall back to the model's default temperature
                last_err = e
                continue
            raise
    if last_err:
        raise last_err
    raise LLMError("OpenAI call could not be made with supported parameters")


def ping() -> str:
    """Minimal live call used by `doctor` to validate the API key + model.

    Returns the model id on success; raises LLMError on failure.
    """
    _provider, _client, model = _get_client()
    call_text(
        "You are a connectivity check. Reply with exactly: OK",
        "Reply with exactly: OK",
        max_tokens=256,
    )
    return model


def _extract_json(text: str) -> Any:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not starts:
        raise ValueError("no JSON object/array found in response")
    start = min(starts)
    # Greedy shrink from the end until a prefix parses.
    for end in range(len(text), start, -1):
        chunk = text[start:end]
        if chunk[-1] not in "}]":
            continue
        try:
            return json.loads(chunk)
        except Exception:
            continue
    raise ValueError("could not parse JSON from response")


def call_structured(
    system: str,
    user: str,
    validate: Callable[[Any], Any],
    max_tokens: int = 4096,
    temperature: float = 0.0,
    cache_label: str = None,
) -> Any:
    """Call the LLM, parse JSON, and run `validate`. Retry once on any failure.

    If `cache_label` is given, the raw JSON output is cached on disk keyed by the full
    rendered prompt + model + schema version, so repeat runs are reproducible.
    """
    model = config.OPENAI_MODEL if config.get_provider() == "openai" else config.ANTHROPIC_MODEL
    ckey = cache.make_key(model, system, user, config.SCHEMA_VERSION) if cache_label else None
    if cache_label:
        cached = cache.get(cache_label, ckey)
        if cached is not None:
            try:
                return validate(cached)
            except Exception:  # noqa: BLE001 - cached payload no longer matches schema
                cache.mark_stale(cache_label)

    suffix = "\n\nReturn ONLY a single valid JSON value. No prose, no markdown, no code fences."
    last_err = None
    for attempt in range(2):
        prompt = user + suffix
        if attempt == 1 and last_err:
            prompt += (
                f"\n\nYour previous response was rejected: {last_err}. "
                "Return ONLY valid JSON that matches the requested schema."
            )
        raw = call_text(system, prompt, max_tokens=max_tokens, temperature=temperature)
        try:
            obj = _extract_json(raw)
        except Exception as e:  # noqa: BLE001
            last_err = f"JSON parse error: {e}"
            continue
        try:
            result = validate(obj)
        except Exception as e:  # noqa: BLE001
            last_err = f"schema error: {e}"
            continue
        if cache_label:
            cache.put(cache_label, ckey, obj)
        return result
    raise LLMError(f"LLM did not return valid JSON after 2 attempts: {last_err}")
