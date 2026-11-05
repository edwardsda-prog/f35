#!/usr/bin/env python3
"""Generate authoritative structured CSVs, declarative schema copies, PDFs, and Discovery Engine JSONL manifests."""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.seed_data.bq_seed_records import BQ_SEED_TABLES, SCHEMAS_DIR  # noqa: E402
from app.seed_data.jtd_corpus import GCS_DOCS_PREFIX, JTD_CORPUS_DOCUMENTS  # noqa: E402

OUTPUT_ROOT = PROJECT_ROOT / "data" / "synthetic_seed"
STRUCTURED_DIR = OUTPUT_ROOT / "structured"
STRUCTURED_TABLES_DIR = STRUCTURED_DIR / "tables"
STRUCTURED_SCHEMAS_DIR = STRUCTURED_DIR / "schemas"
UNSTRUCTURED_DIR = OUTPUT_ROOT / "unstructured"
UNSTRUCTURED_DOCS_DIR = UNSTRUCTURED_DIR / "docs"


def generate_structured_csvs() -> list[Path]:
    """Write the 6 active tables' CSVs and copy declarative JSON schemas to data/synthetic_seed/structured/."""
    if STRUCTURED_DIR.exists():
        shutil.rmtree(STRUCTURED_DIR)
    STRUCTURED_DIR.mkdir(parents=True, exist_ok=True)
    STRUCTURED_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    STRUCTURED_SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)

    generated_files: list[Path] = []

    for schema_path in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        dest_schema = STRUCTURED_SCHEMAS_DIR / schema_path.name
        shutil.copy2(schema_path, dest_schema)
        generated_files.append(dest_schema)

    for table_name, rows in BQ_SEED_TABLES.items():
        if not rows:
            continue
        fieldnames = list(rows[0].keys())
        for target_dir in (STRUCTURED_DIR, STRUCTURED_TABLES_DIR):
            csv_path = target_dir / f"{table_name}.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            generated_files.append(csv_path)

    return generated_files


def _render_pdf_document(pdf_path: Path, doc: dict[str, Any]) -> None:
    """Render a multi-section technical publication PDF using ReportLab."""
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "F35Title",
        parent=styles["Heading1"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0B2545"),
        spaceAfter=10,
    )
    meta_style = ParagraphStyle(
        "F35Meta",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#134074"),
    )
    body_style = ParagraphStyle(
        "F35Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceBefore=8,
        spaceAfter=8,
    )

    story: list[Any] = []
    story.append(
        Paragraph(
            f"UK DEFENCE / F-35 JOINT PROGRAM OFFICE — OFFICIAL TECHNICAL DATA ({doc['doc_id']})",
            meta_style,
        )
    )
    story.append(Paragraph(doc["title"], title_style))

    meta_rows = [
        ["Document ID", doc["doc_id"], "Chunk ID", doc["chunk_id"]],
        ["Publication Code", doc["publication_code"], "S1000D DMC", doc.get("s1000d_dmc", "N/A")],
        ["Subsystem Code", doc["system_subsystem_code"], "Service Branch", doc["service_branch_origin"]],
        [
            "Variants",
            ", ".join(doc["aircraft_variant_applicability"]),
            "BIT Fault Associated",
            str(doc["bit_fault_associated"]).lower(),
        ],
        ["Version Date", doc["document_version_date"], "GCS URI", doc["uri"]],
    ]
    meta_table = Table(meta_rows, colWidths=[95, 165, 95, 165])
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF4ED")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0B2545")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8DA9C4")),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>AUTHORITATIVE TECHNICAL CONTENT & VERBATIM EXTRACT:</b>", body_style))
    story.append(Paragraph(doc["content"], body_style))

    doc_template = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    doc_template.build(story)


