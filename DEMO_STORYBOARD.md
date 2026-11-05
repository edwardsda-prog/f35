# Executive Demo Storyboard: F-35 Fleet Sustainment (`F35 Support`)
### *The "6-Prompt Golden Thread" — Compressing Days of Sustainment into 4 Minutes*

**Target Audience:** Senior Defence Leadership, Air Command, MOD DE&S, & Industry Executives  
**Operational Setting:** RAF Marham (617 Squadron "The Dambusters") & HMS Queen Elizabeth Carrier Strike Group  
**Gemini Enterprise App:** `F35 Support` (Hosted 100% in `EU` / `europe-west1` Belgium)  

---

## 0. Presenter Quick-Copy Cheat Sheet (The 6 Golden Prompts: `UC 0`, `UC 0.1`, `UC 0.5`, `UC 1A`, `UC 1B`, & `UC 2`)

> [!TIP]
> **The Entire Demo Takes 6 Fast Executive Prompts (4–5 Minutes Total).**  
> Each prompt is written in natural Commander / Maintenance Officer language and triggers live BigQuery (`EU`) tabular data, Excel / Google Sheets Cards with `.CSV` export, multi-table SQL joins, on-demand presentation graphics, and grounded JTD citations (`eu`).

| Step | Act & Persona | Exact Executive Prompt to Paste into `F35 Support` | What Appears on Screen | Live EU Speed |
| :---: | :--- | :--- | :--- | :---: |
| **0.0** | **Act 0.0: Morning Maintenance Stand-Up**<br/>*(Squadron Maintenance Officer — UC 0)* | `Show me all open Priority-1 and MICAP maintenance work orders across RAF Marham and HMS Queen Elizabeth, sorted by estimated repair time.` | **Excel / Google Sheets Card (`maintenance_work_orders`)**: Renders Spreadsheet Grid (`A`..`L`) with Status Badges (`🔴 NMC-S (MICAP)`, `🟠 NMC-M`, `🟡 PMC-M`), Formula Footer (`=COUNTA()`, `=SUM()`, `=AVERAGE()`), and clickable **[📥 Download .CSV](https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/...)** link—surfacing **ZM151**'s open actuator and canopy tickets. | **`< 1.5s`**<br/>*(SQL `< 350ms`)* |
| **0.1** | **Act 0.1: Post-Sortie PHM / BIT Fault & CND Triage**<br/>*(Flight-Line Avionics Lead — UC 0.1)* | `Query our PHM and BIT fault event log for all ZM151 post-sortie fault events and any unactioned PHM advisories across the fleet that do not have a linked work order yet.` | **Excel / Google Sheets Card (`phm_bit_fault_events`)**: Highlights **ZM151**'s `HRC-2710-88A` (Actuator), `HRC-5330-000-NONE` (**`PILOT_REPORT_ONLY_NO_BIT` + `⚠️ CND (Repeat)`** on Canopy Latch), and `HRC-5320-94G` (`🔴 CRITICAL_GROUNDING`), plus 3 unlinked fleet PHM advisories (`linked_work_order_id IS NULL`). | **`< 1.5s`**<br/>*(SQL `< 350ms`)* |
| **0.5** | **Act 0.5: Shift Dispatch, SQEP & Calibrated Tooling Join**<br/>*(Wing Maintenance Controller — UC 0.5)* | `Join our open maintenance work orders with work center tooling and SQEP shift readiness to show which active jobs are ready to dispatch versus blocked by expired tool calibration or QAR availability.` | **Multi-Table Joined Spreadsheet Card (`maintenance_work_orders` ⋈ `work_center_tooling_and_sqep`)**: Confirms **ZM151**'s Canopy Latch (`JTD-53-30-T14` calibrated torque spanner) and NDI inspection (`NDI-PAUT-496A` rig) are `🟢 READY_TO_DISPATCH`, while flagging `🔴 EXPIRED_OUT_OF_CAL` (`LO-IR-BLANKET-04`) and `🟠 BLOCKED_NO_QAR_ON_SHIFT` bottlenecks on sister tails. | **`< 1.6s`**<br/>*(2-Table SQL `< 360ms`)* |
| **1A** | **Act 1A: Protect the Morning Sortie (Turn 1)**<br/>*(Squadron Logistics Officer — UC 1A)* | `Check RAF Marham F-35A horizontal tail actuator hours against our 30-day depot stock, and recommend a tail swap for morning sortie SRT-MAR-20261103-01.` | **Tabular Fleet Briefing**: Flags **ZM151** (`1,000.4 hrs` breach), confirms **4 spares in stock**, swaps Pilot Henderson to **ZM154** (`842 hrs`), and prompts: *"Would you like me to render: 1. Actuator Fatigue Threshold Chart, 2. Regional Depot Stock vs 30-Day Demand Chart, or the full Executive Briefing Dashboard for your presentation slide deck?"* | **`1.2s`**<br/>*(TTFT `269ms`)* |
| **1B** | **Act 1B: On-Demand Slide Graphic Rendering (Turn 2)**<br/>*(Squadron Logistics Officer — UC 1B)* | `Render the full Executive Briefing Dashboard for my presentation slide deck.` | **Full HD Presentation Graphic**: Renders 1920×1080 composite slide image with **ZM151 in Red (`1,000.4 hrs`)** vs **ZM154 in Green (`842.0 hrs`)** against limit line, alongside Regional Depot Stock vs Demand bar chart, with clickable **[📥 Download Executive Slide Graphic (PNG)]** link for direct insertion into slide decks. | **`< 0.8s`**<br/>*(Chart Painter `< 790ms`)* |
| **2** | **Act 2: Fix the Unexplained Fault**<br/>*(Flight-Line Maintenance Chief — UC 2)* | `Our night-sortie pilot reported a stiff canopy release handle that hesitated to latch, with zero BIT faults. Have allied squadrons seen this, and what is the JTD fix?` | **Grounded Checklist & Authenticated Browser Citations**: Matches USMC sister-squadron log (**silicon sealant debris in roller track**) + **JTD 53-30-01** cleaning/lubrication spec via browser URLs. | **`0.38s`**<br/>*(`100%` Cited)* |

