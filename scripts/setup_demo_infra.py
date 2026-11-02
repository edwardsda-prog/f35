#!/usr/bin/env python3
"""Provision and seed live EU Google Cloud infrastructure for F-35 Fleet Sustainment Agent Platform."""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import google.auth
import google.auth.transport.requests
import httpx
from google.api_core.exceptions import NotFound
from google.cloud import bigquery, storage

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.seed_data.bq_seed_records import BQ_SEED_TABLES, SCHEMAS_DIR  # noqa: E402
from app.seed_data.jtd_corpus import JTD_CORPUS_DOCUMENTS  # noqa: E402
from scripts.generate_synthetic_corpus import (  # noqa: E402
    OUTPUT_ROOT,
    generate_structured_csvs,
    generate_unstructured_corpus,
)

REQUIRED_APIS = [
    "bigquery.googleapis.com",
    "discoveryengine.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "iam.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
]

RUNTIME_SA_ROLES = [
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/discoveryengine.viewer",
    "roles/storage.objectViewer",
    "roles/aiplatform.user",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
]

EXPECTED_BQ_TABLES = (
    "airframe_component_telemetry",
    "global_depot_inventory",
    "squadron_sortie_schedule",
    "high_freq_strain_telemetry",
    "as_maintained_mbom_fasteners",
    "airworthiness_release_ledger",
)


def get_auth_headers(project_id: str) -> dict[str, str]:
    """Obtain bearer token from in-memory Application Default Credentials."""
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": project_id,
    }


def ensure_apis_enabled(project_id: str) -> None:
    """Enable required GCP APIs idempotently."""
    print(f"[1/6] Ensuring required APIs are enabled on project '{project_id}'...")
    cmd = ["gcloud", "services", "enable", *REQUIRED_APIS, f"--project={project_id}", "--quiet"]
    subprocess.run(cmd, check=True)
    print("  -> Required GCP APIs enabled.")