def generate_unstructured_corpus() -> list[Path]:
    """Generate DOC-01, DOC-02, DOC-03, and DOC-09 PDFs/JSONL and Discovery Engine metadata JSONL manifests."""
    if UNSTRUCTURED_DIR.exists():
        shutil.rmtree(UNSTRUCTURED_DIR)
    UNSTRUCTURED_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []
    jtd_manifest_lines: list[str] = []
    narrative_manifest_lines: list[str] = []
    unified_manifest_lines: list[str] = []

    for doc in JTD_CORPUS_DOCUMENTS:
        doc_id = doc["doc_id"]
        filename = doc["filename"]
        file_path = UNSTRUCTURED_DOCS_DIR / filename

        # Always write a companion JSON chunk file for deterministic inspection
        json_chunk_path = UNSTRUCTURED_DOCS_DIR / f"{doc_id}_{doc['chunk_id']}.json"
        json_chunk_path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        generated.append(json_chunk_path)

        if filename.endswith(".jsonl"):
            # Write multi-record maintenance narrative log JSONL for DOC-02 + PDF companion
            log_entries = [
                {
                    "work_order_id": "WO-USMC-VMFA211-2024-0892",
                    "doc_id": doc["doc_id"],
                    "chunk_id": doc["chunk_id"],
                    "service_branch_origin": "USMC",
                    "squadron": "VMFA-211 (Wake Island Avengers)",
                    "aircraft_variant": "F-35B",
                    "system_subsystem_code": "53-30",
                    "bit_fault_associated": False,
                    "symptom_reported": "Stiff / sticky canopy forward latch mechanism on final closure; zero BIT fault codes.",
                    "root_cause": "Cured RTV silicon sealant debris migrated into forward canopy roller path.",
                    "corrective_action": doc["content"],
                },
                {
                    "work_order_id": "RAF-617SQN-707A-2025-0411",
                    "doc_id": doc["doc_id"],
                    "chunk_id": "DOC-LOG-RAF-617SQN-2025-0411",
                    "service_branch_origin": "RAF",
                    "squadron": "617 Squadron (RAF Marham)",
                    "aircraft_variant": "F-35B",
                    "system_subsystem_code": "53-30",
                    "bit_fault_associated": False,
                    "symptom_reported": "Physical binding on canopy forward catch during pre-flight lock check; no BIT fault.",
                    "root_cause": "Silicon sealant debris in forward roller track channel + dry pivot pin.",
                    "corrective_action": (
                        "Removed silicon sealant debris from roller track per USMC VMFA-211 cross-service advisory, "
                        "lubricated pivot pin with MIL-PRF-81322 per JTD Section 53-30-01, and verified 28.5 N*m "
                        "fastener torque with calibrated torque spanner."
                    ),
                },
            ]
            with file_path.open("w", encoding="utf-8") as jf:
                for entry in log_entries:
                    jf.write(json.dumps(entry) + "\n")
            generated.append(file_path)
            pdf_companion = UNSTRUCTURED_DOCS_DIR / doc.get("pdf_filename", f"{doc_id}.pdf")
            _render_pdf_document(pdf_companion, doc)
            generated.append(pdf_companion)
        else:
            _render_pdf_document(file_path, doc)
            generated.append(file_path)

        # Build Discovery Engine Document-schema metadata JSONL entry (dataSchema="document")
        pdf_doc_filename = doc.get("pdf_filename", doc["filename"])
        gcs_pdf_uri = f"{GCS_DOCS_PREFIX}/{pdf_doc_filename}"
        metadata_entry = {
            "id": doc["chunk_id"],
            "jsonData": json.dumps(
                {
                    "_id": doc["chunk_id"],
                    "id": doc["chunk_id"],
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
                    "text": doc["content"],
                }
            ),
            "content": {
                "mimeType": "application/pdf",
                "uri": gcs_pdf_uri,
            },
        }
        line_str = json.dumps(metadata_entry)
        unified_manifest_lines.append(line_str)
        if doc["datastore_target"] == "narrative":
            narrative_manifest_lines.append(line_str)
        else:
            jtd_manifest_lines.append(line_str)

    # Write jtd_metadata.jsonl, narrative_metadata.jsonl, and unified metadata.jsonl
    jtd_manifest_path = UNSTRUCTURED_DIR / "jtd_metadata.jsonl"
    jtd_manifest_path.write_text("\n".join(jtd_manifest_lines) + "\n", encoding="utf-8")
    generated.append(jtd_manifest_path)

    narrative_manifest_path = UNSTRUCTURED_DIR / "narrative_metadata.jsonl"
    narrative_manifest_path.write_text("\n".join(narrative_manifest_lines) + "\n", encoding="utf-8")
    generated.append(narrative_manifest_path)

    unified_manifest_path = UNSTRUCTURED_DIR / "metadata.jsonl"
    unified_manifest_path.write_text("\n".join(unified_manifest_lines) + "\n", encoding="utf-8")
    generated.append(unified_manifest_path)

    return generated


def main() -> None:
    structured_files = generate_structured_csvs()
    unstructured_files = generate_unstructured_corpus()
    print(f"Generated {len(structured_files)} structured files in {STRUCTURED_DIR}")
    print(f"Generated {len(unstructured_files)} unstructured files in {UNSTRUCTURED_DIR}")


if __name__ == "__main__":
    main()