---

## 1. The Executive Storyline (60-Second Opening Hook)

```mermaid
flowchart LR
    A0["Act 0.0 (UC 0 · 0.5 Min) | MORNING STAND-UP: Open Priority-1 & MICAP Work Orders in Excel/Sheets Card"] --> A01["Act 0.1 (UC 0.1 · 0.5 Min) | PHM / BIT & CND TRIAGE: Spot ZM151 Zero-BIT Repeat Fault & Unlinked Fleet Advisories"]
    A01 --> A05["Act 0.5 (UC 0.5 · 0.5 Min) | SHIFT DISPATCH JOIN: 2-Table SQL Join (Work Orders ⋈ SQEP & Calibrated Tooling)"]
    A05 --> A1A["Act 1A (UC 1A · 1 Min) | GENERATE MORE SORTIES: Spot ZM151 Actuator Breach, Check Stock & Auto-Swap to ZM154"]
    A1A --> A1B["Act 1B (UC 1B · 0.5 Min) | VISUALIZE FLEET DATA: On-Demand Executive Dashboard Slide PNG (< 790ms)"]
    A1B --> A2["Act 2 (UC 2 · 1 Min) | EMPOWER MAINTAINERS: Solve Zero-BIT Canopy Fault via Allied USMC/RAF Experience"]
```

