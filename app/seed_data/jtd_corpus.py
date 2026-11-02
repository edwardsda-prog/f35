"""Authoritative unstructured technical publications and maintenance log corpus (DOC-01..DOC-09)."""

from __future__ import annotations

from typing import Any

GCS_DOCS_PREFIX = "gs://antig-dave-f35-staging-europe-west1/unstructured/docs"

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
        "uri": f"{GCS_DOCS_PREFIX}/DOC-01_JTD_Section_53-30-01_Canopy_Rigging.pdf",
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
        "uri": f"{GCS_DOCS_PREFIX}/DOC-02_Joint_Force_Maintenance_Logs_2021_2026.jsonl",
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
        "system_subsystem_code": "53-11",
        "aircraft_variant_applicability": ["F-35A", "F-35B"],
        "service_branch_origin": "RAF",
        "bit_fault_associated": False,
        "document_version_date": "2026-11-02",
        "datastore_target": "narrative",
        "uri": f"{GCS_DOCS_PREFIX}/DOC-03_Marham_Pilot_Debrief_Logbook_20261102.pdf",
        "content": (
            "UK MOD FORM 707A — AIRCRAFT POST-FLIGHT DEBRIEF & MAINTENANCE WORK ORDER LOGBOOK. "
            "STATION: RAF Marham (617 Squadron 'Dambusters'). DATE: 2026-11-02. "
            "AIRCRAFT TAIL NUMBER: ZM151. PILOT: Flt Lt Henderson (Callsign: VIPER-1). "
            "PILOT DEBRIEF NARRATIVE: 'Experienced severe airframe shudder at roughly 14:22 Zulu during "
            "defensive split-S maneuver in North Sea ACMI Area 3. Entry was transonic at Mach 1.3 with "
            "an asymmetric rolling pull peaking at 9.4 G and concurrent Exhaust Gas Temperature (EGT) "
            "thermal spike to 220.0 C across the aft/port fuselage boundary layer. Acoustic thump felt "
            "through port wing root (Frame 496 Wing Carry-Through Bulkhead). Aircraft recovered uneventfully "
            "to RAF Marham at 14:58Z; requesting immediate ASIP structural integrity assessment prior to "
            "scheduled 06:30Z morning sortie SRT-MAR-20261103-01.'"
        ),
    },
    {
        "doc_id": "DOC-04",
        "chunk_id": "DOC-JTD-53-11-00-TASK-280",
        "title": "JTD Rule 53-11-00 & Task Card 53-11-00-280 — Wing Carry-Through Bulkhead Over-G Inspection & Fastener Torque-Recheck",
        "filename": "DOC-04_JTD_Rule_53-11-00_Task_Card_280.pdf",
        "mime_type": "application/pdf",
        "publication_code": "JTD-F35-53-11-00",
        "s1000d_dmc": "DMC-F35-53-11-00-280A-A",
        "system_subsystem_code": "53-11",
        "aircraft_variant_applicability": ["F-35A", "F-35B", "F-35C"],
        "service_branch_origin": "RAF",
        "bit_fault_associated": False,
        "document_version_date": "2026-10-01",
        "datastore_target": "jtd",
        "uri": f"{GCS_DOCS_PREFIX}/DOC-04_JTD_Rule_53-11-00_Task_Card_280.pdf",
        "content": (
            "JOINT TECHNICAL DATA (JTD) RULE 53-11-00 & MANDATORY TASK CARD 53-11-00-280 | "
            "S1000D DMC-F35-53-11-00-280A-A. "
            "SUBSYSTEM 53-11: PRIMARY WING CARRY-THROUGH BULKHEAD (FRAME 496) STRUCTURAL EXCEEDANCE PROTOCOL. "
            "RULE 53-11-00 MANDATORY NDI TRIGGER: Whenever deterministic Rainflow cycle counting and "
            "Palmgren-Miner cumulative damage analysis on 200 Hz MIL-STD-1553 / ARINC 429 strain telemetry "
            "indicates structural stress exceeds 100.0% of Design Yield Strength (e.g., 104.2% at Frame 496), "
            "a mandatory Class-A Phased-Array Ultrasonic C-Scan Non-Destructive Inspection "
            "(CLASS_A_ULTRASONIC_C_SCAN) MUST be performed before flight release. "
            "JTD TASK CARD 53-11-00-280 (CALIBRATED FASTENER TORQUE-RECHECK PROCEDURE): "
            "If Class-A Ultrasonic C-Scan inspection of Frame 496 Titanium Ti-6Al-4V close-tolerance shear "
            "fasteners (including Fastener Hole #14) measures hole shear elongation between 0.005 in and "
            "the 0.015 in SRM Chapter 51-40 discard limit (e.g., 0.012 in measured elongation), depot "
            "teardown is NOT required. Perform JTD Task Card 53-11-00-280: execute calibrated fastener "
            "torque-recheck to 38.0 N*m +/- 1.5 N*m (336 in-lbs), verify zero collar rotation, and record "
            "disposition SERVICEABLE_WITH_TORQUE_RECHECK on Aircraft Form 700 / AFTO Form 781 subject to "
            "Lead Stress Engineer Human-in-the-Loop (HITL) release sign-off."
        ),
    },
    {
        "doc_id": "DOC-05",
        "chunk_id": "DOC-SRM-51-40-FRAME496-CAD",
        "title": "Structural Repair Manual (SRM) Chapter 51-40 — Frame 496 Fastener Hole Elongation Limits & 3D CAD Datum Coordinates",
        "filename": "DOC-05_SRM_Chapter_51-40_Fastener_Hole_Limits.pdf",
        "mime_type": "application/pdf",
        "publication_code": "SRM-F35-51-40",
        "s1000d_dmc": "DMC-F35-51-40-00-00A-040A-A",
        "system_subsystem_code": "51-40",
        "aircraft_variant_applicability": ["F-35A", "F-35B", "F-35C"],
        "service_branch_origin": "USAF",
        "bit_fault_associated": False,
        "document_version_date": "2026-08-12",
        "datastore_target": "jtd",
        "uri": f"{GCS_DOCS_PREFIX}/DOC-05_SRM_Chapter_51-40_Fastener_Hole_Limits.pdf",
        "content": (
            "STRUCTURAL REPAIR MANUAL (SRM) CHAPTER 51-40 | PRIMARY BULKHEAD FASTENER HOLE ELONGATION "
            "ALLOWABLE LIMITS & 3D CAD SPATIAL DATUM MAPPING. "
            "CAD DATUM REFERENCE (FRAME 496 — PORT WING CARRY-THROUGH BULKHEAD): "
            "Fastener Hole #14 3D CAD Coordinates: Fuselage Station FS 496.00, Buttock Line BL -42.50 (Port), "
            "Waterline WL 118.25 (Local Flange Coordinate: X=142.4 mm, Y=-38.2 mm, Z=12.0 mm; "
            "Ultrasonic C-Scan ROI Pixel Bounding Box: [x_min=412, y_min=288, x_max=468, y_max=344]). "
            "METALLURGY SPECIFICATION: Titanium Alloy Ti-6Al-4V (AMS 4928 / AMS 4967) close-tolerance "
            "shear bolt (Manufacturing Batch Lot #8841-B). "
            "ALLOWABLE SHEAR ELONGATION THRESHOLDS (SRM CHAPTER 51-40 TABLE 51-40-2): "
            "- Measured Elongation <= 0.005 in (0.127 mm): UNRESTRICTED_SERVICEABLE. "
            "- Measured Elongation > 0.005 in and < 0.015 in (e.g., 0.012 in / 0.305 mm): "
            "SERVICEABLE_WITH_TORQUE_RECHECK (Requires JTD Task Card 53-11-00-280 calibrated torque-recheck; "
            "no structural teardown required). "
            "- Measured Elongation >= 0.015 in (0.381 mm): GROUNDED_DEPOT_TEARDOWN (Exceeds maximum "
            "allowable elongation limit of 0.015 inches; requires oversize ream and interference bushing)."
        ),
    },
    {
        "doc_id": "DOC-06",
        "chunk_id": "DOC-NDI-CSCAN-ZM151-F496-H14",
        "title": "Phased-Array Ultrasonic C-Scan NDI Image & Report — Tail ZM151, Frame 496, Fastener Hole #14",
        "filename": "DOC-06_Ultrasonic_CScan_Frame496_Hole14.png",
        "pdf_filename": "DOC-06_Ultrasonic_CScan_Frame496_Hole14.pdf",
        "mime_type": "image/png",
        "publication_code": "NDI-CSCAN-20261102-ZM151",
        "s1000d_dmc": "NDI-F35B-ZM151-F496-H14",
        "system_subsystem_code": "53-11",
        "aircraft_variant_applicability": ["F-35A", "F-35B"],
        "service_branch_origin": "RAF",
        "bit_fault_associated": False,
        "document_version_date": "2026-11-02",
        "datastore_target": "jtd",
        "uri": f"{GCS_DOCS_PREFIX}/DOC-06_Ultrasonic_CScan_Frame496_Hole14.png",
        "content": (
            "PHASED-ARRAY ULTRASONIC C-SCAN NON-DESTRUCTIVE INSPECTION (NDI) RECORD | DOC-06. "
            "INSPECTION ID: NDI-CSCAN-20261102-ZM151 | AIRCRAFT TAIL: ZM151 | STATION: Frame 496 "
            "(Port-Side Wing Carry-Through Bulkhead Upper Shear Web). "
            "PROBE CONFIG: 10 MHz 64-Element Linear Phased Array, 0-deg/45-deg Shear Wave Gate. "
            "MULTIMODAL VISION & CAD REGISTRATION FINDINGS: "
            "- Target Feature: Frame 496 — Fastener Hole #14 (CAD Datum FS 496.00, BL -42.50, WL 118.25; "
            "C-Scan Pixel Bounding Box [412, 288, 468, 344]). "
            "- Measured Shear Elongation: 0.012 inches (0.305 mm) bearing deformation along 315-deg load axis. "
            "- SRM Chapter 51-40 Allowable Elongation Limit: 0.015 inches (0.381 mm). "
            "- Margin to Condemnation Limit: +0.003 inches (Within allowable service limits: 0.012 in < 0.015 in). "
            "- Subsurface Cracking / Delamination: NONE DETECTED (0.000 in). "
            "- Installed Fastener Metadata: MBOM-ZM151-F496-H14, Titanium Ti-6Al-4V, Lot #8841-B "
            "(312.0 hours since install; 14 allied F-35 tails globally share Lot #8841-B)."
        ),
    },
    {
        "doc_id": "DOC-07",
        "chunk_id": "DOC-AWD-MIL-HDBK-516C-DEFSTAN-00-970",
        "title": "Airworthiness Directives & Structural Integrity Basis — MIL-HDBK-516C, DEF STAN 00-970 & MIL-STD-3001",
        "filename": "DOC-07_Airworthiness_Directives_MIL-HDBK-516C.pdf",
        "mime_type": "application/pdf",
        "publication_code": "AWD-MIL-HDBK-516C-00970",
        "s1000d_dmc": "AWD-UKMAA-DEFSTAN-00-970",
        "system_subsystem_code": "00-00",
        "aircraft_variant_applicability": ["F-35A", "F-35B", "F-35C"],
        "service_branch_origin": "RAF",
        "bit_fault_associated": False,
        "document_version_date": "2026-07-01",
        "datastore_target": "jtd",
        "uri": f"{GCS_DOCS_PREFIX}/DOC-07_Airworthiness_Directives_MIL-HDBK-516C.pdf",
        "content": (
            "MILITARY AIRWORTHINESS CERTIFICATION DIRECTIVE | MIL-HDBK-516C SECTION 5 (STRUCTURES), "
            "UK MAA DEF STAN 00-970 PART 1 SECTION 3, AND MIL-STD-3001. "
            "MANDATORY ENGINEERING INVARIANTS FOR AI-ASSISTED SUSTAINMENT PLATFORMS: "
            "(1) DETERMINISTIC STRUCTURAL MATH ONLY (SAFE-01): Under MIL-HDBK-516C para 5.3 and DEF STAN 00-970, "
            "probabilistic language models MUST NEVER estimate or interpolate Rainflow cycle counts, "
            "Palmgren-Miner cumulative fatigue damage (D = sum(n_i / N_i)), or structural yield percentages. "
            "All fatigue and yield values MUST be computed by a verified deterministic ASIP physics engine "
            "(e.g., EXC-20261102-ZM151: Peak 9.4 G at Mach 1.3, 220.0 C EGT -> Miner's Rule damage delta "
            "D_i = 0.0042, Calculated Yield = 104.2%). "
            "(2) FLEET-WIDE LOT CONTAINMENT: Any fastener lot exhibiting measurable shear elongation > 0.010 in "
            "after an over-G event (such as Titanium Ti-6Al-4V Lot #8841-B at 0.012 in) requires flagging all "
            "affected airframes across the global fleet (14 other F-35 tails globally) for proactive 30-day "
            "NDI inspection. "
            "(3) TWO-STAGE HUMAN-IN-THE-LOOP (HITL) RELEASE GATE (SAFE-02): Automated generation of an "
            "Aircraft Form 700 / AFTO Form 781 release package MUST stage the record in PENDING_HITL_REVIEW. "
            "Transition to CONFIRMED_BY_ENGINEER requires explicit subsequent-turn authorization by a "
            "designated Lead Stress Engineer or Chief Technical Officer (CTO)."
        ),
    },
    {
        "doc_id": "DOC-08",
        "chunk_id": "DOC-FORM700-SAR-TEMPLATE-ZM151",
        "title": "UK MOD Form 700 / AFTO Form 781 & MIL-STD-3001 Structural Appraisal Report (SAR) Template",
        "filename": "DOC-08_Form_700_Structural_Appraisal_Template.pdf",
        "mime_type": "application/pdf",
        "publication_code": "MOD-FORM-700-AFTO-781",
        "s1000d_dmc": "FORM700-SAR-MIL-STD-3001",
        "system_subsystem_code": "00-00",
        "aircraft_variant_applicability": ["F-35A", "F-35B", "F-35C"],
        "service_branch_origin": "RAF",
        "bit_fault_associated": False,
        "document_version_date": "2026-10-10",
        "datastore_target": "jtd",
        "uri": f"{GCS_DOCS_PREFIX}/DOC-08_Form_700_Structural_Appraisal_Template.pdf",
        "content": (
            "UK MOD FORM 700 (MOD FORMS 703 / 704 / 705 / 707A) & US AFTO FORM 781 AIRWORTHINESS RELEASE "
            "PACKAGE SPECIFICATION | MIL-STD-3001 STRUCTURAL APPRAISAL REPORT (SAR) TEMPLATE. "
            "REFERENCE PACKAGE ID: AWR-700-20261102-ZM151. "
            "REPORT ARTIFACT URI: gs://antig-dave-f35-staging-europe-west1/unstructured/sar/SAR-20261102-ZM151.pdf. "
            "REQUIRED APPRAISAL FIELDS: "
            "- Aircraft Tail & Unit: ZM151 (RAF Marham, 617 Squadron). "
            "- Exceedance Telemetry Sync: Event EXC-20261102-ZM151 at 2026-11-02T14:22:18.420Z (3.2s window), "
            "Peak Load 9.4 G at Mach 1.3, Peak EGT 220.0 C on Frame 496. "
            "- Deterministic ASIP Physics Result: Palmgren-Miner Damage Delta = 0.0042; "
            "Calculated Yield Strength = 104.2% (> 100.0% threshold -> CLASS_A_ULTRASONIC_C_SCAN). "
            "- NDI & 3D CAD Join Result: DOC-06 Phased-Array Ultrasonic C-Scan mapped to SRM Chapter 51-40 "
            "Frame 496 — Fastener Hole #14; Measured Shear Elongation = 0.012 in vs Allowable Limit = 0.015 in. "
            "- mBOM Fastener Audit: Record MBOM-ZM151-F496-H14, Titanium Ti-6Al-4V, Lot #8841-B, 312.0 hrs "
            "since install; 14 other global F-35 tails flagged for 30-day containment inspection. "
            "- Mandated Maintenance Action: JTD Task Card 53-11-00-280 (Calibrated Fastener Torque-Recheck). "
            "- Engineering Disposition: SERVICEABLE_WITH_TORQUE_RECHECK. "
            "- HITL Governance Gate: Staged as PENDING_HITL_REVIEW for Lead Stress Engineer / CTO approval."
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
        "uri": f"{GCS_DOCS_PREFIX}/DOC-09_MAM_Section_9-1_HighTemp_RAM.pdf",
        "content": (
            "LOW OBSERVABLE (LO) MAINTENANCE MANUAL (MAM) SECTION 9-1 | S1000D DMC-F35B-51-70-09-01A-720A-A. "
            "SUBSYSTEM: OUTER MOLD LINE (OML) COATING & RADAR ABSORBENT MATERIAL (RAM) THERMAL RESTORATION. "
            "APPLICABILITY: F-35A / F-35B / F-35C (RAF Marham & RN 809 NAS HMS Queen Elizabeth). "
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
