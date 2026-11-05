"""Authoritative unstructured technical publications and maintenance log corpus (DOC-01, DOC-02, DOC-03, DOC-09)."""

from __future__ import annotations

from typing import Any

GCS_DOCS_PREFIX = "gs://antig-dave-f35-staging-europe-west1/unstructured/docs"
GCS_DOCS_HTTP_PREFIX = (
    "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/unstructured/docs"
)

# Cross-service UK (RAF/RN) <-> US (USAF/USMC) maintenance terminology crosswalk
SYNONYM_CROSSWALK_DICT: dict[str, list[str]] = {
    "catch": ["latch", "canopy forward latch", "locking pawl"],
    "latch": ["catch", "canopy forward catch", "locking pawl"],
    "spanner": ["wrench", "calibrated torque wrench"],
    "wrench": ["spanner", "calibrated torque spanner"],
    "binding": ["stiff", "sticky", "mechanical resistance", "roller track drag"],
    "stiff": ["binding", "sticky", "mechanical resistance"],
    "sticky": ["binding", "stiff", "sealant drag"],
    "gouge": ["score", "surface scratch", "fretting"],
    "score": ["gouge", "surface scratch", "fretting"],
}

JTD_CORPUS_DOCUMENTS: list[dict[str, Any]] = [
    {
        "doc_id": "DOC-01",
        "chunk_id": "DOC-JTD-53-30-01-CHUNK-014",
        "title": "JTD Section 53-30-01 — Canopy Mechanical Rigging & Pivot Pin Lubrication",
        "filename": "DOC-01_JTD_Section_53-30-01_Canopy_Rigging.pdf",
        "mime_type": "application/pdf",
        "publication_code": "JTD-F35-53-30-01",
        "s1000d_dmc": "DMC-F35A-53-30-01-00A-520A-A",
        "system_subsystem_code": "53-30",
        "aircraft_variant_applicability": ["F-35A", "F-35B", "F-35C"],
        "service_branch_origin": "RAF",
        "bit_fault_associated": False,
        "document_version_date": "2026-10-15",
        "datastore_target": "jtd",
        "uri": f"{GCS_DOCS_HTTP_PREFIX}/DOC-01_JTD_Section_53-30-01_Canopy_Rigging.pdf",
        "content": (
            "JOINT TECHNICAL DATA (JTD) SECTION 53-30-01 | S1000D DMC-F35A-53-30-01-00A-520A-A. "
            "SUBSYSTEM 53-30: CANOPY ACTUATION, FORWARD LATCH / CATCH MECHANISM & MECHANICAL RIGGING. "
            "APPLICABILITY: F-35A / F-35B / F-35C (RAF 617 Sqn, 207 Sqn, RN 809 NAS). "
            "SYMPTOM DIAGNOSTIC PROFILE: Physical mechanical binding, stiff or sticky movement on the "
            "canopy forward catch / latch mechanism during the final 2.0 inches of closure stroke with "
            "NO Built-In-Test (BIT) fault code flagged (BIT_FAULT_ASSOCIATED = FALSE). "
            "INSPECTION & RIGGING PROCEDURE: "
            "(1) Inspect forward canopy roller path and latch striker housing for foreign object debris (FOD) "
            "or cured environmental sealant intrusion prior to actuator removal. "
            "(2) Verify canopy forward catch / latch engagement clearance is within 0.040 in +/- 0.010 in "
            "(1.02 mm +/- 0.25 mm) using feeler gauge set. "
            "(3) Clean forward pivot pins and lubricate with MIL-PRF-81322 (NATO Code G-395) synthetic "
            "wide-temperature aircraft grease. "
            "(4) Re-torque forward latch bellcrank mounting bolts to 28.5 N*m (252 in-lbs) using a "
            "calibrated torque spanner / torque wrench."
        ),
    },
    {
        "doc_id": "DOC-02",
        "chunk_id": "DOC-LOG-USMC-VMFA211-2024-0892",
        "title": "5-Year Joint Force Maintenance Narrative Logs (2021-2026) — USMC Sister Squadron Canopy Sealant Debris Fix",
        "filename": "DOC-02_Joint_Force_Maintenance_Logs_2021_2026.jsonl",
        "pdf_filename": "DOC-02_Joint_Force_Maintenance_Logs_2021_2026.pdf",
        "mime_type": "application/pdf",
        "publication_code": "JTD-NARRATIVE-LOG-53-30",
        "s1000d_dmc": "LOG-JOINT-53-30-2021-2026",
        "system_subsystem_code": "53-30",
        "aircraft_variant_applicability": ["F-35A", "F-35B"],
        "service_branch_origin": "USMC",
        "bit_fault_associated": False,
        "document_version_date": "2026-09-20",
        "datastore_target": "narrative",
        "uri": f"{GCS_DOCS_HTTP_PREFIX}/DOC-02_Joint_Force_Maintenance_Logs_2021_2026.jsonl",
        "content": (
            "5-YEAR JOINT FORCE UNSTRUCTURED MAINTENANCE NARRATIVE LOGS (2021-2026) | WORK ORDER "
            "WO-USMC-VMFA211-2024-0892 & RAF-617SQN-707A-2025-0411. "
            "ORIGIN: USMC Sister Squadron VMFA-211 ('Wake Island Avengers') & RAF Marham 617 Squadron. "
            "SUBSYSTEM: 53-30 Canopy Forward Latch / Catch Track Assembly. "
            "BIT FAULT PRESENT: FALSE (No PHM/BIT fault code logged on Autonomic Logistics Information System). "
            "DISCREPANCY NARRATIVE: Pilot reported stiff / sticky canopy forward latch (UK: forward catch) "
            "with mechanical binding during final closure lock-down; no score or gouge visible on striker pin. "
            "ROOT CAUSE & CORRECTIVE ACTION: Inspection of the forward canopy roller path revealed cured "
            "RTV silicon sealant debris migrated into the port-side roller channel after high-altitude thermal "
            "cycling. Technicians removed the silicon sealant debris from the roller path using a non-metallic "
            "phenolic scraper, flushed the track with isopropyl alcohol (TT-I-735), lubricated the pivot pin "
            "per JTD Section 53-30-01 (MIL-PRF-81322), and verified smooth latch engagement with a calibrated "
            "torque wrench (UK: torque spanner) at 28.5 N*m. Total repair turnaround time: 45 minutes "
            "(saved 14-hour canopy actuator replacement)."
        ),
    },
    {
        "doc_id": "DOC-03",
        "chunk_id": "DOC-DEBRIEF-MARHAM-20261102-ZM151",
        "title": "RAF Marham Squadron Pilot Post-Flight Debrief Logbook (Tail ZM151 — 02 Nov 2026)",
        "filename": "DOC-03_Marham_Pilot_Debrief_Logbook_20261102.pdf",
        "mime_type": "application/pdf",
        "publication_code": "MOD-FORM-707A-ZM151-20261102",
        "s1000d_dmc": "MOD-707A-ZM151-20261102",
        "system_subsystem_code": "53-30",
        "aircraft_variant_applicability": ["F-35A", "F-35B"],
        "service_branch_origin": "RAF",
        "bit_fault_associated": False,
        "document_version_date": "2026-11-02",
        "datastore_target": "narrative",
        "uri": f"{GCS_DOCS_HTTP_PREFIX}/DOC-03_Marham_Pilot_Debrief_Logbook_20261102.pdf",
        "content": (
            "UK MOD FORM 707A — AIRCRAFT POST-FLIGHT DEBRIEF & MAINTENANCE WORK ORDER LOGBOOK. "
            "STATION: RAF Marham (617 Squadron 'Dambusters'). DATE: 2026-11-02. "
            "AIRCRAFT TAIL NUMBER: ZM151. PILOT: Flt Lt Henderson (Callsign: VIPER-1). "
            "PILOT DEBRIEF NARRATIVE: 'During pre-flight canopy lock-down and post-recovery manual release "
            "handle check on Tail ZM151, forward canopy locking catch (US: forward latch) exhibited "
            "noticeable mechanical stiffness during the final 2.0 inches of closure stroke. Zero Built-In-Test "
            "(BIT) fault codes were active on cockpit ICAW display (ruled out electrical limit-switch fault "
            "code 53-30-9914). Aft canopy fairing and port-side boundary-layer seal interface also experienced "
            "220.0 C Exhaust Gas Temperature (EGT) thermal exposure during vertical recovery; flight-line "
            "engineering requested JTD Section 53-30-01 mechanical rigging check and MAM Section 9-1 "
            "High-Temp RAM Sheet B restoration prior to morning sortie SRT-MAR-20261103-01.'"
        ),
    },
    {
        "doc_id": "DOC-09",
        "chunk_id": "DOC-MAM-SEC-9-1-RAM-CURE",
        "title": "Low Observable (LO) Maintenance Manual (MAM) Section 9-1 — High-Temp RAM Sheet 'B' & 4-Hour Heater Blanket Cure",
        "filename": "DOC-09_MAM_Section_9-1_HighTemp_RAM.pdf",
        "mime_type": "application/pdf",
        "publication_code": "MAM-F35-LO-9-1",
        "s1000d_dmc": "DMC-F35B-51-70-09-01A-720A-A",
        "system_subsystem_code": "53-30",
        "aircraft_variant_applicability": ["F-35A", "F-35B", "F-35C"],
        "service_branch_origin": "RN",
        "bit_fault_associated": False,
        "document_version_date": "2026-09-05",
        "datastore_target": "jtd",
        "uri": f"{GCS_DOCS_HTTP_PREFIX}/DOC-09_MAM_Section_9-1_HighTemp_RAM.pdf",
        "content": (
            "LOW OBSERVABLE (LO) MAINTENANCE MANUAL (MAM) SECTION 9-1 | S1000D DMC-F35B-51-70-09-01A-720A-A. "
            "SUBSYSTEM: OUTER MOLD LINE (OML) COATING & RADAR ABSORBENT MATERIAL (RAM) THERMAL RESTORATION. "
            "APPLICABILITY: F-35A / F-35B / F-35C (RAF Marham & RN 809 NAS HMS Queen Elizabeth / HMS Prince of Wales). "
            "HIGH-TEMPERATURE THERMAL ZONE RULE (220 C EXPOSURE): "
            "When performing OML panel access, canopy frame sealing, or fastener torque-recheck restoration "
            "(including Frame 496 and aft canopy fairing zones) subjected to boundary-layer aerodynamic "
            "heating or Exhaust Gas Temperature (EGT) thermal transients up to 220 C (428 F): "
            "(1) Standard ambient-cure LO conductive caulk is PROHIBITED due to thermal outgassing above 150 C. "
            "(2) Technicians MUST apply High-Temp RAM Sheet 'B' (NSN 8030-01-642-1190, fluorosilicone "
            "magnetic-loaded elastomer) over the fastener countersink and seam interface. "
            "(3) Execute a mandatory 4-hour heater blanket cure cycle at 175 C +/- 5 C (347 F) under "
            "22 inHg vacuum bag pressure before conducting portable Radar Cross-Section (RCS) reflectometer "
            "verification."
        ),
    },
]

JTD_DOCUMENTS_BY_ID: dict[str, dict[str, Any]] = {
    doc["doc_id"]: doc for doc in JTD_CORPUS_DOCUMENTS
}


def get_corpus_documents(datastore_target: str | None = None) -> list[dict[str, Any]]:
    """Return all authoritative corpus documents or filter by datastore_target ('jtd' or 'narrative')."""
    if datastore_target is None:
        return [dict(doc) for doc in JTD_CORPUS_DOCUMENTS]
    return [
        dict(doc)
        for doc in JTD_CORPUS_DOCUMENTS
        if doc.get("datastore_target") == datastore_target
    ]


def get_document_by_id(doc_id: str) -> dict[str, Any]:
    """Return a single corpus document by its doc_id (e.g., 'DOC-01'..'DOC-09')."""
    if doc_id not in JTD_DOCUMENTS_BY_ID:
        raise KeyError(f"Unknown corpus document ID: {doc_id}")
    return dict(JTD_DOCUMENTS_BY_ID[doc_id])