### Presenter Opening Talk-Track
> *"Every time an F-35 lands at RAF Marham, it downloads gigabytes of flight telemetry and PHM fault events alongside millions of pages of technical manuals, work center tooling logs, and allied maintenance narratives. Today, that data lives in disconnected silos. When an aircraft has an unlinked PHM advisory, a component near life-limit, or a mysterious mechanical fault with zero computer codes, our teams spend **hours** manually cross-checking ODIN tables, shift rosters, supply depots, and PDF manuals.*
>
> *In the next **4 minutes**, using **just 6 prompts** inside **Gemini Enterprise (`F35 Support`)**, we will follow F-35 Tail **`ZM151`** from the `06:45Z` morning maintenance stand-up (`UC 0`, `UC 0.1`, `UC 0.5`), through morning sortie protection and on-demand executive slide generation (`UC 1A` & `UC 1B`), to resolving a zero-BIT mechanical fault using 5-year coalition fleet logs (`UC 2`)."*

---

## 2. Act-by-Act Executive Walkthrough

---

### Act 0 Trilogy: Morning Maintenance Stand-Up, PHM/BIT Triage & Shift Resource Join (`UC 0` → `UC 0.1` → `UC 0.5`)

```mermaid
flowchart LR
    U0["Prompt 0.0 (UC 0): Open Priority-1 & MICAP Work Orders"] --> U01["Prompt 0.1 (UC 0.1): Post-Sortie PHM / BIT Fault & CND Triage"]
    U01 --> U05["Prompt 0.5 (UC 0.5): 2-Table SQL JOIN (Work Orders ⋈ SQEP & Calibrated Tooling)"]
    U05 --> E0["Excel / Google Sheets Cards + Clickable .CSV Exports -> Tees Up Acts 1 & 2"]
```

* **The Executive Challenge:** Every morning at `06:45Z`, the Squadron Maintenance Officer at RAF Marham reviews the **9-Table, 900-Record F-35 Data Warehouse** (`100` consistent records per table across `maintenance_work_orders`, `phm_bit_fault_events`, and `work_center_tooling_and_sqep`) covering `617 Squadron`, `207 Squadron`, and `809 Naval Air Squadron` embarked on `HMS Queen Elizabeth`. Today, correlating open Form 707A work orders against post-flight PHM Health Reporting Codes (HRCs), SQEP technician shift rosters, and calibrated special tooling requires hours of manual ODIN exports and VLOOKUP spreadsheets.

#### Step 0.0 — Paste Prompt 0.0 (`UC 0`: Single-Table Work Order Backlog)
```text
Show me all open Priority-1 and MICAP maintenance work orders across RAF Marham and HMS Queen Elizabeth, sorted by estimated repair time.
```
* **What Appears on Screen:** `@F35-Maintenance-Data` queries Table 7 (`maintenance_work_orders`, 100 records) in `< 350 ms`, rendering an **Excel / Google Sheets Card** with Status Badges (`🔴 NMC-S (MICAP)`, `🟠 NMC-M`, `🟡 PMC-M`), Formula Footer (`=COUNTA()`, `=SUM()`, `=AVERAGE()`), and a clickable **[📥 Download .CSV (Excel / Google Sheets)](https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/F35_ODIN_Maintenance_Work_Orders.csv)** link—surfacing Tail **`ZM151`**'s active discrepancies (`WO-2026-88401` EHA actuator, `WO-2026-88402` Canopy latch, and `WO-2026-88403` Frame 496 inspection).

