"""Allowlist, validate, minimize, and hash browser-side realtime events."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.services.interview_realtime.errors import RealtimeInterviewValidationError


MAX_EVENT_PAYLOAD_BYTES = 16 * 1024

ALLOWED_EVENT_TYPES = frozenset(
    {
        "session_connected",
        "session_disconnected",
        "question_started",
        "question_completed",
        "user_transcript_completed",
        "assistant_transcript_completed",
        "session_error",
    }
)

_ALLOWED_FIELDS = {
    "session_connected": {"provider_session_id", "transport", "occurred_at"},
    "session_disconnected": {"reason", "code", "occurred_at"},
    "question_started": {"turn_index", "question_text", "question_type", "occurred_at"},
    "question_completed": {"turn_index", "question_text", "question_type", "occurred_at"},
    "user_transcript_completed": {
        "turn_index",
        "transcript",
        "provider_item_id",
        "occurred_at",
    },
    "assistant_transcript_completed": {
        "turn_index",
        "transcript",
        "transcript_kind",
        "question_type",
        "provider_item_id",
        "occurred_at",
    },
    "session_error": {"code", "message", "retryable", "occurred_at"},
}

_SENSITIVE_KEY_PARTS = (
    "authorization",
    "apikey",
    "clientsecret",
    "token",
    "sdp",
    "audio",
    "video",
    "rawmedia",
)
_SECRET_VALUE_PATTERN = re.compile(
    r"(?i)(?:\bbearer\s+[a-z0-9._~+/=-]{8,}|\bsk-[a-z0-9_-]{8,}|\bek_[a-z0-9_-]{8,})"
)
_BASE64_LIKE = re.compile(r"^[A-Za-z0-9+/=_-]+$")
_QUESTION_TYPES = {"technical", "behavioral", "project_deep_dive", "hr"}


@dataclass(frozen=True)
class RedactedRealtimeEvent:
    stored_payload: dict[str, Any]
    payload_hash: str
    turn_index: int | None = None
    turn_updates: dict[str, Any] = field(default_factory=dict)


def redact_realtime_event(
    event_type: str,
    payload: dict[str, Any],
    *,
    question_limit: int,
) -> RedactedRealtimeEvent:
    if event_type not in ALLOWED_EVENT_TYPES:
        raise RealtimeInterviewValidationError("unsupported realtime event type")
    if not isinstance(payload, dict):
        raise RealtimeInterviewValidationError("event payload must be an object")

    serialized = _canonical_json(payload)
    if len(serialized.encode("utf-8")) > MAX_EVENT_PAYLOAD_BYTES:
        raise RealtimeInterviewValidationError("event payload exceeds 16384 bytes")

    _reject_sensitive_or_nested_payload(payload)
    unknown = set(payload) - _ALLOWED_FIELDS[event_type]
    if unknown:
        raise RealtimeInterviewValidationError(
            f"unsupported payload fields for {event_type}: {', '.join(sorted(unknown))}"
        )

    payload_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    occurred_at = _optional_datetime(payload.get("occurred_at"))
    occurred_at_value = occurred_at.isoformat() if occurred_at is not None else None

    if event_type in {"question_started", "question_completed"}:
        turn_index = _turn_index(payload, question_limit)
        question_text = _required_text(payload, "question_text", 4000)
        question_type = _optional_choice(payload, "question_type", _QUESTION_TYPES)
        turn_updates: dict[str, Any] = {
            "question_text": question_text,
            "question_type": question_type,
        }
        if event_type == "question_started":
            turn_updates["started_at"] = occurred_at
        else:
            turn_updates["ended_at"] = occurred_at
        return RedactedRealtimeEvent(
            stored_payload=_without_none(
                {
                    "turn_index": turn_index,
                    "question_type": question_type,
                    "occurred_at": occurred_at_value,
                    "question_length": len(question_text),
                }
            ),
            payload_hash=payload_hash,
            turn_index=turn_index,
            turn_updates=turn_updates,
        )

    if event_type in {"user_transcript_completed", "assistant_transcript_completed"}:
        turn_index = _turn_index(payload, question_limit)
        transcript = _required_text(payload, "transcript", 12000)
        provider_item_id = _optional_text(payload, "provider_item_id", 255)
        transcript_kind = None
        if event_type == "user_transcript_completed":
            turn_updates = {"answer_transcript": transcript, "ended_at": occurred_at}
        else:
            transcript_kind = _optional_choice(
                payload, "transcript_kind", {"question", "followup"}
            ) or "followup"
            question_type = _optional_choice(payload, "question_type", _QUESTION_TYPES)
            if transcript_kind == "question":
                turn_updates = {
                    "question_text": transcript,
                    "question_type": question_type,
                    "started_at": occurred_at,
                }
            else:
                turn_updates = {"ai_followup_text": transcript}
        return RedactedRealtimeEvent(
            stored_payload=_without_none(
                {
                    "turn_index": turn_index,
                    "transcript_kind": transcript_kind,
                    "provider_item_id": provider_item_id,
                    "occurred_at": occurred_at_value,
                    "transcript_length": len(transcript),
                }
            ),
            payload_hash=payload_hash,
            turn_index=turn_index,
            turn_updates=turn_updates,
        )

    if event_type == "session_connected":
        provider_session_id = _optional_text(payload, "provider_session_id", 255)
        transport = _optional_choice(payload, "transport", {"webrtc"}) or "webrtc"
        return RedactedRealtimeEvent(
            stored_payload=_without_none(
                {
                    "provider_session_id": provider_session_id,
                    "transport": transport,
                    "occurred_at": occurred_at_value,
                }
            ),
            payload_hash=payload_hash,
        )

    if event_type == "session_disconnected":
        return RedactedRealtimeEvent(
            stored_payload=_without_none(
                {
                    "reason": _optional_text(payload, "reason", 500),
                    "code": _optional_text(payload, "code", 100),
                    "occurred_at": occurred_at_value,
                }
            ),
            payload_hash=payload_hash,
        )

    retryable = payload.get("retryable")
    if retryable is not None and not isinstance(retryable, bool):
        raise RealtimeInterviewValidationError("retryable must be a boolean")
    return RedactedRealtimeEvent(
        stored_payload=_without_none(
            {
                "code": _optional_text(payload, "code", 100),
                "message": _optional_text(payload, "message", 500),
                "retryable": retryable,
                "occurred_at": occurred_at_value,
            }
        ),
        payload_hash=payload_hash,
    )


def validate_persistable_text(value: str | None, *, field_name: str) -> None:
    if value is None:
        return
    if _SECRET_VALUE_PATTERN.search(value):
        raise RealtimeInterviewValidationError(
            f"{field_name} contains credential-like content"
        )
    compact = re.sub(r"\s+", "", value)
    if len(compact) > 1024 and _BASE64_LIKE.fullmatch(compact):
        raise RealtimeInterviewValidationError(
            f"{field_name} appears to contain encoded media or binary data"
        )


def _reject_sensitive_or_nested_payload(payload: dict[str, Any]) -> None:
    for key, value in payload.items():
        normalized_key = re.sub(r"[^a-z0-9]", "", str(key).lower())
        if any(part in normalized_key for part in _SENSITIVE_KEY_PARTS):
            raise RealtimeInterviewValidationError(
                f"sensitive payload field is not accepted: {key}"
            )
        if isinstance(value, (dict, list, bytes, bytearray)):
            raise RealtimeInterviewValidationError(
                f"nested or binary payload field is not accepted: {key}"
            )
        if isinstance(value, str):
            validate_persistable_text(value, field_name=str(key))


def _turn_index(payload: dict[str, Any], question_limit: int) -> int:
    value = payload.get("turn_index")
    if isinstance(value, bool) or not isinstance(value, int):
        raise RealtimeInterviewValidationError("turn_index must be an integer")
    if value < 0 or value >= question_limit:
        raise RealtimeInterviewValidationError(
            "turn_index must be within the session question limit"
        )
    return value


def _required_text(payload: dict[str, Any], key: str, limit: int) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RealtimeInterviewValidationError(f"{key} is required")
    if len(value) > limit:
        raise RealtimeInterviewValidationError(f"{key} exceeds {limit} characters")
    validate_persistable_text(value, field_name=key)
    return value.strip()


def _optional_text(payload: dict[str, Any], key: str, limit: int) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise RealtimeInterviewValidationError(f"{key} must be a string")
    if len(value) > limit:
        raise RealtimeInterviewValidationError(f"{key} exceeds {limit} characters")
    validate_persistable_text(value, field_name=key)
    return value.strip() or None


def _optional_choice(
    payload: dict[str, Any],
    key: str,
    choices: set[str],
) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or value not in choices:
        raise RealtimeInterviewValidationError(
            f"{key} must be one of: {', '.join(sorted(choices))}"
        )
    return value


def _optional_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > 64:
        raise RealtimeInterviewValidationError("occurred_at must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RealtimeInterviewValidationError(
            "occurred_at must be an ISO-8601 string"
        ) from exc
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def _without_none(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if item is not None}


def _canonical_json(payload: dict[str, Any]) -> str:
    try:
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise RealtimeInterviewValidationError(
            "event payload must contain JSON-compatible scalar values"
        ) from exc
