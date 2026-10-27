#!/usr/bin/env python3
"""Normalize common model-native tool-call dialects for benchmark scoring."""

from __future__ import annotations

import ast
import json
import re
from typing import Any


TOOL_BLOCK_RE = re.compile(
    r"<tool_call\b[^>]*>(.*?)(?:</tool_call\s*>|</\s*>|$)", re.I | re.S
)
FUNCTION_RE = re.compile(
    r"<function(?:=|\s+name\s*=\s*['\"]?)([A-Za-z0-9_.:-]+)['\"]?\s*>",
    re.I | re.S,
)
PARAMETER_RE = re.compile(
    r"<parameter(?:=|\s+name\s*=\s*['\"]?)([A-Za-z0-9_.:-]+)['\"]?\s*>(.*?)</parameter\s*>",
    re.I | re.S,
)
GEMMA_STRING_RE = re.compile(r'<\|"\|>(.*?)<\|"\|>', re.S)
GEMMA_BARE_KEY_RE = re.compile(r"([,{]\s*)([A-Za-z_][A-Za-z0-9_.-]*)\s*:")
DSML_INVOKE_RE = re.compile(
    r'<｜DSML｜invoke\s+name=["\']([^"\']+)["\'][^>]*>(.*?)</｜DSML｜invoke>',
    re.I | re.S,
)
DSML_PARAMETER_RE = re.compile(
    r'<｜DSML｜parameter\s+name=["\']([^"\']+)["\']\s+string=["\'](true|false)["\']>(.*?)</｜DSML｜parameter>',
    re.I | re.S,
)
DEEPSEEK_R1_RE = re.compile(
    r"<｜tool▁call▁begin｜>function<｜tool▁sep｜>([^\n]+)\s*```json\s*(.*?)\s*```<｜tool▁call▁end｜>",
    re.I | re.S,
)
LFM_TOOL_CALL_RE = re.compile(
    r"<\|tool_call_start\|>(.*?)<\|tool_call_end\|>", re.I | re.S
)


