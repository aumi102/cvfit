"""OpenAI Realtime short-lived client-secret issuance over direct HTTP."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings
from app.services.interview_realtime.errors import (
    RealtimeInterviewProviderUnavailable,
    RealtimeInterviewUnavailable,
)


OPENAI_REALTIME_CLIENT_SECRETS_URL = (
    "https://api.openai.com/v1/realtime/client_secrets"
)
CLIENT_SECRET_TTL_SECONDS = 60


@dataclass(frozen=True)
class RealtimeClientSecret:
    value: str
    expires_at: int
    provider_session_id: str | None
    model: str
    voice: str


def ensure_realtime_provider_configured(config: Settings) -> None:
    if not config.ENABLE_REALTIME_INTERVIEW:
        raise RealtimeInterviewUnavailable("realtime interview is disabled")
    if not (
        config.OPENAI_API_KEY.strip()
        and config.OPENAI_REALTIME_MODEL.strip()
        and config.OPENAI_REALTIME_VOICE.strip()
    ):
        raise RealtimeInterviewUnavailable(
            "realtime interview provider is not configured"
        )


def create_realtime_client_secret(
    config: Settings,
    *,
    user_id: uuid.UUID,
    instructions: str,
) -> RealtimeClientSecret:
    """Mint an ephemeral token without persisting or logging either credential."""
    ensure_realtime_provider_configured(config)

    model = config.OPENAI_REALTIME_MODEL.strip()
    voice = config.OPENAI_REALTIME_VOICE.strip()
    payload = {
        "expires_after": {
            "anchor": "created_at",
            "seconds": CLIENT_SECRET_TTL_SECONDS,
        },
        "session": {
            "type": "realtime",
            "model": model,
            "instructions": instructions,
            "output_modalities": ["audio"],
            "max_output_tokens": 512,
            "audio": {
                "input": {
                    "noise_reduction": {"type": "near_field"},
                    "transcription": {"model": "gpt-4o-mini-transcribe"},
                    "turn_detection": {
                        "type": "server_vad",
                        "create_response": True,
                        "interrupt_response": True,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 600,
                    },
                },
                "output": {"voice": voice},
            },
            "tools": [],
            "tool_choice": "none",
            "truncation": "auto",
        },
    }
    headers = {
        "Authorization": f"Bearer {config.OPENAI_API_KEY.strip()}",
        "Content-Type": "application/json",
        "OpenAI-Safety-Identifier": _safety_identifier(user_id),
    }

    try:
        with httpx.Client(
            timeout=httpx.Timeout(10.0, connect=5.0),
            follow_redirects=False,
        ) as client:
            response = client.post(
                OPENAI_REALTIME_CLIENT_SECRETS_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            provider_payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise RealtimeInterviewProviderUnavailable(
            "realtime provider is temporarily unavailable"
        ) from exc

    return _parse_provider_response(provider_payload, model=model, voice=voice)


def _parse_provider_response(
    payload: Any,
    *,
    model: str,
    voice: str,
) -> RealtimeClientSecret:
    if not isinstance(payload, dict):
        raise RealtimeInterviewProviderUnavailable(
            "realtime provider returned an invalid response"
        )

    value = payload.get("value")
    expires_at = payload.get("expires_at")
    if not isinstance(value, str) or not value:
        raise RealtimeInterviewProviderUnavailable(
            "realtime provider returned an invalid response"
        )
    if isinstance(expires_at, bool) or not isinstance(expires_at, (int, float)):
        raise RealtimeInterviewProviderUnavailable(
            "realtime provider returned an invalid response"
        )

    provider_session_id: str | None = None
    provider_session = payload.get("session")
    if isinstance(provider_session, dict):
        candidate = provider_session.get("id")
        if isinstance(candidate, str) and candidate:
            provider_session_id = candidate[:255]

    return RealtimeClientSecret(
        value=value,
        expires_at=int(expires_at),
        provider_session_id=provider_session_id,
        model=model,
        voice=voice,
    )


def _safety_identifier(user_id: uuid.UUID) -> str:
    return hashlib.sha256(f"cvfit:{user_id}".encode("utf-8")).hexdigest()
