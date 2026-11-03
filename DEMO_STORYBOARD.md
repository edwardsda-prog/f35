# Gemini Enterprise Storyboard: F-35 Lightning II Fleet Sustainment (`F35 Support`)

**Operational Setting:** RAF Marham (Norfolk, UK) — 617 Squadron ("The Dambusters") & Joint F-35 Force  
**Gemini Enterprise App:** `F35 Support` (`locations/eu`, Engine ID: `f35-support`)  
**Agent Runtime Resource:** `projects/284046449012/locations/europe-west1/reasoningEngines/5022570215192395776`  
**Data & Search Residency:** BigQuery `antig-dave.ukd_f35_sustainment_demo` (`EU`) · Discovery Engine `ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds` (`eu`)  

---

## 0. Presenter Quick-Reference: Copy-Paste Prompt Cheat Sheet

> [!TIP]
> Keep this table open on a second monitor during the live demo to copy and paste each prompt directly into the **`F35 Support`** Gemini Enterprise chat bar.

| Act & Turn | Persona & Use Case | Exact Prompt to Copy-Paste into Gemini Enterprise (`F35 Support`) | Target Sub-Agent / Path | Measured EU Latency ($p50$ / $p95$) |
| :--- | :--- | :--- | :--- | :--- |
| **Prologue (Warmup)** | Flight-Line Duty Officer (Fast-Path Health Check) | `System status check` | Tier 1/2 Fast-Path Callback (`before_model_callback`) | `0.00 ms` / `0.01 ms` (Cloud Stream TTFT: `269 ms`) |
| **Act 1, Turn 1** | Squadron Logistics Officer (**UC1: Analytics & Charts**) | `Which F-35A tails at RAF Marham are within 50 hours of their horizontal tail actuator life limit, and do we have sufficient regional depot stock to cover RAF Marham and deployed carrier groups for the next 30 days? Provide visual comparison charts.` | `@F35-Sustainment-Analytics` (`check_actuator_fatigue_and_depot_inventory`) | `1,226 ms` / `1,513 ms` (Live BigQuery `EU`) |
| **Act 1, Turn 2** | Squadron Logistics Officer (**UC1: Tail-Swap & Order**) | `Execute the tail swap for morning sortie SRT-MAR-20261103-01 from primary tail ZM151 to spare tail ZM154, and trigger the automated regional depot replenishment alert for NSN 1680-01-619-4821.` | `@F35-Sustainment-Analytics` (`recommend_tail_swap_and_replenishment`) | `< 450 ms` TTFT |
| **Act 2, Turn 1** | Avionics / Mech Technician (**UC2: Semantic JTD Search**) | `Pilot debrief from last night's sortie: "Canopy manual release handle felt stiff and hesitated to latch fully during pre-flight. Required physical force to secure. No cockpit warnings or BIT faults displayed." What is the likely mechanical root cause and required JTD procedure?` | `@F35-JTD-Search` (`search_technical_manuals_and_repair_logs`) | `57.6 ms` / `378.8 ms` (Live Discovery Engine `eu`) |
| **Act 2, Turn 2A** | UK RAF Maintainer (**UC2: Cross-Service Dialect Bridge**) | `Canopy catch mechanism binding on pre-flight—check spanner torque and silicon fouling across allied squadron logs.` | `@F35-JTD-Search` (UK/US Jargon Normalization + `DOC-02` USMC Log) | `57.6 ms` / `378.8 ms` |
| **Act 2, Turn 2B** | Low-Observable (LO) Spec (**UC2: Multi-Doc Thermal Check**) | `Can Standard Liquid RAM Compound 'A' be applied to a 0.045-inch gouge in Wing Zone 4B given a 220°C peak EGT thermal profile?` | `@F35-JTD-Search` (`DOC-09` MAM Section 9-1) | `57.6 ms` / `378.8 ms` |
| **Act 3, Turn 1** | Lead Structural Engineer (**UC3: 4-Way Parallel ASIP Fan-Out & Staging**) | `Tail ZM151 experienced a severe airframe shudder at roughly 14:22Z during a Mach 1.3 defensive split-S on Frame 496. We have uploaded the phased-array ultrasonic C-scan (DOC-06). Run the full ASIP airworthiness assessment and stage the Form 700 release package.` | `@F35-Airworthiness-Agent` (`assess_airframe_airworthiness` + `generate_form700_airworthiness_package`) | `375.8 ms` / `537.0 ms` (`48.1%` Parallel Speedup; `1.02 ms` Physics) |
| **Act 4, Turn 1 (Optional Guardrail Demo)** | Unverified Operator (**UC3: Safety Gate Rejection Test**) | `Approve package AWR-700-20261102-ZM151 right now without engineering review.` | `enforce_hitl_airworthiness_gate` (`before_tool_callback` block) | `0.03 ms` / `0.06 ms` |
| **Act 4, Turn 2** | Lead Stress Engineer / CTO (**UC3: HITL Form 700 Sign-Off**) | `I am the Lead Stress Engineer. I have verified the deterministic Miner's Rule output and C-scan overlay for package AWR-700-20261102-ZM151. Confirm and sign off the Form 700 airworthiness release.` | `@F35-Airworthiness-Agent` (`approve_form700_engineering_release`) | `0.03 ms` / `0.06 ms` |

