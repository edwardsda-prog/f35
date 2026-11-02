"""End-to-End (E2E) test suite package for F-35 Fleet Sustainment Agent Platform.

Provides shared contract-invocation utilities supporting both synchronous (`def`)
and asynchronous (`async def`) ADK 2.0 tool implementations, as well as both
dictionary and Pydantic `BaseModel` return payloads.
"""

from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]


def invoke_contract(fn: Any, **kwargs: Any) -> Any:
    """Invoke a sync or async callable passing supported keyword arguments."""
    sig = inspect.signature(fn)
    accepts_var_kw = any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
    )
    call_kwargs = (
        kwargs
        if accepts_var_kw
        else {k: v for k, v in kwargs.items() if k in sig.parameters}
    )
    result = fn(**call_kwargs)
    if inspect.isawaitable(result):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(result)
        return asyncio.run(result)
    return result


def get_field(obj: Any, *candidate_keys: str, default: Any = None) -> Any:
    """Extract a field from a dict, Pydantic model, or nested payload."""
    if obj is None:
        return default
    for key in candidate_keys:
        if isinstance(obj, dict) and key in obj:
            return obj[key]
        if hasattr(obj, key):
            return getattr(obj, key)
    if hasattr(obj, "model_dump"):
        dumped = obj.model_dump()
        for key in candidate_keys:
            if key in dumped:
                return dumped[key]
    if isinstance(obj, dict):
        for sub_val in obj.values():
            if isinstance(sub_val, dict):
                for key in candidate_keys:
                    if key in sub_val:
                        return sub_val[key]
    return default


class E2EDummyTool:
    """Mock ADK BaseTool for callback testing."""

    def __init__(self, name: str) -> None:
        self.name = name


class E2EDummyPart:
    """Mock GenAI Part with text."""

    def __init__(self, text: str) -> None:
        self.text = text


class E2EDummyContent:
    """Mock GenAI Content with parts."""

    def __init__(self, text: str, role: str = "user") -> None:
        self.role = role
        self.parts = [E2EDummyPart(text)]


class E2EToolContext:
    """Mock ADK ToolContext with mutable session state and user content."""

    def __init__(
        self,
        state: dict[str, Any] | None = None,
        user_text: str = "",
        invocation_id: str = "e2e-inv-1",
    ) -> None:
        self.state: dict[str, Any] = state if state is not None else {}
        self.user_content = E2EDummyContent(user_text) if user_text else None
        self.invocation_id = invocation_id


class E2ECallbackContext:
    """Mock ADK CallbackContext for `before_model_callback`."""

    def __init__(
        self,
        state: dict[str, Any] | None = None,
        user_text: str = "",
        agent_name: str = "f35_sustainment_coordinator",
    ) -> None:
        self.state: dict[str, Any] = state if state is not None else {}
        self.user_content = E2EDummyContent(user_text) if user_text else None
        self.agent_name = agent_name


class E2ELlmRequest:
    """Mock ADK LlmRequest for `before_model_callback`."""

    def __init__(self, user_text: str) -> None:
        self.contents = [E2EDummyContent(user_text, role="user")]
        self.model = "gemini-3.8-flash"