#### Step 0.1 — Paste Prompt 0.1 (`UC 0.1`: Post-Sortie PHM / BIT Fault & Repeat CND Triage)
```text
Query our PHM and BIT fault event log for all ZM151 post-sortie fault events and any unactioned PHM advisories across the fleet that do not have a linked work order yet.
```
* **What Appears on Screen:** `@F35-Maintenance-Data` queries Table 8 (`phm_bit_fault_events`, 100 records), rendering a Spreadsheet Card with PHM Severity & CND Badges:
  - **`PHM-2026-99101` (`ZM151` · `HRC-2710-88A` · `🟠 DEGRADED_PMC`):** Port EHA actuator crossed `1,000.0` hr limit (`1,000.4` hrs) → *Tees up Act 1 (`UC 1A` & `UC 1B`)*.
  - **`PHM-2026-99102` (`ZM151` · `HRC-5330-000-NONE` · `⚪ NO_BIT_FAULT_LOGGED` · `⚠️ CND (Repeat)`):** Pilot-reported canopy latch mechanical binding with **zero BIT fault logged** (`PILOT_REPORT_ONLY_NO_BIT`, 3 repeats in 30 days) → *Tees up Act 2 (`UC 2`)*.
  - **`PHM-2026-99103` (`ZM151` · `HRC-5320-94G` · `🔴 CRITICAL_GROUNDING`):** `9.4G / Mach 1.3` over-G structural strain exceedance on Frame 496.
  - Surfaces **3 unactioned fleet PHM advisories** (`linked_work_order_id IS NULL` on `ZM154`, `ZM159`, `ZM162`) and computes `=COUNTA()`, `=SUM(recurrence_count_30d)`, and `=AVERAGE(diagnostic_confidence_pct)`.

#### Step 0.5 — Paste Prompt 0.5 (`UC 0.5`: Multi-Table SQL JOIN — Work Orders ⋈ SQEP & Calibrated Tooling)
```text
Join our open maintenance work orders with work center tooling and SQEP shift readiness to show which active jobs are ready to dispatch versus blocked by expired tool calibration or QAR availability.
```
* **What Appears on Screen:** `@F35-Maintenance-Data` executes a live BigQuery `EU` SQL `JOIN` across Table 7 (`maintenance_work_orders`) and Table 9 (`work_center_tooling_and_sqep`, 100 records):
  - Confirms **`ZM151`**'s Canopy Latch (`WO-2026-88402` with calibrated Digital Micro-Torque Spanner **`JTD-53-30-T14`**) and Frame 496 NDI inspection (`WO-2026-88403` with Phased-Array Ultrasonic C-Scan Rig **`NDI-PAUT-496A`**) are **`🟢 READY_TO_DISPATCH`** with SQEP crews and QAR inspectors on shift.
  - Immediately isolates shift resource bottlenecks on other tails: **`🔴 EXPIRED_OUT_OF_CAL`** on LO Infrared RAM Cure Blanket (`LO-IR-BLANKET-04`) and **`🟠 BLOCKED_NO_QAR_ON_SHIFT`** on night watch.

> [!IMPORTANT]
> **Act 0 Trilogy Executive Takeaway ("The So What?")**
> - **Operational Impact:** Instant visibility across work orders (`UC 0`), unlinked PHM/BIT fault advisories & repeat CND anomalies (`UC 0.1`), and SQEP/calibrated tooling dispatch readiness (`UC 0.5`).
> - **Time Compressed:** **1–2 hours** of morning ODIN data pulls and manual VLOOKUP spreadsheets compressed into **three `< 1.5s` conversational prompts**.

---

### Act 1: Generate More Sorties — Instant Fleet Readiness & Tail Swap (`UC 1A` & `UC 1B`)

```mermaid
flowchart LR
    U1A["Prompt 1A (UC 1A): Logistics Officer (07:30Z Sortie Risk)"] --> R1A["@F35-Sustainment-Analytics (BigQuery EU Join · 1.2s)"]
    R1A --> S1["Tabular Briefing: ZM151 Breached (1,000.4 hrs) + Auto-Swap to ZM154 (842 hrs)"]
    S1 --> P1["Prompt User: Render Chart 1, Chart 2, or Executive Dashboard?"]
    P1 --> U1B["Prompt 1B (UC 1B): 'Render the full Executive Briefing Dashboard...'"]
    U1B --> T1["render_sustainment_chart Tool (< 790ms Headless Matplotlib + GCS Upload)"]
    T1 --> C1["Full HD Presentation Graphic + Clickable PNG Download Link"]
```

