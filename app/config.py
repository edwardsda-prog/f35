"""Platform configuration, regional invariants, and Gemini 3.8 Flash model factory.

Enforces REG-01 (EU / europe-west1 residency) and PERF-05 (Gemini Enterprise global
routing with string enum thinking_level).
"""

from __future__ import annotations

import os
from typing import Literal

from google.adk.models import Gemini
from google.genai import types

from app.seed_data import bq_seed_records as _bq_seed_records
from app.seed_data import jtd_corpus as _jtd_corpus

# Ensure environment defaults align with Enterprise SDK and EU residency rules
os.environ.setdefault("GOOGLE_GENAI_USE_ENTERPRISE", "True")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "antig-dave")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

# Core GCP Project & Regional Residency Constants (REG-01)
PROJECT_ID: str = "antig-dave"
PROJECT_NUMBER: str = "284046449012"
COMPUTE_REGION: str = "europe-west1"
GCP_REGION: str = "europe-west1"

# BigQuery Configuration (EU Multi-Region)
BQ_LOCATION: str = "EU"
BQ_DATASET: str = "ukd_f35_sustainment_demo"
BQ_DATASET_FQN: str = f"{PROJECT_ID}.{BQ_DATASET}"
BQ_TABLES: dict[str, str] = {
    "airframe_component_telemetry": "airframe_component_telemetry",
    "global_depot_inventory": "global_depot_inventory",
    "squadron_sortie_schedule": "squadron_sortie_schedule",
    "high_freq_strain_telemetry": "high_freq_strain_telemetry",
    "as_maintained_mbom_fasteners": "as_maintained_mbom_fasteners",
    "airworthiness_release_ledger": "airworthiness_release_ledger",
    "maintenance_work_orders": f"{BQ_DATASET_FQN}.maintenance_work_orders",
    "phm_bit_fault_events": f"{BQ_DATASET_FQN}.phm_bit_fault_events",
    "work_center_tooling_and_sqep": f"{BQ_DATASET_FQN}.work_center_tooling_and_sqep",
}

# Attach non-_ROWS table aliases onto bq_seed_records for cross-feature compatibility
for _tbl_key, _rows_attr in (
    ("AIRFRAME_COMPONENT_TELEMETRY", "AIRFRAME_COMPONENT_TELEMETRY_ROWS"),
    ("GLOBAL_DEPOT_INVENTORY", "GLOBAL_DEPOT_INVENTORY_ROWS"),
    ("SQUADRON_SORTIE_SCHEDULE", "SQUADRON_SORTIE_SCHEDULE_ROWS"),
    ("HIGH_FREQ_STRAIN_TELEMETRY", "HIGH_FREQ_STRAIN_TELEMETRY_ROWS"),
    ("AS_MAINTAINED_MBOM_FASTENERS", "AS_MAINTAINED_MBOM_FASTENERS_ROWS"),
    ("AIRWORTHINESS_RELEASE_LEDGER", "AIRWORTHINESS_RELEASE_LEDGER_ROWS"),
    ("MAINTENANCE_WORK_ORDERS", "MAINTENANCE_WORK_ORDERS_ROWS"),
    ("PHM_BIT_FAULT_EVENTS", "PHM_BIT_FAULT_EVENTS_ROWS"),
    ("WORK_CENTER_TOOLING_AND_SQEP", "WORK_CENTER_TOOLING_AND_SQEP_ROWS"),
):
    if not hasattr(_bq_seed_records, _tbl_key) and hasattr(_bq_seed_records, _rows_attr):
        setattr(_bq_seed_records, _tbl_key, getattr(_bq_seed_records, _rows_attr))

for _jtd_alias, _jtd_attr in (
    ("JTD_CORPUS_DOCS", "JTD_CORPUS_DOCUMENTS"),
    ("JTD_CORPUS_BY_ID", "JTD_DOCUMENTS_BY_ID"),
):
    if not hasattr(_jtd_corpus, _jtd_alias) and hasattr(_jtd_corpus, _jtd_attr):
        setattr(_jtd_corpus, _jtd_alias, getattr(_jtd_corpus, _jtd_attr))