def normalize_tool_response(text: str, message: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the canonical assistant text, calls, source format and warnings."""
    message = message if isinstance(message, dict) else {}
    content = strip_think_tags(text).strip()
    native_calls = message.get("tool_calls")
    if isinstance(native_calls, list) and native_calls:
        calls, warnings = normalize_calls(native_calls)
        return result(content, calls, "openai_tool_calls", warnings)
    function_call = message.get("function_call")
    if isinstance(function_call, dict):
        calls, warnings = normalize_calls([function_call])
        return result(content, calls, "openai_function_call", warnings)

    lfm = parse_lfm_calls(content)
    if lfm:
        calls, warnings = normalize_calls(lfm)
        return result("", calls, "lfm_tool_calls", warnings)

    tagged = parse_tagged_calls(content)
    if tagged:
        calls, warnings = normalize_calls(tagged)
        return result("", calls, "tagged_tool_call", warnings)

    mistral = parse_mistral_calls(content)
    if mistral:
        calls, warnings = normalize_calls(mistral)
        return result("", calls, "mistral_tool_calls", warnings)

    gemma = parse_gemma_calls(content)
    if gemma:
        calls, warnings = normalize_calls(gemma)
        return result("", calls, "gemma4_tool_call", warnings)

    deepseek = parse_deepseek_calls(content)
    if deepseek:
        calls, warnings = normalize_calls(deepseek)
        return result("", calls, "deepseek_tool_call", warnings)

    envelope = parse_json_envelope(content)
    if envelope is not None:
        return envelope
    repaired_envelope = parse_repaired_json_envelope(content)
    if repaired_envelope is not None:
        return repaired_envelope
    return result(content, [], "plain_text", [])


def canonical_tool_envelope(normalized: dict[str, Any]) -> dict[str, Any] | None:
    """Map a normalized response to the benchmark's historical single-call schema."""
    calls = normalized.get("tool_calls", [])
    text = str(normalized.get("assistant_text", ""))
    if calls:
        first = calls[0]
        return {
            "tool": first["name"],
            "args": first["arguments"],
            "final_answer": text,
        }
    if normalized.get("source_format") == "json_envelope":
        return {"tool": "none", "args": {}, "final_answer": text}
    return None


def canonical_agent_action(normalized: dict[str, Any]) -> dict[str, Any] | None:
    """Map any supported dialect to the v3 multi-call agent contract."""
    calls = normalized.get("tool_calls", [])
    text = str(normalized.get("assistant_text", "")).strip()
    if calls:
        return {
            "calls": [
                {
                    "id": str(call.get("id") or f"call_{index}"),
                    "tool": call["name"],
                    "args": call["arguments"],
                }
                for index, call in enumerate(calls, 1)
            ],
            "answer": text or None,
        }
    if text:
        return {"calls": [], "answer": text}
    return None


def result(
    assistant_text: str,
    calls: list[dict[str, Any]],
    source_format: str,
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "assistant_text": assistant_text,
        "tool_calls": calls,
        "source_format": source_format,
        "warnings": warnings,
    }


def normalize_calls(calls: list[Any]) -> tuple[list[dict[str, Any]], list[str]]:
    normalized: list[dict[str, Any]] = []
    warnings: list[str] = []
    for index, raw_call in enumerate(calls, 1):
        if not isinstance(raw_call, dict):
            warnings.append(f"tool call {index} is not an object")
            continue
        call = raw_call.get("function") if isinstance(raw_call.get("function"), dict) else raw_call
        name = str(call.get("name") or call.get("tool") or call.get("function_name") or "").strip()
        if not name or name.lower() in {"none", "null", "final_answer"}:
            warnings.append(f"tool call {index} has no usable name")
            continue
        arguments = call.get("arguments", call.get("args", call.get("parameters", call.get("input", {}))))
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError as exc:
                warnings.append(f"tool call {name} has invalid arguments: {exc}")
                continue
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            warnings.append(f"tool call {name} arguments are not an object")
            continue
        normalized.append(
            {
                "id": str(raw_call.get("id") or f"call_{index}"),
                "name": name,
                "arguments": arguments,
            }
        )
    return normalized, warnings


def parse_json_envelope(content: str) -> dict[str, Any] | None:
    raw = strip_fence(content.strip())
    if not (
        (raw.startswith("{") and raw.endswith("}"))
        or (raw.startswith("[") and raw.endswith("]"))
    ):
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    source_format = "json_envelope"
    if isinstance(payload, list):
        if len(payload) == 1 and isinstance(payload[0], dict):
            payload = payload[0]
            source_format = "json_singleton_list"
        elif payload and all(isinstance(item, dict) for item in payload):
            normalized_calls, warnings = normalize_calls(payload)
            if normalized_calls:
                return result("", normalized_calls, "json_call_list", warnings)
            return None
        else:
            return None
    if not isinstance(payload, dict):
        return None

    calls: list[Any] = []
    agent_calls = payload.get("calls")
    if isinstance(agent_calls, list):
        calls.extend(agent_calls)
        source_format = "agent_json_envelope" if source_format == "json_envelope" else source_format
    elif isinstance(agent_calls, dict):
        calls.append(agent_calls)
        source_format = "agent_json_envelope" if source_format == "json_envelope" else source_format
    if isinstance(payload.get("tool_calls"), list):
        calls.extend(payload["tool_calls"])
    if any(key in payload for key in ("tool", "name", "function_name", "function")):
        calls.append(payload)
    normalized_calls, warnings = normalize_calls(calls)
    assistant_text = first_string(payload, "answer", "final_answer", "content", "message")
    has_agent_contract = "calls" in payload or "answer" in payload
    if not normalized_calls and not assistant_text and not has_agent_contract:
        return None
    return result(assistant_text, normalized_calls, source_format, warnings)


def parse_repaired_json_envelope(content: str) -> dict[str, Any] | None:
    """Conservatively repair delimiter-only mistakes in an agent JSON envelope."""
    raw = strip_fence(content.strip())
    if not raw.startswith("{") or '"calls"' not in raw:
        return None
    candidate = re.sub(
        r"](?:\s*[}\]])+\s*,\s*\"answer\"\s*:",
        '],"answer":',
        raw,
        count=1,
    )
    candidate = balance_json_delimiters(candidate)
    if candidate == raw:
        return None
    repaired = parse_json_envelope(candidate)
    if repaired is None:
        return None
    repaired["source_format"] = "repaired_json_envelope"
    repaired["warnings"] = [
        *repaired.get("warnings", []),
        "repaired malformed agent JSON delimiters",
    ]
    return repaired


def balance_json_delimiters(raw: str) -> str:
    """Balance braces and brackets while leaving JSON strings untouched."""
    opening_for = {"}": "{", "]": "["}
    closing_for = {"{": "}", "[": "]"}
    stack: list[str] = []
    output: list[str] = []
    in_string = False
    escaped = False
    for char in raw:
        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            output.append(char)
            continue
        if char in closing_for:
            stack.append(char)
            output.append(char)
            continue
        if char in opening_for:
            while stack and stack[-1] != opening_for[char]:
                output.append(closing_for[stack.pop()])
            if stack:
                stack.pop()
                output.append(char)
            continue
        output.append(char)
    while stack:
        output.append(closing_for[stack.pop()])
    return "".join(output)


def parse_lfm_calls(content: str) -> list[dict[str, Any]]:
    """Parse LFM's Python-like list of calls without evaluating model output."""
    match = LFM_TOOL_CALL_RE.fullmatch(content.strip())
    if not match:
        return []
    try:
        expression = ast.parse(match.group(1).strip(), mode="eval").body
    except SyntaxError:
        return []
    nodes = expression.elts if isinstance(expression, (ast.List, ast.Tuple)) else [expression]
    calls: list[dict[str, Any]] = []
    for node in nodes:
        if not isinstance(node, ast.Call) or node.args:
            return []
        name = dotted_ast_name(node.func)
        if not name:
            return []
        arguments: dict[str, Any] = {}
        for keyword in node.keywords:
            if keyword.arg is None:
                return []
            try:
                arguments[keyword.arg] = ast.literal_eval(keyword.value)
            except (ValueError, TypeError):
                return []
        calls.append({"name": name, "arguments": arguments})
    return calls


def dotted_ast_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_ast_name(node.value)
        return f"{parent}.{node.attr}" if parent else ""
    return ""


def parse_tagged_calls(content: str) -> list[dict[str, Any]]:
    lowered = content.lower()
    if not (
        lowered.startswith("<tool_call")
        or lowered.startswith("<function_call")
        or lowered.startswith("<invoke")
        or "<｜tool" in content
    ):
        return []
    blocks = TOOL_BLOCK_RE.findall(content)
    if not blocks and lowered.startswith("<tool_call") and ">" in content:
        blocks = [content.split(">", 1)[1]]
    calls: list[dict[str, Any]] = []
    for block in blocks:
        envelope = parse_json_envelope(block.strip())
        if envelope and envelope["tool_calls"]:
            calls.extend(envelope["tool_calls"])
            continue
        function = FUNCTION_RE.search(block)
        if not function:
            continue
        remainder = block[function.end() :]
        arguments = extract_balanced_object(remainder)
        if arguments is not None:
            try:
                parsed_arguments = json.loads(arguments)
            except json.JSONDecodeError:
                parsed_arguments = None
        else:
            parsed_arguments = {
                key: value.strip() for key, value in PARAMETER_RE.findall(remainder)
            }
        if isinstance(parsed_arguments, dict):
            calls.append({"name": function.group(1), "arguments": parsed_arguments})
    return calls


def parse_mistral_calls(content: str) -> list[Any]:
    payload = ""
    for prefix in ("[TOOL_CALLS]", "[tool_calls]", "<function_call>"):
        if content.startswith(prefix):
            payload = content[len(prefix) :].strip().removesuffix("</function_call>").strip()
            break
    if not payload:
        return []
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else [parsed]


def parse_gemma_calls(content: str) -> list[dict[str, Any]]:
    remaining = content.strip()
    prefix = "<|tool_call>call:"
    if not remaining.startswith(prefix):
        return []
    calls: list[dict[str, Any]] = []
    while remaining.startswith(prefix):
        remaining = remaining[len(prefix) :]
        object_start = remaining.find("{")
        if object_start == 0:
            raw_object = extract_balanced_object(remaining)
            if raw_object is None:
                return []
            envelope = parse_json_envelope(raw_object)
            if envelope is None or not envelope["tool_calls"]:
                return []
            calls.extend(envelope["tool_calls"])
            remaining = remaining[len(raw_object) :].strip()
            if not remaining.startswith("<tool_call|>"):
                return []
            remaining = remaining[len("<tool_call|>") :].strip()
            continue
        if object_start < 0:
            return []
        name = remaining[:object_start].strip()
        raw_object = extract_balanced_object(remaining[object_start:])
        if raw_object is None:
            return []
        converted = GEMMA_STRING_RE.sub(
            lambda match: json.dumps(match.group(1), ensure_ascii=False), raw_object
        )
        converted = GEMMA_BARE_KEY_RE.sub(r'\1"\2":', converted)
        try:
            arguments = json.loads(converted)
        except json.JSONDecodeError:
            return []
        calls.append({"name": name, "arguments": arguments})
        remaining = remaining[object_start + len(raw_object) :].strip()
        if not remaining.startswith("<tool_call|>"):
            return []
        remaining = remaining[len("<tool_call|>") :].strip()
    return calls


def parse_deepseek_calls(content: str) -> list[dict[str, Any]]:
    stripped = content.strip()
    calls: list[dict[str, Any]] = []
    if stripped.startswith("<｜DSML｜tool_calls>"):
        for name, body in DSML_INVOKE_RE.findall(stripped):
            arguments: dict[str, Any] = {}
            for key, is_string, raw_value in DSML_PARAMETER_RE.findall(body):
                if is_string == "true":
                    arguments[key] = raw_value.strip()
                else:
                    try:
                        arguments[key] = json.loads(raw_value.strip())
                    except json.JSONDecodeError:
                        return []
            calls.append({"name": name, "arguments": arguments})
        return calls
    if stripped.startswith("<｜tool▁calls▁begin｜>"):
        for name, raw_arguments in DEEPSEEK_R1_RE.findall(stripped):
            try:
                arguments = json.loads(raw_arguments.strip())
            except json.JSONDecodeError:
                return []
            calls.append({"name": name.strip(), "arguments": arguments})
    return calls


def strip_think_tags(text: str) -> str:
    stripped = re.sub(r"<think(?:ing)?>.*?</think(?:ing)?>", "", text, flags=re.I | re.S)
    return re.sub(r"^\s*</think(?:ing)?>\s*", "", stripped, flags=re.I)


def strip_fence(text: str) -> str:
    match = re.fullmatch(r"```(?:json|tool_code)?\s*(.*?)\s*```", text, flags=re.I | re.S)
    return match.group(1).strip() if match else text


def first_string(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value.strip()
    return ""


def extract_balanced_object(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None