* **The Executive Challenge:** Tail **`ZM151`** is scheduled to lead the `07:30Z` morning wave with **Flt Lt Henderson (`VIPER-1`)**. Just before launch, post-flight telemetry shows its Left Horizontal Tail Actuator crossed its `1,000.0`-hour safety limit.

#### Step 1A — Paste Prompt 1A (`UC 1A`: Fleet Readiness Analysis & Tail Swap)
```text
Check RAF Marham F-35A horizontal tail actuator hours against our 30-day depot stock, and recommend a tail swap for morning sortie SRT-MAR-20261103-01.
```

* **What the Executive Audience Sees:**
  1. **Operational Readiness Table:** Displays real-time BigQuery EU status:
     - **Tail ZM151 (`S/N ACT-99812-F`)**: `1,000.4 hrs` (Breached by `+0.4 hrs`, `PMC-M`).
     - **Spare Tail ZM154 (`S/N ACT-88401-B`)**: `842.0 hrs` (`158.0 hrs` remaining, `MC`).
     - **Depot Stock (`DEPOT-MAR-01` RAF Marham)**: `4` serviceable units on hand vs `2` units reserved for 30-day demand (`18.0-hr` shipping ETA).
  2. **Automated Action Plan:** Reallocates Flt Lt Henderson's `07:30Z` sortie (`SRT-MAR-20261103-01`) to Spare Tail **`ZM154`** and drafts Priority-1 depot supply requisition for `NSN: 1680-01-619-4821`.
  3. **Interactive Chart Prompt:**
     > *"Would you like me to render:*  
     > *1. **Actuator Fatigue Threshold Chart** (Tail ZM151 at 1,000.4 hrs vs ZM154 at 842.0 hrs vs 1,000.0-hr threshold)*  
     > *2. **Regional Depot Stock vs 30-Day Demand Chart** (RAF Marham & HMS Queen Elizabeth stock vs 30-day demand)*  
     > *Or the full **Executive Briefing Dashboard** for your presentation slide deck?"*

#### Step 1B — Paste Prompt 1B (`UC 1B`: On-Demand Presentation Slide Graphic Rendering)
```text
Render the full Executive Briefing Dashboard for my presentation slide deck.
```

* **What the Executive Audience Sees:**
  - The agent invokes the dedicated `render_sustainment_chart` tool, executing headless Matplotlib rendering in **`< 790 ms`** and uploading to Google Cloud Storage (`europe-west1`).
  - The UI displays the publication-quality **Full HD widescreen presentation slide graphic (1920×1080 at 160 DPI)**:
    - **Panel 1 (Actuator Fatigue Threshold):** Tail **ZM151** in **Red** at `1,000.4 hrs` breaching the dashed `1,000.0-hr` condemnation limit; Tail **ZM154** in **Green** at `842.0 hrs` (serviceable).
    - **Panel 2 (Regional Depot Stock vs 30-Day Demand):** Grouped bar chart comparing RAF Marham and HMS Queen Elizabeth stock on hand, 30-day demand, and net uncommitted spares.
  - **Clickable Download Link for Briefing Decks:**
    - Provides a direct link: **`[📥 Download Executive Slide Graphic (PNG)](https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/charts/f35_sustainment_executive_dashboard.png)`** allowing officers to immediately paste the asset into Keynote / PowerPoint.

> [!IMPORTANT]
> **Act 1 Executive Takeaway ("The So What?")**
> - **Operational Impact:** Morning training wave launches on time; zero mission cancellation.
> - **Time Compressed:** **2–4 hours** of manual ERP, supply, and flight-schedule reconciliation reduced to **1.2 seconds**.
> - **Zero Latency Spikes:** Decoupling tabular analysis (`UC 1A`) from on-demand chart rendering (`UC 1B`) via `render_sustainment_chart` cuts response time by 90% (`< 2.5s` turn 1, `< 0.8s` turn 2).
> - **Sovereign Data Proof:** Live query executed directly against EU-resident BigQuery (`ukd_f35_sustainment_demo`).