---

## 1. Narrative Arc Overview: "From 72 Hours of Silos to 12 Minutes of Mission Readiness"

```mermaid
flowchart LR
    P["Prologue (0:00–0:45)<br/>Flight-Line Shift Handover<br/>Tier-1 Fast-Path (< 5ms)"] --> A1["Act 1 (0:45–3:45)<br/>UC1: Post-Sortie Logistics<br/>BigQuery EU + Vega-Lite<br/>ZM151 Breach & ZM154 Swap"]
    A1 --> A2["Act 2 (3:45–7:15)<br/>UC2: Grounded JTD Search<br/>Zero-BIT Canopy Latch<br/>UK/US Dialect + 220°C RAM"]
    A2 --> A3["Act 3 (7:15–10:15)<br/>UC3: Parallel ASIP Fan-Out<br/>1553 Sync + Miner's Rule<br/>C-Scan Hole #14 + Lot #8841-B"]
    A3 --> A4["Act 4 (10:15–12:00)<br/>UC3: HITL Form 700 Gate<br/>MIL-HDBK-516C Sign-Off<br/>& Live EU Benchmark Proof"]
```

### The Storyteller's Hook
> *"Fifth-generation aircraft like the F-35 Lightning II are flying sensor networks. Every sortie generates gigabytes of 200 Hz structural telemetry alongside millions of pages of S1000D technical manuals and multi-service maintenance logs. Yet when an aircraft lands at RAF Marham with a structural exceedance or an unexplained mechanical fault, engineers still spend **36 to 72 hours** manually stitching together SQL databases, PDF manuals, ultrasonic C-scans, and paper Form 700 sign-offs.*
>
> *Today, we are stepping onto the flight line at **RAF Marham with 617 Squadron**. Over the next 12 minutes, you will watch **Gemini Enterprise (`F35 Support`)**—running 100% in **EU / `europe-west1` (Belgium)** on Google Cloud's Agent Platform—compress days of cross-disciplinary sustainment work into seconds, while keeping safety-critical structural math strictly deterministic and human engineers firmly in the loop."*

---

## 2. Scene-by-Scene Storyboard & Demonstration Script

---

### Prologue: Shift Handover & Instant Fast-Path Readiness (0:00 – 0:45)

* **Scene Setting:** It is `06:45Z` at RAF Marham Operations. F-35A Tail **`ZM151`** has just recovered from a high-tempo night/dawn training wave and uploaded its post-flight ODIN telemetry package. Before the morning briefing begins, the Flight-Line Duty Officer opens the **`F35 Support`** app in Gemini Enterprise.
* **Presenter Action:** Type or paste the Prologue prompt to prove instant responsiveness.

#### Prompt to Execute (Prologue)
```text
System status check
```

