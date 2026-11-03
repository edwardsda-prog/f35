#!/usr/bin/env python3
"""Generate authoritative structured CSVs, declarative schema copies, PDFs, C-Scan PNG, and Discovery Engine JSONL manifests."""

from __future__ import annotations

import csv
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
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
UNSTRUCTURED_SAR_DIR = UNSTRUCTURED_DIR / "sar"


def generate_structured_csvs() -> list[Path]:
    """Write Tables 1-6 CSVs and copy declarative JSON schemas to data/synthetic_seed/structured/."""
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


def generate_cscan_png(png_path: Path) -> Path:
    """Render high-resolution annotated Phased-Array Ultrasonic C-Scan image for DOC-06."""
    png_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1024, 720
    img = Image.new("RGB", (width, height), color=(10, 18, 34))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # Header banner
    draw.rectangle([0, 0, width, 68], fill=(16, 36, 68))
    draw.text(
        (20, 14),
        "DOC-06 | PHASED-ARRAY ULTRASONIC C-SCAN NDI — TAIL ZM151 | STATION: FRAME 496 (PORT BULKHEAD)",
        fill=(235, 245, 255),
        font=font,
    )
    draw.text(
        (20, 38),
        "PROBE: 10 MHz 64-EL | CAD DATUM: FS 496.00, BL -42.50, WL 118.25 | FASTENER LOT: #8841-B (Ti-6Al-4V)",
        fill=(140, 210, 255),
        font=font,
    )

    # Ultrasonic C-scan attenuation grid canvas
    grid_x0, grid_y0, grid_x1, grid_y1 = 60, 100, 700, 560
    draw.rectangle([grid_x0, grid_y0, grid_x1, grid_y1], fill=(14, 48, 86), outline=(90, 160, 220), width=2)

    # Draw coordinate grid lines
    for gx in range(grid_x0, grid_x1 + 1, 40):
        draw.line([(gx, grid_y0), (gx, grid_y1)], fill=(25, 70, 115), width=1)
    for gy in range(grid_y0, grid_y1 + 1, 40):
        draw.line([(grid_x0, gy), (grid_x1, gy)], fill=(25, 70, 115), width=1)

    # Draw neighboring reference fastener holes (#12, #13, #15) — nominal green/cyan echoes
    nominal_holes = [
        ("Hole #12 (0.002 in)", 210, 316),
        ("Hole #13 (0.003 in)", 325, 316),
        ("Hole #15 (0.003 in)", 555, 316),
    ]
    for label, cx, cy in nominal_holes:
        draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(30, 180, 120), outline=(180, 255, 210), width=2)
        draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(10, 25, 45))
        draw.text((cx - 48, cy + 28), label, fill=(180, 240, 210), font=font)

    # Draw target Fastener Hole #14 with asymmetric shear elongation echo at [412, 288, 468, 344]
    cx14, cy14 = 440, 316
    for r, col in [(26, (220, 65, 40)), (21, (250, 140, 30)), (16, (255, 220, 60))]:
        draw.ellipse([cx14 - r - 4, cy14 - r, cx14 + r + 6, cy14 + r], fill=col)
    draw.ellipse([cx14 - 9, cy14 - 9, cx14 + 12, cy14 + 9], fill=(10, 18, 34))

    # Bounding box [412, 288, 468, 344]
    bbox = [412, 288, 468, 344]
    draw.rectangle(bbox, outline=(255, 50, 50), width=3)
    draw.text(
        (375, 266),
        "ROI [412, 288, 468, 344] — Fastener Hole #14",
        fill=(255, 110, 110),
        font=font,
    )
    draw.text(
        (368, 352),
        "Measured Shear Elongation: 0.012 in (< 0.015 in Limit)",
        fill=(255, 230, 110),
        font=font,
    )

    # Right-hand telemetry & metrology readout panel
    panel_x0, panel_y0, panel_x1, panel_y1 = 720, 100, 995, 560
    draw.rectangle([panel_x0, panel_y0, panel_x1, panel_y1], fill=(18, 32, 58), outline=(100, 160, 220), width=2)
    readout_lines = [
        "NDI METROLOGY READOUT",
        "------------------------------",
        "Tail Number: ZM151 (RAF Marham)",
        "Station: Frame 496",
        "Feature: Fastener Hole #14",
        "CAD FS: 496.00 | BL: -42.50",
        "CAD WL: 118.25",
        "Pixel BBox: [412,288,468,344]",
        "",
        "MEASURED ELONGATION:",
        "  0.012 in (0.305 mm)",
        "",
        "ALLOWABLE LIMIT (SRM 51-40):",
        "  0.015 in (0.381 mm)",
        "",
        "MARGIN TO CONDEMNATION:",
        "  +0.003 in (WITHIN LIMIT)",
        "",
        "FASTENER mBOM RECORD:",
        "  ID: MBOM-ZM151-F496-H14",
        "  Material: Titanium Ti-6Al-4V",
        "  Batch: Lot #8841-B",
        "  Install Hrs: 312.0 hrs",
        "  Fleet Affected: 14 Tails",
        "",
        "MANDATED ACTION:",
        "  JTD Task Card 53-11-00-280",
        "  SERVICEABLE_WITH_TORQUE_RECHECK",
    ]
    y_cursor = panel_y0 + 16
    for line in readout_lines:
        color = (255, 220, 90) if "0.012" in line or "0.015" in line or "SERVICEABLE" in line else (220, 235, 250)
        draw.text((panel_x0 + 12, y_cursor), line, fill=color, font=font)
        y_cursor += 15

    # Bottom A-scan waveform trace
    wave_y0, wave_y1 = 585, 695
    draw.rectangle([60, wave_y0, 995, wave_y1], fill=(12, 26, 48), outline=(70, 120, 180), width=1)
    draw.text((72, wave_y0 + 8), "A-SCAN RF ECHO GATE — HOLE #14 SHEAR INTERFACE (PEAK: 9.4G / 104.2% YIELD)", fill=(160, 215, 255), font=font)
    points: list[tuple[int, int]] = []
    for x in range(80, 975, 3):
        rel = (x - 440) / 28.0
        envelope = math.exp(-(rel * rel))
        y = int((wave_y0 + wave_y1) / 2 + 36 * envelope * math.sin((x - 80) * 0.35))
        points.append((x, y))
    if len(points) > 1:
        draw.line(points, fill=(80, 250, 160), width=2)

    img.save(png_path, format="PNG")
    return png_path


def generate_unstructured_corpus() -> list[Path]:
    """Generate DOC-01..DOC-09 PDFs/JSONL/PNG, SAR PDF, and Discovery Engine metadata JSONL manifests."""
    UNSTRUCTURED_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    UNSTRUCTURED_SAR_DIR.mkdir(parents=True, exist_ok=True)

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

        if filename.endswith(".png"):
            generate_cscan_png(file_path)
            generated.append(file_path)
            pdf_companion = UNSTRUCTURED_DOCS_DIR / doc.get("pdf_filename", f"{doc_id}.pdf")
            _render_pdf_document(pdf_companion, doc)
            generated.append(pdf_companion)
        elif filename.endswith(".jsonl"):
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

    # Also generate the signed/staged SAR PDF referenced in Table 6
    sar_pdf_path = UNSTRUCTURED_SAR_DIR / "SAR-20261102-ZM151.pdf"
    _render_pdf_document(sar_pdf_path, JTD_CORPUS_DOCUMENTS[7])  # DOC-08 SAR template & ZM151 data
    generated.append(sar_pdf_path)

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
