"""Backend API & ADK 2.0 Domain Re-Exports (`packages/api`)."""

from __future__ import annotations

from app.agent import app, root_agent
from app.callbacks import fast_path_before_model_callback
from app.clients import (
    bq_client,
    get_access_token,
    get_async_http_client,
    get_bq_client,
    get_http_client,
)
from app.config import (
    BQ_DATASET,
    BQ_LOCATION,
    COMPUTE_REGION,
    DE_LOCATION,
    GENAI_LOCATION,
    GENAI_USE_ENTERPRISE,
    JTD_DATASTORE_ID,
    NARRATIVE_DATASTORE_ID,
    PROJECT_ID,
    get_gemini_model,
)

__all__ = [
    "BQ_DATASET",
    "BQ_LOCATION",
    "COMPUTE_REGION",
    "DE_LOCATION",
    "GENAI_LOCATION",
    "GENAI_USE_ENTERPRISE",
    "JTD_DATASTORE_ID",
    "NARRATIVE_DATASTORE_ID",
    "PROJECT_ID",
    "app",
    "bq_client",
    "fast_path_before_model_callback",
    "get_access_token",
    "get_async_http_client",
    "get_bq_client",
    "get_gemini_model",
    "get_http_client",
    "root_agent",
]
