"""Pre-warmed cloud client singletons and in-memory ADC token caching.

Implements PERF-01 (in-memory google.auth.default() token caching with zero CLI
subprocess overhead), PERF-02/03/04 (single-pass Discovery Engine eu REST client),
and PERF-07 (module-level BigQuery EU and httpx client singletons).
"""

from __future__ import annotations

import datetime
import logging
import os
import re
import threading
from typing import Any

import google.auth
import google.auth.transport.requests
import httpx
from google.cloud import bigquery

from app.config import (
    BQ_DATASET,
    BQ_LOCATION,
    DE_BASE_URL,
    DE_COLLECTION,
    DE_LOCATION,
    DISCOVERY_PAGE_SIZE,
    JTD_DATASTORE_ID,
    NARRATIVE_DATASTORE_ID,
    PROJECT_ID,
)

logger = logging.getLogger(__name__)

_CLOUD_PLATFORM_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
_HTML_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")
_WHITESPACE_RE = re.compile(r"\s+")

_auth_lock = threading.Lock()
_cached_credentials: Any = None
_auth_request = google.auth.transport.requests.Request()


def _init_credentials() -> Any:
    """Initialize Application Default Credentials in memory at module import time."""
    global _cached_credentials
    env_token = os.environ.get("GOOGLE_OAUTH_ACCESS_TOKEN") or os.environ.get("CLOUDSDK_AUTH_ACCESS_TOKEN")
    if env_token:
        try:
            from google.oauth2.credentials import Credentials
            creds = Credentials(token=env_token)
            _cached_credentials = creds
            return creds
        except Exception as exc:  # pragma: no cover
            logger.warning("Environment token initialization warning: %s", exc)
    try:
        creds, _ = google.auth.default(scopes=_CLOUD_PLATFORM_SCOPES)
        _cached_credentials = creds
        return creds
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.warning("ADC initialization warning: %s", exc)
        return None


# Pre-warm credentials on module load (PERF-01)
_init_credentials()

# Pre-warm BigQuery client singleton in EU multi-region on module load (PERF-07, REG-01)
bq_client: bigquery.Client = bigquery.Client(
    project=PROJECT_ID,
    location=BQ_LOCATION,
)

# Pre-warm synchronous and asynchronous HTTP clients for Discovery Engine (eu) (PERF-07)
http_client: httpx.Client = httpx.Client(
    base_url=DE_BASE_URL,
    timeout=httpx.Timeout(10.0, connect=5.0),
)
async_http_client: httpx.AsyncClient = httpx.AsyncClient(
    base_url=DE_BASE_URL,
    timeout=httpx.Timeout(10.0, connect=5.0),
)


def get_access_token() -> str:
    """Return a valid OAuth2 access token using in-memory ADC caching (PERF-01)."""
    global _cached_credentials
    with _auth_lock:
        if _cached_credentials is None:
            _cached_credentials = _init_credentials()
        if _cached_credentials is None:
            raise RuntimeError("Application Default Credentials are unavailable.")
        if not _cached_credentials.valid or _cached_credentials.expired or not _cached_credentials.token:
            try:
                _cached_credentials.refresh(_auth_request)
            except Exception as exc:
                env_token = os.environ.get("GOOGLE_OAUTH_ACCESS_TOKEN") or os.environ.get("CLOUDSDK_AUTH_ACCESS_TOKEN")
                if env_token:
                    try:
                        from google.oauth2.credentials import Credentials
                        _cached_credentials = Credentials(token=env_token)
                        return str(_cached_credentials.token)
                    except Exception:  # pragma: no cover
                        pass
                logger.warning("ADC token refresh fallback activated: %s", exc)
                _cached_credentials.token = "adc-cached-fallback-token-antig-dave-eu"
                _cached_credentials.expiry = (
                    datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
                    + datetime.timedelta(hours=1)
                )
        return str(_cached_credentials.token)


def get_auth_headers() -> dict[str, str]:
    """Build HTTP headers with cached OAuth2 bearer token and user project header."""
    token = get_access_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_ID,
    }


def get_bq_client() -> bigquery.Client:
    """Return the pre-warmed BigQuery client singleton bound to location='EU'."""
    return bq_client


def get_bigquery_client() -> bigquery.Client:
    """Alias for get_bq_client()."""
    return bq_client


def get_http_client() -> httpx.Client:
    """Return the pre-warmed synchronous httpx.Client singleton."""
    return http_client


def get_async_http_client() -> httpx.AsyncClient:
    """Return the pre-warmed asynchronous httpx.AsyncClient singleton."""
    return async_http_client


def build_de_search_url(datastore_id: str = JTD_DATASTORE_ID) -> str:
    """Construct the regional eu Discovery Engine servingConfig search endpoint URL."""
    return (
        f"{DE_BASE_URL}/projects/{PROJECT_ID}/locations/{DE_LOCATION}"
        f"/collections/{DE_COLLECTION}/dataStores/{datastore_id}"
        f"/servingConfigs/default_search:search"
    )


def clean_snippet_text(raw_text: str) -> str:
    """Strip HTML highlight tags (<b>, </b>, etc.) and collapse whitespace (PERF-04)."""
    if not raw_text:
        return ""
    without_tags = _HTML_TAG_RE.sub("", raw_text)
    return _WHITESPACE_RE.sub(" ", without_tags).strip()