# Discovery Engine & Gemini Enterprise Configuration (eu Multi-Region)
DE_LOCATION: str = "eu"
DISCOVERY_ENGINE_LOCATION: str = "eu"
DE_COLLECTION: str = "default_collection"
JTD_DATASTORE_ID: str = "ukd-f35-jtd-ietm-ds"
NARRATIVE_DATASTORE_ID: str = "ukd-f35-narrative-logs-ds"
GEMINI_APP_ID: str = "f35-support"
DISCOVERY_PAGE_SIZE: int = 15
DE_BASE_URL: str = "https://eu-discoveryengine.googleapis.com/v1alpha"

# Cloud Storage & Service Account Configuration
GCS_STAGING_BUCKET: str = "antig-dave-f35-staging-europe-west1"
GCS_EXPORTS_PREFIX: str = "exports"
GCS_BROWSER_BASE_URL: str = f"https://storage.cloud.google.com/{GCS_STAGING_BUCKET}"
RUNTIME_SERVICE_ACCOUNT: str = (
    "f35-sustainment-runtime-sa@antig-dave.iam.gserviceaccount.com"
)
USE_CLOUD_CLIENTS: bool = os.environ.get("USE_CLOUD_CLIENTS", "true").lower() in (
    "1",
    "true",
    "yes",
)

# Gemini 3.8 Flash Enterprise Global Endpoint Configuration (PERF-05)
GENAI_LOCATION: str = "global"
GEMINI_LOCATION: str = "global"
GENAI_USE_ENTERPRISE: bool = True
GEMINI_ENTERPRISE: bool = True

COORDINATOR_MODEL: str = "gemini-3.8-flash"
UC0_MODEL: str = "gemini-3.8-flash"
UC1_MODEL: str = "gemini-3.8-flash"
UC2_MODEL: str = "gemini-3.8-flash"
UC3_MODEL: str = "gemini-3.8-flash"

ThinkingLevelType = Literal["LOW", "MEDIUM", "HIGH"]


def get_generate_content_config(
    thinking_level: ThinkingLevelType = "LOW",
    temperature: float = 0.0,
    max_output_tokens: int | None = None,
) -> types.GenerateContentConfig:
    """Build GenerateContentConfig using the string enum thinking_level (PERF-05)."""
    resolved_level = thinking_level.upper()
    if resolved_level not in ("LOW", "MEDIUM", "HIGH"):
        raise ValueError(f"Invalid thinking_level: {thinking_level}")
    kwargs: dict[str, object] = {
        "temperature": temperature,
        "thinking_config": types.ThinkingConfig(
            thinking_level=types.ThinkingLevel(resolved_level)
        ),
    }
    if max_output_tokens is not None:
        kwargs["max_output_tokens"] = max_output_tokens
    return types.GenerateContentConfig(**kwargs)


def get_low_latency_config(
    max_output_tokens: int = 1536,
    thinking_level: ThinkingLevelType = "LOW",
    temperature: float = 0.0,
) -> types.GenerateContentConfig:
    """Return a low-latency GenerateContentConfig with bounded output tokens (PERF-05)."""
    return get_generate_content_config(
        thinking_level=thinking_level,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )


def get_gemini_model(
    model_name: str = COORDINATOR_MODEL,
    thinking_level: ThinkingLevelType = "LOW",
    temperature: float = 0.0,
) -> Gemini:
    """Instantiate an ADK 2.0 Gemini model with Enterprise global routing (PERF-05)."""
    _ = get_generate_content_config(
        thinking_level=thinking_level,
        temperature=temperature,
    )
    return Gemini(
        model=model_name,
        client_kwargs={
            "enterprise": GENAI_USE_ENTERPRISE,
            "project": PROJECT_ID,
            "location": GENAI_LOCATION,
        },
    )


def get_flash_model(
    model_name: str = UC0_MODEL,
    thinking_level: ThinkingLevelType = "LOW",
    temperature: float = 0.0,
) -> Gemini:
    """Return a pre-configured Gemini 3.8 Flash model on the Enterprise global endpoint."""
    return get_gemini_model(
        model_name=model_name,
        thinking_level=thinking_level,
        temperature=temperature,
    )
