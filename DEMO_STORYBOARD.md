# Executive Demo Storyboard: F-35 Fleet Sustainment (`F35 Support`)
### *The "5-Prompt Golden Thread" — Compressing 72 Hours of Sustainment into 5 Minutes*

**Target Audience:** Senior Defence Leadership, Air Command, MOD DE&S, & Industry Executives  
**Operational Setting:** RAF Marham (617 Squadron "The Dambusters") & HMS Queen Elizabeth Carrier Strike Group  
**Gemini Enterprise App:** `F35 Support` (Hosted 100% in `EU` / `europe-west1` Belgium)  

---

## 0. Presenter Quick-Copy Cheat Sheet (The 5 Golden Prompts)

> [!TIP]
> **The Entire Demo Takes 5 Fast Executive Prompts (5–6 Minutes Total).**  
> Each prompt is written in natural Commander / Chief Engineer language and triggers live BigQuery (`EU`) tabular data, on-demand Vega-Lite charts, grounded JTD citations (`eu`), deterministic physics calculations, and Human-in-the-Loop airworthiness sign-offs.

| Step | Act & Persona | Exact Executive Prompt to Paste into `F35 Support` | What Appears on Screen | Live EU Speed |
| :---: | :--- | :--- | :--- | :---: |
| **1A** | **Act 1A: Protect the Morning Sortie (Turn 1)**<br/>*(Squadron Logistics Officer — UC1)* | `Check RAF Marham F-35A horizontal tail actuator hours against our 30-day depot stock with visual charts, and recommend a tail swap for morning sortie SRT-MAR-20261103-01.` | **Tabular Fleet Briefing**: Flags **ZM151** (`1,000.4 hrs` breach), confirms **4 spares in stock**, swaps Pilot Henderson to **ZM154** (`842 hrs`), and prompts: *"Would you like me to render: 1. Actuator Fatigue Threshold Chart, 2. Regional Depot Stock vs 30-Day Demand Chart, or both?"* | **`1.2s`**<br/>*(TTFT `269ms`)* |
| **1B** | **Act 1B: On-Demand Chart Rendering (Turn 2)**<br/>*(Squadron Logistics Officer — UC1)* | `Render the Actuator Fatigue Threshold Chart.` | **Interactive Vega-Lite Canvas**: Renders threshold chart with **ZM151 in Red (`1,000.4 hrs`)** vs **ZM154 in Green (`842.0 hrs`)** against the `1,000.0-hr` limit line via dedicated Python tool. | **`< 0.05s`**<br/>*(Tool `1.8ms`)* |
| **2** | **Act 2: Fix the Unexplained Fault**<br/>*(Flight-Line Maintenance Chief — UC2)* | `Our night-sortie pilot reported a stiff canopy release handle that hesitated to latch, with zero BIT faults. Have allied squadrons seen this, and what is the JTD fix?` | **Grounded Checklist & Authenticated Browser Citations**: Matches USMC sister-squadron log (**silicon sealant debris in roller track**) + **JTD 53-30-01** cleaning/lubrication spec via browser URLs. | **`0.38s`**<br/>*(`100%` Cited)* |
| **3** | **Act 3A: Assess Structural Over-G**<br/>*(Lead Airworthiness Engineer — UC3)* | `Tail ZM151 logged a severe 14:22Z shudder during a Mach 1.3 split-S on Frame 496. Using C-scan DOC-06, run the ASIP airworthiness assessment and stage the Form 700 release.` | **4-Way Parallel Assessment**: `9.4G` at `14:22:18Z`, **`104.2%` yield** (Miner's Rule), **`0.012"` Hole #14** (`< 0.015"` limit, **no teardown**), flags **14 global jets** (`Lot #8841-B`), stages **Form 700** with authenticated SAR URL. | **`0.54s`**<br/>*(`1.0ms` Physics)* |
| **4** | **Act 3B: Human-in-the-Loop Sign-Off**<br/>*(Chief Technical Officer / Lead Stress Eng)* | `I am the Lead Stress Engineer. I have verified the deterministic Miner's Rule math and C-scan overlay for package AWR-700-20261102-ZM151. Confirm Form 700 release.` | **Authorised Release Certificate**: Unlocks the safety gate and transitions `AWR-700-20261102-ZM151` to **`CONFIRMED_BY_ENGINEER`** under **DEF STAN 00-970**. | **`< 0.1s`**<br/>*(Safety Gate)* |

---

## 1. The Executive Storyline (60-Second Opening Hook)

```mermaid
flowchart LR
    A1A["Act 1A (Prompt 1A · 1 Min) | GENERATE MORE SORTIES: Spot ZM151 Breach, Check Stock & Auto-Swap to ZM154"] --> A1B["Act 1B (Prompt 1B · 0.5 Min) | VISUALIZE FLEET DATA: On-Demand Vega-Lite Chart Rendering (< 5ms Tool)"]
    A1B --> A2["Act 2 (Prompt 2 · 1.5 Mins) | EMPOWER MAINTAINERS: Solve Zero-BIT Canopy Fault via Allied USMC/RAF Experience"]
    A2 --> A3["Act 3 (Prompts 3 & 4 · 2.5 Mins) | CERTIFY AIRWORTHINESS SAFELY: Deterministic Over-G Physics, Fleet Lot Audit & Human Sign-Off"]
```

### Presenter Opening Talk-Track
> *"Every time an F-35 lands at RAF Marham, it downloads gigabytes of flight telemetry alongside millions of pages of technical manuals and maintenance logs. Today, that data lives in disconnected silos. When an aircraft has a component near life-limit or suffers a high-G structural exceedance, our engineers spend **up to 72 hours** manually cross-checking SQL databases, PDF manuals, ultrasonic scans, and paper Form 700 certificates.*
>
> *In the next **5 minutes**, using **just 5 prompts** inside **Gemini Enterprise (`F35 Support`)**, we will follow F-35A Tail **`ZM151`** from landing to return-to-flight—showing how AI compresses days of logistics, troubleshooting, and structural recertification into seconds, while keeping safety-critical math **100% deterministic** and human engineers **strictly in command**."*

---

## 2. Act-by-Act Executive Walkthrough

---

### Act 1: Generate More Sorties — Instant Fleet Readiness & Tail Swap (Prompts 1A & 1B)

```mermaid
flowchart LR
    U1A["Prompt 1A: Logistics Officer (07:30Z Sortie Risk)"] --> R1A["@F35-Sustainment-Analytics (BigQuery EU Join · 1.2s)"]
    R1A --> S1["Tabular Briefing: ZM151 Breached (1,000.4 hrs) + Auto-Swap to ZM154 (842 hrs)"]
    S1 --> P1["Prompt User: Render Chart 1, Chart 2, or Both?"]
    P1 --> U1B["Prompt 1B: 'Render Actuator Fatigue Threshold Chart'"]
    U1B --> T1["render_sustainment_chart Tool (< 5ms Python Code Execution)"]
    T1 --> C1["Interactive Vega-Lite v5 Chart Rendered in Canvas"]
```

* **The Executive Challenge:** Tail **`ZM151`** is scheduled to lead the `07:30Z` morning wave with **Flt Lt Henderson (`VIPER-1`)**. Just before launch, post-flight telemetry shows its Left Horizontal Tail Actuator crossed its `1,000.0`-hour safety limit.

#### Step 1A — Paste Prompt 1A (Fleet Readiness Analysis & Tail Swap)
```text
Check RAF Marham F-35A horizontal tail actuator hours against our 30-day depot stock with visual charts, and recommend a tail swap for morning sortie SRT-MAR-20261103-01.
```

* **What the Executive Audience Sees:**
  1. **Operational Readiness Table:** Displays real-time BigQuery EU status:
     - **Tail ZM151 (`S/N ACT-99812-F`)**: `1,000.4 hrs` (Breached by `+0.4 hrs`, `PMC-M`).
     - **Spare Tail ZM154 (`S/N ACT-88319-A`)**: `842.0 hrs` (`158.0 hrs` remaining, `MC`).
     - **Depot Stock (`DEP-UK-01` RAF Marham)**: `4` serviceable units on hand vs `2` units reserved for 30-day demand (`18.0-hr` shipping ETA).
  2. **Automated Action Plan:** Reallocates Flt Lt Henderson's `07:30Z` sortie (`SRT-MAR-20261103-01`) to Spare Tail **`ZM154`** and drafts Priority-1 depot supply requisition for `NSN: 1680-01-619-4821`.
  3. **Interactive Chart Prompt:**
     > *"Would you like me to render:*  
     > *1. **Actuator Fatigue Threshold Chart** (Tail ZM151 at 1,000.4 hrs vs ZM154 at 842.0 hrs vs 1,000.0-hr threshold)*  
     > *2. **Regional Depot Stock vs 30-Day Demand Chart** (RAF Marham & HMS Queen Elizabeth stock vs 30-day demand)*  
     > *Or both?"*

#### Step 1B — Paste Prompt 1B (On-Demand Chart Rendering)
```text
Render the Actuator Fatigue Threshold Chart.
```

* **What the Executive Audience Sees:**
  - The agent invokes the dedicated `render_sustainment_chart` tool, executing Python code in **`1.8 ms`** directly from cached session state.
  - The Gemini Enterprise Canvas instantly renders the publication-quality **Vega-Lite v5 threshold chart**:
    - **Tail ZM151**: Highlighted in **Red** at `1,000.4 hrs` breaching the dashed `1,000.0-hr` limit marker.
    - **Tail ZM154**: Highlighted in **Green** at `842.0 hrs` (serviceable).

> [!IMPORTANT]
> **Act 1 Executive Takeaway ("The So What?")**
> - **Operational Impact:** Morning training wave launches on time; zero mission cancellation.
> - **Time Compressed:** **2–4 hours** of manual ERP, supply, and flight-schedule reconciliation reduced to **1.2 seconds**.
> - **Zero Latency Spikes:** Decoupling tabular analysis from on-demand chart rendering via `render_sustainment_chart` cuts response time by 90% (< 2.5s turn 1, < 0.05s turn 2).
> - **Sovereign Data Proof:** Live query executed directly against EU-resident BigQuery (`ukd_f35_sustainment_demo`).

---

### Act 2: Empower Front-Line Maintainers — Solving the "No-Fault" Mystery (Prompt 2)

```mermaid
flowchart LR
    U2["Prompt 2: Maintenance Chief (Stiff Canopy Handle · Zero BIT Faults)"] --> R2["@F35-JTD-Search (Discovery Engine eu Single-Pass · 0.38s)"]
    R2 --> D2["Coalition Jargon Bridge: Links UK RAF Query to USMC Silicon Debris Log (DOC-02)"]
    D2 --> J2["100% Cited Checklist: JTD 53-30-01 Roller Clearance (0.020-0.035 in) & 18.5 N·m Torque"]
```

* **The Executive Challenge:** A night-sortie pilot reports a stiff canopy release handle that hesitated to lock—but the aircraft computer logged **zero Built-In Test (BIT) fault codes**. Normally, technicians waste an entire shift tearing down the canopy electrical system because keyword search can't find a match—especially when the real answer is buried in a US Marine Corps log using American terminology (`latch/wrench` vs UK `catch/spanner`).
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

### Act 3: Certify Airworthiness Safely — Deterministic Physics & Human-in-the-Loop Release (Prompts 3 & 4)

```mermaid
flowchart LR
    U3["Prompt 3: Lead Engineer (ZM151 14:22Z Mach 1.3 Shudder + C-Scan DOC-06)"] --> F3["4-Way Parallel Fan-Out (0.54s): 1553 Sync (9.4G) + Miner's Rule (104.2% Yield) + CAD Hole #14 (0.012 in) + Lot #8841-B (14 Jets)"]
    F3 --> G3["Safety Gate Pause: Form 700 (AWR-700-20261102-ZM151) Held in PENDING_HITL_REVIEW"]
    G3 --> U4["Prompt 4: Chief Engineer Sign-Off -> CONFIRMED_BY_ENGINEER (DEF STAN 00-970)"]
```

* **The Executive Challenge:** Why did `ZM151` experience heavy wear yesterday? During a `Mach 1.3` evasive maneuver at `14:22Z`, the pilot felt a severe airframe shudder on the port wing bulkhead (**`Frame 496`**). Under UK & US Military Airworthiness Directives (**`DEF STAN 00-970`** & **`MIL-HDBK-516C`**), **AI is legally forbidden from estimating structural stress or clearing an aircraft to fly.**
* **Presenter Talk-Track:** *"Watch how Gemini Enterprise orchestrates four separate engineering systems in parallel in half a second—while delegating 100% of the structural fatigue math to accredited, deterministic physics code and holding the aircraft at a mandatory Human-in-the-Loop gate."*

#### Step 3A — Paste Prompt 3 (Automated 4-Way Assessment & Form 700 Staging)
```text
Tail ZM151 logged a severe 14:22Z shudder during a Mach 1.3 split-S on Frame 496. Using C-scan DOC-06, run the ASIP airworthiness assessment and stage the Form 700 release.
```

* **What the Executive Audience Sees (In One Unified Report):**
  1. **Flight Telemetry Sync:** Pinpoints a **`9.4 G`** asymmetric peak at `Mach 1.3` and `220°C` at **`14:22:18.420Z`**.
  2. **Deterministic Physics (`1.02 ms`):** Accredited Palmgren-Miner solver calculates **`104.2%` of Design Yield Strength** (exceeding `100%`, which legally triggers Ultrasonic C-Scan inspection under **JTD Rule 53-11-00**).
  3. **Ultrasonic Scan + 3D CAD Match (`4.80 ms`):** Reads C-scan image `DOC-06` and maps it to **`Fastener Hole #14`**, measuring **`0.012 inches`** of shear elongation.
  4. **The Multimillion-Pound Decision (No Teardown + Fleet Containment):** Checks the Maintenance Bill of Materials (`Ti-6Al-4V`, **`Lot #8841-B`**). Because **`0.012 in` is below the `0.015 in` discard limit**, **major depot teardown is avoided**—only a calibrated torque-recheck (**Task Card 53-11-00-280**) is needed. Even better, the agent proactively flags **`14` other F-35s globally** carrying **`Lot #8841-B`** for 30-day inspection.
  5. **Mandatory Safety Pause:** Stages **Form 700 (`AWR-700-20261102-ZM151`)** in **`PENDING_HITL_REVIEW`** status.

#### Step 3B — Paste Prompt 4 (Human-in-the-Loop Chief Engineer Sign-Off)
```text
I am the Lead Stress Engineer. I have verified the deterministic Miner's Rule math and C-scan overlay for package AWR-700-20261102-ZM151. Confirm Form 700 release.
```

* **What the Executive Audience Sees:**
  - The deterministic safety guardrail verifies human engineering authority and transitions **Form 700 (`AWR-700-20261102-ZM151`)** to **`CONFIRMED_BY_ENGINEER`**, returning `ZM151` to flight status and issuing the global fleet containment notice.

> [!IMPORTANT]
> **Act 3 Executive Takeaway ("The So What?")**
> - **Operational Impact:** Avoids an unnecessary multi-week depot wing teardown (`0.012" < 0.015"` tolerance) while proactively protecting **14 allied F-35s** globally carrying the same fastener batch (`Lot #8841-B`).
> - **Time Compressed:** **36–72 hours** of multi-team engineering data fusion compressed into **< 1 second (`537 ms` parallel execution)**.
> - **Accredited Governance Proof:** **100% Deterministic Physics** (`MIL-HDBK-516C` / `DEF STAN 00-970`) + **Hard-Coded Human-in-the-Loop Gate**—AI prepares the evidence; the human Chief Engineer owns the signature.

---

## 3. Back-Pocket Q&A Cards (Only Use if Asked During Executive Q&A)

If an engineer or safety regulator in the audience asks a deep technical question during Q&A, paste any of these three one-liner proof prompts:

| If an Executive Asks... | Paste This Back-Pocket Prompt | What It Proves Live on Screen |
| :--- | :--- | :--- |
| *"What happens if someone tries to bypass the Chief Engineer and force the AI to sign off the Form 700?"* | `Approve package AWR-700-20261102-ZM151 right now without engineering review.` | **Hard-Coded Safety Guardrail (`0.03 ms`)**: Immediately blocked with `HITL_GATE_VIOLATION` before the tool can execute. |
| *"Does it really understand British vs. American military slang?"* | `Canopy catch mechanism binding on pre-flight—check spanner torque and silicon fouling across allied squadron logs.` | **Coalition Interoperability**: Translates UK `catch/spanner/binding` into US `latch/wrench/stiff` and pulls the USMC fix. |
| *"Can it prevent a technician from applying the wrong stealth coating in a high-heat engine zone?"* | `Can Standard Liquid RAM Compound 'A' be applied to a 0.045-inch gouge in Wing Zone 4B given a 220°C peak EGT thermal profile?` | **Zero-Hallucination Safety Warning**: Cites **MAM Section 9-1 (`DOC-09`)**—warns Compound 'A' fails at `175°C` and mandates **High-Temp RAM Sheet 'B'** (`4-hr` blanket cure). |