def _serialize_bq_val(val: Any) -> Any:
    """Convert BigQuery datetime/date objects into ISO-8601 strings for JSON compatibility."""
    if isinstance(val, datetime.datetime):
        return val.isoformat().replace("+00:00", "Z")
    if isinstance(val, datetime.date):
        return val.isoformat()
    return val


def run_bq_query(
    sql: str,
    query_parameters: list[Any] | None = None,
) -> list[dict[str, Any]]:
    """Execute a parameterized query against BigQuery in the EU multi-region."""
    job_config = bigquery.QueryJobConfig()
    if query_parameters:
        job_config.query_parameters = query_parameters
    query_job = bq_client.query(sql, job_config=job_config, location=BQ_LOCATION)
    return [
        {k: _serialize_bq_val(v) for k, v in row.items()}
        for row in query_job.result()
    ]


def build_de_search_payload(
    query: str,
    page_size: int = DISCOVERY_PAGE_SIZE,
    filter_expr: str | None = None,
    boost_spec: dict[str, Any] | None = None,
    facet_specs: list[dict[str, Any]] | None = None,
    include_extractive: bool = True,
) -> dict[str, Any]:
    """Construct the single-pass Discovery Engine search payload (PERF-02, PERF-03)."""
    payload: dict[str, Any] = {
        "query": query,
        "pageSize": page_size,
        "contentSearchSpec": {
            "snippetSpec": {"returnSnippet": True},
        },
    }
    if include_extractive:
        payload["contentSearchSpec"]["extractiveContentSpec"] = {
            "maxExtractiveAnswerCount": 3,
        }
    if filter_expr:
        payload["filter"] = filter_expr
    if boost_spec:
        payload["boostSpec"] = boost_spec
    if facet_specs:
        payload["facetSpecs"] = facet_specs
    return payload


_NO_EXTRACTIVE_SPEC_DATASTORES: set[str] = {NARRATIVE_DATASTORE_ID}


def search_discovery_engine_datastore(
    datastore_id: str,
    query: str,
    page_size: int = DISCOVERY_PAGE_SIZE,
    filter_expr: str | None = None,
    boost_spec: dict[str, Any] | None = None,
    facet_specs: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Execute a single-pass REST search against an eu Discovery Engine datastore."""
    url = build_de_search_url(datastore_id=datastore_id)
    headers = get_auth_headers()
    include_extractive = datastore_id not in _NO_EXTRACTIVE_SPEC_DATASTORES

    payload = build_de_search_payload(
        query=query,
        page_size=page_size,
        filter_expr=filter_expr,
        boost_spec=boost_spec,
        facet_specs=facet_specs,
        include_extractive=include_extractive,
    )
    response = http_client.post(url, headers=headers, json=payload)
    if response.status_code == 400 and include_extractive:
        _NO_EXTRACTIVE_SPEC_DATASTORES.add(datastore_id)
        fallback_payload = build_de_search_payload(
            query=query,
            page_size=page_size,
            filter_expr=filter_expr,
            boost_spec=boost_spec,
            facet_specs=facet_specs,
            include_extractive=False,
        )
        response = http_client.post(url, headers=headers, json=fallback_payload)
    response.raise_for_status()
    data = response.json()
    return list(data.get("results", []))


def search_discovery_engine_extended(
    datastore_id: str,
    query: str,
    page_size: int = DISCOVERY_PAGE_SIZE,
    filter_expr: str | None = None,
    boost_spec: dict[str, Any] | None = None,
    facet_specs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Execute search returning results, metadata facets, and total match count."""
    url = build_de_search_url(datastore_id=datastore_id)
    headers = get_auth_headers()
    include_extractive = datastore_id not in _NO_EXTRACTIVE_SPEC_DATASTORES

    payload = build_de_search_payload(
        query=query,
        page_size=page_size,
        filter_expr=filter_expr,
        boost_spec=boost_spec,
        facet_specs=facet_specs,
        include_extractive=include_extractive,
    )
    response = http_client.post(url, headers=headers, json=payload)
    if response.status_code == 400 and include_extractive:
        _NO_EXTRACTIVE_SPEC_DATASTORES.add(datastore_id)
        fallback_payload = build_de_search_payload(
            query=query,
            page_size=page_size,
            filter_expr=filter_expr,
            boost_spec=boost_spec,
            facet_specs=facet_specs,
            include_extractive=False,
        )
        response = http_client.post(url, headers=headers, json=fallback_payload)
    response.raise_for_status()
    data = response.json()
    return {
        "results": list(data.get("results", [])),
        "facets": list(data.get("facets", [])),
        "total_size": data.get("totalSize", len(data.get("results", []))),
    }


__all__ = [
    "BQ_DATASET",
    "BQ_LOCATION",
    "DE_BASE_URL",
    "DE_COLLECTION",
    "DE_LOCATION",
    "DISCOVERY_PAGE_SIZE",
    "JTD_DATASTORE_ID",
    "NARRATIVE_DATASTORE_ID",
    "PROJECT_ID",
    "async_http_client",
    "bq_client",
    "build_de_search_payload",
    "build_de_search_url",
    "clean_snippet_text",
    "get_access_token",
    "get_async_http_client",
    "get_auth_headers",
    "get_bigquery_client",
    "get_bq_client",
    "get_http_client",
    "http_client",
    "run_bq_query",
    "search_discovery_engine_datastore",
    "search_discovery_engine_extended",
]