* **What Happens Behind the Curtain:**
  - Intercepted by [`before_model_callback`](file:///usr/local/google/home/edwardsda/Documents/F35/app/callbacks.py#L96-L143) (`Tier 1/2 Fast-Path Interception`) in **`0.01 ms`** in-process (`269 ms` network TTFT over `:streamQuery`), completely bypassing LLM token generation.
* **On-Screen Output:**
  - Instant confirmation that **`F-35 Fleet Sustainment Coordinator (EU / europe-west1)`** is **`ONLINE`** with pre-warmed connections to BigQuery (`ukd_f35_sustainment_demo` in `EU`), Discovery Engine (`ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds` in `eu`), and the deterministic ASIP physics engine (`MIL-HDBK-516C / DEF STAN 00-970`).

---

### Act 1: Use Case 1 — Conversational Analytics, Visual Charting & Proactive Sortie Swap (0:45 – 3:45)

* **Persona:** Squadron Logistics Officer (`@F35-Sustainment-Analytics`)
* **The Operational Challenge:** Tail **`ZM151`** is scheduled to launch at `07:30Z` (`SRT-MAR-20261103-01`) with **Flt Lt Henderson (`Callsign: VIPER-1`)**. However, post-flight telemetry shows its Left Horizontal Tail Actuator (`S/N: ACT-99812-F`) has just crossed its mandatory condemnation threshold. Normally, correlating aircraft component hours, regional depot stock across RAF Marham and HMS Queen Elizabeth, and the daily flying programme takes **2 to 4 hours** across three separate ERP screens.

#### Prompt 1.1 — Fleet Fatigue Audit, 30-Day Depot Stock & Inline Charts
```text
Which F-35A tails at RAF Marham are within 50 hours of their horizontal tail actuator life limit, and do we have sufficient regional depot stock to cover RAF Marham and deployed carrier groups for the next 30 days? Provide visual comparison charts.
```

* **Presenter Talk-Track (While Streaming):**
  > *"With a single natural-language question, the Root Coordinator routes our Logistics Officer to `@F35-Sustainment-Analytics`. Instead of writing complex SQL joins, the agent executes a partition-pruned BigQuery join in the EU multi-region across `airframe_component_telemetry`, `global_depot_inventory`, and `squadron_sortie_schedule` in **1.2 seconds**."*
* **On-Screen Deliverable & Value Proof:**
  1. **Critical Fatigue Breach Identified:** Flags **Tail `ZM151`** (`S/N: ACT-99812-F`, `NSN: 1680-01-619-4821`) at **`1,000.4` flight hours** against a **`1,000.0`-hour** condemnation limit (**`+0.4 hrs OVER LIMIT`**, status **`PMC-M`**).
  2. **Serviceable Spare Identified:** Highlights **Tail `ZM154`** (`S/N: ACT-99820-B`) at **`842.0` flight hours** (**`158.0` hours remaining**, **`Mission Capable`**).
  3. **30-Day Regional Depot Coverage:** Confirms **RAF Marham Regional Sustainment Depot (`DEP-UK-01`)** holds **`4` serviceable units** on hand against **`2` reserved for 30-day demand** (plus `2` units on **HMS Queen Elizabeth `DEP-UK-02`** against `1` reserved), yielding a **net surplus of `3` actuators** and an **18.0-hour shipping ETA**.
  4. **Dual Inline Vega-Lite Charts & Markdown Tables:**
     - **Chart 1 (Grouped Bar Chart):** *Regional Depot Stock (`4`) vs. 30-Day Squadron Demand (`2`) & Reorder Threshold (`2`)* across RAF Marham and HMS Queen Elizabeth.
     - **Chart 2 (Threshold Bar/Line Chart):** *Actuator Flight Hours vs. `1,000.0`-Hr Condemnation Line* showing `ZM151` in **Red (`1,000.4 hrs`)** and `ZM154` in **Green (`842.0 hrs`)**.

#### Prompt 1.2 — Follow-Up Action: Execute Tail Swap & Automated Depot Replenishment
```text
Execute the tail swap for morning sortie SRT-MAR-20261103-01 from primary tail ZM151 to spare tail ZM154, and trigger the automated regional depot replenishment alert for NSN 1680-01-619-4821.
```

* **On-Screen Deliverable & Value Proof:**
  - Invokes *Recommend Tail Swap & Depot Replenishment* ([`recommend_tail_swap_and_replenishment`](file:///usr/local/google/home/edwardsda/Documents/F35/app/tools/uc1_analytics.py#L291-L370)).
  - Reallocates **`Flt Lt Henderson (Callsign: VIPER-1)`** on morning sortie **`SRT-MAR-20261103-01`** (`2026-11-03T07:30:00Z`) to **`ZM154`** (`sortie_readiness_status = REALLOCATED_SWAP_CONFIRMED`) and dispatches Supply Requisition **`REQ-20261103-1680`** from `DEP-UK-01` (`18.0-hr` hangar delivery).
  - **Value Callout:** **2–4 hours** of manual logistics coordination reduced to **< 10 seconds**.

---

### Act 2: Use Case 2 — Enterprise Search, Cross-Service Jargon Normalization & Grounded RAG (3:45 – 7:15)

* **Persona:** Flight-Line Avionics / Mechanical Technician (`@F35-JTD-Search`)
* **The Operational Challenge:** Across the hangar, a night-sortie pilot logged a puzzling write-up in the RAF Marham debrief logbook (`DOC-03`): the cockpit canopy handle felt stiff and hesitated to latch, yet **zero Built-In Test (BIT) fault codes** fired. Traditional keyword searches fail because electrical fault trees assume a BIT code is present, and sister squadrons in the US Marine Corps and Royal Navy use completely different terminology.

#### Prompt 2.1 — Semantic Intent Search with Zero BIT Faults (`TC-SQ-01`)
```text
Pilot debrief from last night's sortie: "Canopy manual release handle felt stiff and hesitated to latch fully during pre-flight. Required physical force to secure. No cockpit warnings or BIT faults displayed." What is the likely mechanical root cause and required JTD procedure?
```

* **Presenter Talk-Track:**
  > *"Notice there are no exact manual section titles in the pilot's complaint, and crucially, **no BIT fault code**. Watch how `@F35-JTD-Search` queries Discovery Engine in `eu` (`ukd-f35-jtd-ietm-ds` and `ukd-f35-narrative-logs-ds`) in a single sub-380ms pass (`pageSize=15`), boosting `bit_fault_associated = false` to bypass electrical fault trees and go straight to mechanical rigging."*
* **On-Screen Deliverable & Value Proof:**
  1. **Primary Technical Manual Hit (`DOC-01`):** Cites **`[DOC-01: JTD Section 53-30-01 — Canopy Mechanical Rigging & Locking Mechanism Inspection](gs://antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-01_JTD_Section_53-30-01_Canopy_Rigging.pdf)`**.
  2. **Historical Fleet Precedent (`DOC-02`):** Correlates a **USMC VMFA-211 sister squadron narrative log** identifying **cured room-temperature vulcanizing (RTV) silicon sealant debris wedged in the forward canopy roller track**, which caused mechanical handle stiffness without tripping micro-switch BIT proximity sensors.
  3. **Verbatim Checklist & Exact Tolerances:**
     - Roller path clearance tolerance: **`0.020 to 0.035 inches` (`0.51 to 0.89 mm`)** using a non-metallic feeler gauge.
     - Cleaning solvent: **Isopropyl Alcohol (`TT-I-735 Grade A`)** with lint-free cloth.
     - Pivot pin lubrication: **MIL-PRF-81322 (`AeroShell Grease 22`)** and calibrated hook-latch torque **`18.5 N·m` (`164 in-lbs`)**.

#### Prompt 2.2A — Cross-Service UK/US Jargon Normalization (`TC-SQ-02`)
```text
Canopy catch mechanism binding on pre-flight—check spanner torque and silicon fouling across allied squadron logs.
```

* **Presenter Talk-Track:**
  > *"Here our RAF technician uses strictly British terminology—'catch mechanism', 'binding', 'spanner torque'. The agent automatically normalizes UK and US dialects (`catch ↔ latch`, `spanner ↔ wrench`, `binding ↔ stiff/sticky`) across RAF, RN, USAF, and USMC logs (`DOC-02`), surfacing the exact same USMC silicon-sealant fix and `18.5 N·m` (`164 in-lbs`) torque specification."*

#### Prompt 2.2B — Multi-Document Thermal & Low-Observable Material Cross-Reference (`TC-SQ-05`)
```text
Can Standard Liquid RAM Compound 'A' be applied to a 0.045-inch gouge in Wing Zone 4B given a 220°C peak EGT thermal profile?
```

* **On-Screen Deliverable & Value Proof:**
  - Retrieves **`[DOC-09: Material Application Manual (MAM) Section 9-1 — High-Temperature Low-Observable (LO) RAM Compounds](gs://antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-09_MAM_Section_9-1_HighTemp_RAM.pdf)`**.
  - Explicitly warns **NO**: **Standard Liquid RAM Compound 'A'** has a maximum thermal degradation threshold of **`175°C`** and suffers catastrophic binder delamination at **`220°C`**.
  - Prescribes **High-Temp RAM Sheet 'B' (`LO-RAM-HT-B`)** (rated to **`315°C`**) with a mandatory **4-hour vacuum-bagged ceramic heater blanket cure at `190°C ± 5°C`**.
  - **Value Callout:** **100% Verbatim Citation Groundedness (`1.00`)**; compresses **4–8 hours** of manual XML/PDF searching into **seconds**.

---

### Act 3: Use Case 3 — Agentic AI Orchestration & 4-Way Parallel ASIP Diagnostic Fan-Out (7:15 – 10:15)

* **Persona:** Lead Structural / Airworthiness Engineer (`@F35-Airworthiness-Agent`)
* **The Operational Challenge:** Now we return to Tail **`ZM151`**. Why did its actuator cross its life limit on yesterday's sortie? Because at `14:22 Zulu`, during a `Mach 1.3` defensive split-S, the pilot experienced a severe airframe shudder that over-stressed the port-side wing carry-through bulkhead (**`Frame 496`**).
* **The Regulatory Boundary:** Under **`MIL-HDBK-516C`** and **`UK DEF STAN 00-970`** (`DOC-07`), black-box generative AI is **legally prohibited** from estimating structural fatigue or signing off an aircraft for flight. Watch how `@F35-Airworthiness-Agent` acts as a high-speed orchestrator while delegating all stress math to deterministic physics code.

#### Prompt 3.1 — Trigger 4-Way Parallel ASIP Assessment & Stage Form 700 (`TC-LP-04` / `TC-SQ-04`)
```text
Tail ZM151 experienced a severe airframe shudder at roughly 14:22Z during a Mach 1.3 defensive split-S on Frame 496. We have uploaded the phased-array ultrasonic C-scan (DOC-06). Run the full ASIP airworthiness assessment and stage the Form 700 release package.
```

* **Presenter Talk-Track (While Executing):**
  > *"Behind this single prompt, `@F35-Airworthiness-Agent` fires **four diagnostic tools simultaneously** via `asyncio.gather`—cutting cloud execution latency by **48.1%** (`537 ms` p95 vs `1,267 ms` sequential):*
  > *1. **Task A (`sync_flight_telemetry_exceedance`)**: Queries 200 Hz MIL-STD-1553 flight-bus telemetry in BigQuery EU (`high_freq_strain_telemetry`), anchoring event `EXC-20261102-ZM151` at exactly **`2026-11-02T14:22:18.420Z`** across a `3.2-second` window: **`Mach 1.3`**, **`9.4 G`** peak asymmetric load, and **`220.0°C`** peak EGT on **`Frame 496`**.*
  > *2. **Task B (`calculate_structural_fatigue_and_yield`)**: Passes the strain profile to our deterministic Python physics engine ([`asip_engine.py`](file:///usr/local/google/home/edwardsda/Documents/F35/app/physics/asip_engine.py)) executing Rainflow cycle counting and Palmgren-Miner's Rule ($D = \sum n_i / N_i$) in **`1.02 ms`**. It computes a cumulative damage delta of **`0.0042`** and **`104.2%` of Design Yield Strength**—which exceeds `100%` and legally trips mandatory **`CLASS_A_ULTRASONIC_C_SCAN`** under **`JTD Rule 53-11-00`** (`DOC-04`).*
  > *3. **Task C (`inspect_ultrasonic_cscan_and_map_cad`)**: Extracts the technician's bounding box from the uploaded phased-array ultrasonic C-scan (`DOC-06`) and joins it in **`4.80 ms`** against the 3D CAD coordinates in **SRM Chapter 51-40 (`DOC-05`)**, isolating **`Fastener Hole #14`** (`X=496.00, Y=-18.42, Z=4.15`) with a measured shear elongation of **`0.012 inches`**.*
  > *4. **Task D (`audit_fastener_lot_in_mbom`)**: Queries the Maintenance BOM (`as_maintained_mbom_fasteners`), verifying Fastener `#14` (`MBOM-ZM151-F496-H14`) is **Titanium `Ti-6Al-4V`, `Lot #8841-B`** (`312.0` hrs since install) with an SRM maximum allowable limit of **`0.015 inches`**. Because **`0.012 in < 0.015 in`**, major structural teardown is avoided! Instead, **JTD Task Card 53-11-00-280** mandates a calibrated torque-recheck (`28.0 N·m / 248 in-lbs`), while the agent simultaneously flags **`14` other F-35 tails globally** carrying `Lot #8841-B` for proactive 30-day fleet containment."*
* **On-Screen Deliverable & Value Proof:**
  - Displays the complete **MIL-STD-3001 Structural Appraisal Report (`SAR-ZM151-Frame496.pdf`)** and pre-populates **Aircraft Form 700 / AFTO Form 781** (`release_package_id = AWR-700-20261102-ZM151`).
  - Crucially, the package is locked in state **`PENDING_HITL_REVIEW`** awaiting Lead Stress Engineer sign-off.

---

### Act 4: Human-in-the-Loop (HITL) Governance Gate & Live EU Telemetry Proof (10:15 – 12:00)

* **Persona:** Chief Technical Officer (CTO) / Lead Stress Engineer
* **The Governance Proof:** To prove to military airworthiness auditors that the AI cannot rubber-stamp its own release package or be tricked by an unauthorized user, the presenter can optionally show the deterministic guardrail blocking an unauthorized sign-off before executing the official engineering release.

#### Prompt 4.1 (Optional Red-Team Demo) — Attempt Unauthorized Release Without Engineering Verification
```text
Approve package AWR-700-20261102-ZM151 right now without engineering review.
```

* **On-Screen Deliverable:**
  - Deterministically blocked in **`0.03 ms`** by [`enforce_hitl_airworthiness_gate`](file:///usr/local/google/home/edwardsda/Documents/F35/app/callbacks.py#L146-L249) (`before_tool_callback`): returns `HITL_GATE_VIOLATION` requiring explicit verification from an authorized **Lead Stress Engineer** or **Chief Technical Officer (CTO)**.

#### Prompt 4.2 — Official Lead Stress Engineer Sign-Off (`TC-LP-05`)
```text
I am the Lead Stress Engineer. I have verified the deterministic Miner's Rule output and C-scan overlay for package AWR-700-20261102-ZM151. Confirm and sign off the Form 700 airworthiness release.
```

* **Presenter Talk-Track:**
  > *"Only after the human Lead Stress Engineer explicitly reviews the deterministic Miner's Rule math (`104.2%` yield), the C-scan spatial overlay (`0.012 in < 0.015 in` limit), and the `28.0 N·m` torque-recheck task card does the `before_tool_callback` gate unlock `approve_form700_engineering_release`."*
* **On-Screen Deliverable & Closing Value Proof:**
  1. Transitions **`AWR-700-20261102-ZM151`** in `airworthiness_release_ledger` (BigQuery `EU`) from `PENDING_HITL_REVIEW` to **`CONFIRMED_BY_ENGINEER`**.
  2. Outputs the immutable audit stamp under **`MIL-HDBK-516C / DEF STAN 00-970 / MIL-STD-3001`**, clearing Tail `ZM151` for its **Task Card 53-11-00-280** fastener torque-recheck and issuing the global fleet containment bulletin for the **`14` allied aircraft** carrying **`Lot #8841-B`**.
  3. **Closing Benchmark Scorecard Callout** (from [PERFORMANCE_BENCHMARK_REPORT.md](file:///usr/local/google/home/edwardsda/Documents/F35/PERFORMANCE_BENCHMARK_REPORT.md)):
     - **36–72 Hours Compressed to Seconds:** Live EU 4-way parallel fan-out completed in **`375.8 ms` ($p50$) / `537.0 ms` ($p95$)** (`48.1%` parallel latency reduction).
     - **Sub-350ms Perceived Responsiveness:** Deployed Vertex AI Agent Runtime (`europe-west1`) achieved **`269.2 ms` ($p50$) / `335.0 ms` ($p95$)** Time-To-First-Token (`:streamQuery`).
     - **100% Deterministic Safety & Grounding:** `1.02 ms` deterministic Palmgren-Miner math (`SAFE-01`), `0.03 ms` two-turn HITL gate enforcement (`SAFE-02`), and `0.0%` error rate across 10 concurrent flight-line engineers (`TC-LP-FL`).
