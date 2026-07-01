"""Tests unitarios para las constantes PROMPT_VERSION y trace() con version."""
from __future__ import annotations

import pytest


_EXPECTED_VERSION_CONSTANTS = [
    "PROBLEM_PROMPT_VERSION",
    "SEGMENT_PROMPT_VERSION",
    "VALUEPROP_PROMPT_VERSION",
    "BUSINESS_MODEL_PROMPT_VERSION",
    "HYPOTHESES_PROMPT_VERSION",
    "RISK_PROMPT_VERSION",
    "PRIORITIZE_PROMPT_VERSION",
    "EXPERIMENT_DESIGN_PROMPT_VERSION",
    "METRICS_PROMPT_VERSION",
    "SUCCESS_CRITERIA_PROMPT_VERSION",
    "DECISION_PROMPT_VERSION",
    "ROADMAP_PROMPT_VERSION",
    "CRITIC_PROMPT_VERSION",
    "REPORT_PROMPT_VERSION",
]


def test_all_version_constants_defined():
    from app.agents import prompts
    for name in _EXPECTED_VERSION_CONSTANTS:
        assert hasattr(prompts, name), f"falta constante: {name}"
        assert isinstance(getattr(prompts, name), str), f"{name} debe ser str"


def test_version_format():
    from app.agents import prompts
    for name in _EXPECTED_VERSION_CONSTANTS:
        v = getattr(prompts, name)
        assert "_v" in v, f"versión sin patrón '_v': {name}={v!r}"


def test_trace_with_version_embeds_in_content():
    from app.agents.base import trace
    msg = trace("test_agent", "algún resultado", version="test_agent_v1")
    assert msg.content == "[test_agent_v1] algún resultado"
    assert msg.name == "test_agent"


def test_trace_without_version_backward_compatible():
    from app.agents.base import trace
    msg = trace("test_agent", "algún resultado")
    assert msg.content == "algún resultado"
    assert msg.name == "test_agent"


def test_trace_version_none_backward_compatible():
    from app.agents.base import trace
    msg = trace("test_agent", "algún resultado", version=None)
    assert msg.content == "algún resultado"