def ensure_service_account_and_iam(project_id: str, sa_name: str = "f35-sustainment-runtime-sa") -> str:
    """Create the runtime Service Account idempotently and bind required IAM roles."""
    sa_email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"
    print(f"[2/6] Ensuring Service Account '{sa_email}' and IAM bindings...")

    desc_cmd = [
        "gcloud",
        "iam",
        "service-accounts",
        "describe",
        sa_email,
        f"--project={project_id}",
        "--quiet",
    ]
    res = subprocess.run(desc_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        create_cmd = [
            "gcloud",
            "iam",
            "service-accounts",
            "create",
            sa_name,
            "--display-name=F-35 Sustainment Agent Runtime Service Account",
            f"--project={project_id}",
            "--quiet",
        ]
        subprocess.run(create_cmd, check=True)
        print(f"  -> Created service account: {sa_email}")
    else:
        print(f"  -> Service account already exists: {sa_email}")

    for role in RUNTIME_SA_ROLES:
        bind_cmd = [
            "gcloud",
            "projects",
            "add-iam-policy-binding",
            project_id,
            f"--member=serviceAccount:{sa_email}",
            f"--role={role}",
            "--condition=None",
            "--quiet",
        ]
        subprocess.run(bind_cmd, check=True, stdout=subprocess.DEVNULL)
    print(f"  -> Bound {len(RUNTIME_SA_ROLES)} IAM roles to {sa_email}")
    return sa_email


def ensure_gcs_bucket_and_upload(project_id: str, region: str, bucket_name: str) -> list[str]:
    """Create regional GCS bucket in europe-west1 idempotently and upload structured & unstructured corpus."""
    print(f"[3/6] Ensuring GCS bucket 'gs://{bucket_name}' in location '{region}'...")
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    if not bucket.exists():
        bucket = storage_client.create_bucket(bucket_or_name=bucket_name, location=region)
        print(f"  -> Created GCS bucket gs://{bucket_name} in {bucket.location}")
    else:
        bucket.reload()
        print(f"  -> GCS bucket gs://{bucket_name} already exists in {bucket.location}")

    if not OUTPUT_ROOT.exists():
        generate_structured_csvs()
        generate_unstructured_corpus()

    uploaded_uris: list[str] = []
    for file_path in sorted(OUTPUT_ROOT.rglob("*")):
        if file_path.is_file():
            rel_path = file_path.relative_to(OUTPUT_ROOT).as_posix()
            blob = bucket.blob(rel_path)
            blob.upload_from_filename(str(file_path))
            uploaded_uris.append(f"gs://{bucket_name}/{rel_path}")

    print(f"  -> Uploaded {len(uploaded_uris)} artifacts to gs://{bucket_name}/")
    return uploaded_uris


def ensure_bigquery_dataset_and_tables(
    project_id: str,
    bq_location: str,
    dataset_id: str,
) -> dict[str, int]:
    """Create BigQuery EU dataset and populate all 6 tables using declarative schemas."""
    print(f"[4/6] Provisioning BigQuery dataset '{project_id}.{dataset_id}' (location='{bq_location}')...")
    bq_client = bigquery.Client(project=project_id, location=bq_location)
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset_ref.location = bq_location
    dataset_ref.description = (
        "UK Defence F-35 Lightning II Fleet Sustainment Demo Dataset (EU Multi-Region). "
        "Contains UC1 telemetry/depot/sortie tables and UC3 strain exceedance/mBOM/airworthiness release tables."
    )
    dataset = bq_client.create_dataset(dataset_ref, exists_ok=True)
    print(f"  -> BigQuery dataset ready: {dataset.full_dataset_id} (location={dataset.location})")

    table_row_counts: dict[str, int] = {}

    for schema_file in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        schema_spec = json.loads(schema_file.read_text(encoding="utf-8"))
        table_name = schema_spec["table_name"]
        table_id = f"{project_id}.{dataset_id}.{table_name}"

        bq_fields = [
            bigquery.SchemaField(
                name=col["name"],
                field_type=col["type"],
                mode=col.get("mode", "NULLABLE"),
                description=col.get("description", ""),
            )
            for col in schema_spec["fields"]
        ]

        table_obj = bigquery.Table(table_id, schema=bq_fields)
        table_obj.description = schema_spec.get("description", "")

        partition_field = schema_spec.get("partition_field")
        if partition_field:
            table_obj.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition_field,
            )

        cluster_fields = schema_spec.get("cluster_fields")
        if cluster_fields:
            table_obj.clustering_fields = cluster_fields

        try:
            bq_client.get_table(table_id)
            bq_client.update_table(table_obj, ["schema", "description"])
        except NotFound:
            bq_client.create_table(table_obj)

        rows = BQ_SEED_TABLES[table_name]
        job_config = bigquery.LoadJobConfig(
            schema=bq_fields,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        load_job = bq_client.load_table_from_json(
            rows,
            table_id,
            job_config=job_config,
            location=bq_location,
        )
        load_job.result()

        # Re-apply table description after WRITE_TRUNCATE load job
        updated_table = bq_client.get_table(table_id)
        updated_table.description = schema_spec.get("description", "")
        bq_client.update_table(updated_table, ["description"])

        # Verify live row count via SQL query
        count_query = f"SELECT COUNT(*) AS row_count FROM `{table_id}`"
        query_rows = list(bq_client.query(count_query, location=bq_location).result())
        row_count = int(query_rows[0]["row_count"])
        if row_count <= 0:
            raise RuntimeError(f"Table {table_id} has 0 rows after seeding!")
        table_row_counts[table_name] = row_count
        print(f"  -> Seeded & verified table '{table_name}': {row_count} rows")

    return table_row_counts


def _build_inline_document_payload(doc: dict[str, Any], content_config: str) -> dict[str, Any]:
    """Construct Discovery Engine Document payload matching the datastore's contentConfig."""
    struct_payload = {
        "doc_id": doc["doc_id"],
        "chunk_id": doc["chunk_id"],
        "title": doc["title"],
        "publication_code": doc["publication_code"],
        "s1000d_dmc": doc.get("s1000d_dmc", ""),
        "system_subsystem_code": doc["system_subsystem_code"],
        "aircraft_variant_applicability": doc["aircraft_variant_applicability"],
        "service_branch_origin": doc["service_branch_origin"],
        "bit_fault_associated": doc["bit_fault_associated"],
        "document_version_date": doc["document_version_date"],
        "uri": doc["uri"],
        "content": doc["content"],
    }
    doc_payload: dict[str, Any] = {
        "id": doc["chunk_id"],
        "jsonData": json.dumps(struct_payload),
    }
    if content_config == "CONTENT_REQUIRED":
        full_text = (
            f"{doc['title']}\n"
            f"Document ID: {doc['doc_id']} | Chunk ID: {doc['chunk_id']} | "
            f"Publication: {doc['publication_code']} | Subsystem: {doc['system_subsystem_code']} | "
            f"Service Branch: {doc['service_branch_origin']} | BIT Fault: {doc['bit_fault_associated']}\n"
            f"URI: {doc['uri']}\n\n"
            f"{doc['content']}"
        )
        doc_payload["content"] = {
            "mimeType": "text/plain",
            "rawBytes": base64.b64encode(full_text.encode("utf-8")).decode("ascii"),
        }
    return doc_payload


def ensure_discovery_engine_datastores(
    project_id: str,
    de_location: str,
    bucket_name: str,
    jtd_datastore_id: str = "ukd-f35-jtd-ietm-ds",
    narrative_datastore_id: str = "ukd-f35-narrative-logs-ds",
    force_reimport: bool = False,
) -> dict[str, Any]:
    """Create Discovery Engine datastores in 'eu', import DOC-01..DOC-09, and verify live search."""
    print(f"[5/6] Provisioning Discovery Engine datastores in location='{de_location}'...")
    base_url = (
        f"https://{de_location}-discoveryengine.googleapis.com/v1alpha/"
        f"projects/{project_id}/locations/{de_location}/collections/default_collection"
    )
    headers = get_auth_headers(project_id)

    datastores_spec = [
        (
            jtd_datastore_id,
            "UK Defence F-35 JTD / IETM S1000D Technical Manuals (EU)",
            JTD_CORPUS_DOCUMENTS,
            f"gs://{bucket_name}/unstructured/metadata.jsonl",
        ),
        (
            narrative_datastore_id,
            "UK Defence F-35 5-Year Joint Force Maintenance Narrative Logs (EU)",
            JTD_CORPUS_DOCUMENTS,
            f"gs://{bucket_name}/unstructured/narrative_metadata.jsonl",
        ),
    ]

    verification_results: dict[str, Any] = {}

    with httpx.Client(timeout=60.0) as client:
        for ds_id, display_name, docs_to_index, _gcs_manifest_uri in datastores_spec:
            ds_url = f"{base_url}/dataStores/{ds_id}"
            resp = client.get(ds_url, headers=headers)
            if resp.status_code == 404:
                create_url = f"{base_url}/dataStores?dataStoreId={ds_id}"
                create_payload = {
                    "displayName": display_name,
                    "industryVertical": "GENERIC",
                    "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
                    "contentConfig": "CONTENT_REQUIRED",
                }
                c_resp = client.post(create_url, headers=headers, json=create_payload)
                if c_resp.status_code not in (200, 201, 409):
                    raise RuntimeError(
                        f"Failed creating datastore {ds_id}: {c_resp.status_code} {c_resp.text}"
                    )
                print(f"  -> Created Discovery Engine datastore: {ds_id}")
                time.sleep(3)
                resp = client.get(ds_url, headers=headers)
            else:
                print(f"  -> Discovery Engine datastore already exists: {ds_id}")

            ds_info = resp.json() if resp.status_code == 200 else {}
            content_config = ds_info.get("contentConfig", "CONTENT_REQUIRED")

            list_docs_url = f"{ds_url}/branches/0/documents"
            existing_resp = client.get(list_docs_url, headers=headers)
            existing_docs = (
                existing_resp.json().get("documents", [])
                if existing_resp.status_code == 200
                else []
            )
            existing_ids = {d.get("id") for d in existing_docs}
            expected_ids = {d["chunk_id"] for d in docs_to_index}
            missing_docs = [d for d in docs_to_index if d["chunk_id"] not in existing_ids]

            if force_reimport or missing_docs:
                target_docs = docs_to_index if force_reimport else missing_docs
                import_url = f"{ds_url}/branches/0/documents:import"
                inline_docs = [
                    _build_inline_document_payload(d, content_config) for d in target_docs
                ]
                inline_payload = {
                    "inlineSource": {"documents": inline_docs},
                    "reconciliationMode": "INCREMENTAL",
                }
                imp_resp = client.post(import_url, headers=headers, json=inline_payload)
                if imp_resp.status_code not in (200, 201):
                    raise RuntimeError(
                        f"inlineSource import failed for {ds_id}: "
                        f"{imp_resp.status_code} {imp_resp.text}"
                    )
                print(f"  -> Imported {len(inline_docs)} documents into {ds_id} via inlineSource")
            else:
                print(
                    f"  -> All {len(expected_ids)} corpus documents already present in {ds_id} "
                    f"(skipping re-import to preserve active search index)"
                )

        # Verify live REST search + document listing on both datastores
        search_queries = {
            jtd_datastore_id: "canopy forward latch catch rigging Frame 496 Task Card 53-11-00-280",
            narrative_datastore_id: "silicon sealant debris roller path Flt Lt Henderson 14:22 Zulu",
        }
        for ds_id, query_text in search_queries.items():
            search_url = f"{base_url}/dataStores/{ds_id}/servingConfigs/default_search:search"
            list_docs_url = f"{base_url}/dataStores/{ds_id}/branches/0/documents"

            search_hits = 0
            listed_docs_count = 0
            for _attempt in range(1, 5):
                headers = get_auth_headers(project_id)
                l_resp = client.get(list_docs_url, headers=headers)
                if l_resp.status_code == 200:
                    listed_docs = l_resp.json().get("documents", [])
                    listed_docs_count = len(listed_docs)

                s_payload = {
                    "query": query_text,
                    "pageSize": 15,
                    "contentSearchSpec": {
                        "snippetSpec": {"returnSnippet": True},
                    },
                }
                s_resp = client.post(search_url, headers=headers, json=s_payload)
                if s_resp.status_code == 200:
                    results = s_resp.json().get("results", [])
                    search_hits = len(results)
                    if search_hits > 0:
                        break
                time.sleep(2)

            verification_results[ds_id] = {
                "listed_documents_count": listed_docs_count,
                "live_search_hits": search_hits,
            }
            print(
                f"  -> Verified datastore '{ds_id}': "
                f"{listed_docs_count} documents stored, {search_hits} live search hits returned."
            )

    return verification_results


def ensure_gemini_enterprise_app(
    project_id: str,
    de_location: str,
    engine_id: str = "f35-support",
    datastore_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Create Gemini Enterprise App (Engine) 'f35-support' in locations/eu idempotently."""
    print(f"[6/6] Ensuring Gemini Enterprise App (Engine) '{engine_id}' in location='{de_location}'...")
    if datastore_ids is None:
        datastore_ids = ["ukd-f35-jtd-ietm-ds", "ukd-f35-narrative-logs-ds"]

    base_url = (
        f"https://{de_location}-discoveryengine.googleapis.com/v1alpha/"
        f"projects/{project_id}/locations/{de_location}/collections/default_collection"
    )
    headers = get_auth_headers(project_id)

    with httpx.Client(timeout=60.0) as client:
        engine_url = f"{base_url}/engines/{engine_id}"
        resp = client.get(engine_url, headers=headers)
        if resp.status_code == 200:
            print(f"  -> Gemini Enterprise Engine '{engine_id}' already exists.")
            return resp.json()

        create_url = f"{base_url}/engines?engineId={engine_id}"
        payload = {
            "displayName": "F35 Support",
            "solutionType": "SOLUTION_TYPE_SEARCH",
            "industryVertical": "GENERIC",
            "appType": "APP_TYPE_INTRANET",
            "dataStoreIds": datastore_ids,
            "searchEngineConfig": {
                "searchTier": "SEARCH_TIER_ENTERPRISE",
                "searchAddOns": ["SEARCH_ADD_ON_LLM"],
            },
        }
        c_resp = client.post(create_url, headers=headers, json=payload)
        if c_resp.status_code not in (200, 201, 409):
            raise RuntimeError(
                f"Failed creating Gemini Enterprise Engine '{engine_id}': "
                f"{c_resp.status_code} {c_resp.text}"
            )
        print(f"  -> Provisioned Gemini Enterprise Engine '{engine_id}' linked to {datastore_ids}")
        return c_resp.json()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Provision & seed live EU infrastructure for F-35 Sustainment Agent Platform."
    )
    parser.add_argument("--project", default="antig-dave", help="GCP Project ID")
    parser.add_argument("--region", default="europe-west1", help="Compute & GCS region")
    parser.add_argument("--bq-location", default="EU", help="BigQuery dataset location")
    parser.add_argument("--de-location", default="eu", help="Discovery Engine multi-region location")
    parser.add_argument(
        "--dataset", default="ukd_f35_sustainment_demo", help="BigQuery dataset name"
    )
    parser.add_argument(
        "--bucket",
        default="antig-dave-f35-staging-europe-west1",
        help="Regional GCS staging bucket name",
    )
    parser.add_argument(
        "--engine-id",
        default="f35-support",
        help="Gemini Enterprise App / Engine ID",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_apis_enabled(args.project)
    sa_email = ensure_service_account_and_iam(args.project)
    uploaded_uris = ensure_gcs_bucket_and_upload(args.project, args.region, args.bucket)
    bq_counts = ensure_bigquery_dataset_and_tables(args.project, args.bq_location, args.dataset)
    de_status = ensure_discovery_engine_datastores(args.project, args.de_location, args.bucket)
    engine_info = ensure_gemini_enterprise_app(args.project, args.de_location, args.engine_id)

    summary = {
        "project_id": args.project,
        "compute_region": args.region,
        "bq_location": args.bq_location,
        "de_location": args.de_location,
        "service_account": sa_email,
        "gcs_bucket": f"gs://{args.bucket}",
        "gcs_uploaded_count": len(uploaded_uris),
        "bigquery_dataset": f"{args.project}.{args.dataset}",
        "bigquery_table_row_counts": bq_counts,
        "discovery_engine_datastores": de_status,
        "gemini_enterprise_engine": engine_info.get("name", args.engine_id),
    }
    print("\n=== INFRASTRUCTURE PROVISIONING & VERIFICATION SUMMARY ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
