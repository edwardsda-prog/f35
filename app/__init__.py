"""F-35 Fleet Sustainment Agent Platform (`f35-sustainment-agent`) ADK 2.0 Runtime Package."""

from __future__ import annotations

from app import config as _config  # noqa: F401
from app.agent import app, root_agent

__all__ = ["app", "root_agent"]