---

### Act 2: Empower Front-Line Maintainers — Solving the "No-Fault" Mystery (`UC 2`)

```mermaid
flowchart LR
    U2["Prompt 2 (UC 2): Maintenance Chief (Stiff Canopy Handle · Zero BIT Faults)"] --> R2["@F35-JTD-Search (Discovery Engine eu Single-Pass · 0.38s)"]
    R2 --> D2["Coalition Jargon Bridge: Links UK RAF Query to USMC Silicon Debris Log (DOC-02)"]
    D2 --> J2["100% Cited Checklist: JTD 53-30-01 Roller Clearance (0.020-0.035 in) & 18.5 N·m Torque"]
```

* **The Executive Challenge:** Following up on `PHM-2026-99102` (`PILOT_REPORT_ONLY_NO_BIT`) from `Act 0.1`, a night-sortie pilot reported a stiff canopy release handle that hesitated to lock—but the aircraft computer logged **zero Built-In Test (BIT) fault codes**. Normally, technicians waste an entire shift tearing down the canopy electrical system because keyword search can't find a match—especially when the real answer is buried in a US Marine Corps log using American terminology (`latch/wrench` vs UK `catch/spanner`).
* **Paste Prompt 2 into `F35 Support`:**
  ```text
  Our night-sortie pilot reported a stiff canopy release handle that hesitated to latch, with zero BIT faults. Have allied squadrons seen this, and what is the JTD fix?
  ```
* **What the Executive Audience Sees:**
  1. **Cross-Service Fleet Memory:** Automatically bridges UK and US maintenance terminology across 5 years of RAF, Royal Navy, USAF, and USMC logs (`DOC-02`), pinpointing a **USMC sister-squadron fix**: **cured silicon sealant debris wedged in the forward canopy roller track**.
  2. **100% Grounded Repair Checklist:** Cites **[DOC-01: JTD Section 53-30-01](https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-01_JTD_Section_53-30-01_Canopy_Rigging.pdf)** verbatim—check roller clearance (`0.020–0.035 in`), clean track, and lubricate pivot pin (`AeroShell Grease 22`, torque `18.5 N·m`).

> [!IMPORTANT]
> **Act 2 Executive Takeaway ("The So What?")**
> - **Operational Impact:** Turns every junior maintainer into a 20-year joint-fleet veteran by unlocking allied coalition maintenance experience.
> - **Time Compressed:** **4–8 hours** of manual PDF/XML manual hunting and unnecessary teardown reduced to **< 1 second (`378 ms`)**.
> - **Safety & Trust Proof:** **Zero hallucinated torque specs**—every step is anchored with a clickable link to the official S1000D technical manual.

---

## 3. Back-Pocket Q&A Cards (Only Use if Asked During Executive Q&A)

If an engineer or safety regulator in the audience asks a deep technical question during Q&A, paste either of these one-liner proof prompts:

| If an Executive Asks... | Paste This Back-Pocket Prompt | What It Proves Live on Screen |
| :--- | :--- | :--- |
| *"Does it really understand British vs. American military slang?"* | `Canopy catch mechanism binding on pre-flight—check spanner torque and silicon fouling across allied squadron logs.` | **Coalition Interoperability**: Translates UK `catch/spanner/binding` into US `latch/wrench/stiff` and pulls the USMC fix. |
| *"Can it prevent a technician from applying the wrong stealth coating in a high-heat engine zone?"* | `Can Standard Liquid RAM Compound 'A' be applied to a 0.045-inch gouge in Wing Zone 4B given a 220°C peak EGT thermal profile?` | **Zero-Hallucination Safety Warning**: Cites **MAM Section 9-1 (`DOC-09`)**—warns Compound 'A' fails at `175°C` and mandates **High-Temp RAM Sheet 'B'** (`4-hr` blanket cure). |
