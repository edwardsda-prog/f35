---
issue_id: "ISS-006"
title: "Replace Default Robot Icon on Gemini Enterprise Agent with Resized RAF F-35 (ZM151) Aircraft Logo"
date: "2026-11-04"
status: "VERIFIED_IN_PROD"
severity: "P3-MEDIUM"
domain: "Infra-EU"
sub_agent: "f35_sustainment_coordinator"
guardrails_impacted:
  - "REG-01"
vv_test_cases:
  - "TC-SQ-01"
commit_or_pr: "HEAD"
author: "Antigravity Agent"
---

# [ISS-006] Replace Default Robot Icon on Gemini Enterprise Agent with Resized RAF F-35 (ZM151) Aircraft Logo

> **Quick Reference Summary:** `agents-cli publish gemini` hardcodes the Material Symbol robot SVG (`smart_toy/default/24px.svg`) as the agent `icon` when registering ADK agents in Gemini Enterprise. Cropped and resized `gs://f35sa/f35-RAF.png` (`1408x768`, 1.64 MB) into a `128x128` (`35 KB`) square avatar (`app/assets/f35_raf_icon_128.png`) framing RAF F-35B `ZM151` and patched agent `1346484961578743940` via the Discovery Engine `eu` REST API (`?updateMask=icon`).

---

## 1. Symptom & Operational Context

### 1.1 Observed Failure / Degradation
- **Symptom:** When browsing or selecting **F-35 Fleet Sustainment Coordinator** (`ID: 1346484961578743940`) in Gemini Enterprise (`f35-support`), the agent avatar displays a generic robot icon (`https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/smart_toy/default/24px.svg`) instead of the RAF F-35 aircraft logo (`gs://f35sa/f35-RAF.png`).
- **Impact:** Visual branding and UX polish in the Gemini Enterprise agent gallery (`f35-support` engine in `locations/eu`).
- **Detection Source:** Live user browsing in Gemini Enterprise (`f35-support`).

### 1.2 Reproduction Steps / Triggering Input
1. **Environment:** `GOOGLE_CLOUD_PROJECT=antig-dave`, `GOOGLE_CLOUD_REGION=europe-west1`, Discovery Engine (`eu`), Engine `f35-support`.
2. **Command or Query:**
   ```bash
   GET https://eu-discoveryengine.googleapis.com/v1alpha/projects/284046449012/locations/eu/collections/default_collection/engines/f35-support/assistants/default_assistant/agents/1346484961578743940
   ```
3. **Observed vs. Expected Behavior:**
   - **Observed:** `"icon": {"uri": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/smart_toy/default/24px.svg"}`
   - **Expected:** Resized RAF F-35 (`ZM151`) aircraft logo from `gs://f35sa/f35-RAF.png` rendered as the agent's `icon`.

---

## 2. Root Cause Analysis (RCA)

### 2.1 Primary Root Cause
In `google-agents-cli` (`google/agents/cli/publish/cmd_publish.py`, lines 814 and 910), the `publish gemini` command does not expose a CLI flag for custom agent icons and hardcodes the payload field:
```python
"icon": {
    "uri": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/smart_toy/default/24px.svg"
}
```
Additionally, the source image `gs://f35sa/f35-RAF.png` is a widescreen `1408x768` (`1,643,083` bytes) RGB PNG, which requires square aspect-ratio framing and downsampling (`128x128`, ~35 KB) before base64-encoding into `Agent.icon.content` on the Discovery Engine `v1alpha` API.

### 2.2 Architectural Guardrail / Invariant Analysis
| Guardrail / Test ID | Pre-Fix State | Post-Fix State | Notes |
| :--- | :---: | :---: | :--- |
| `REG-01` | `✅ COMPLIANT` | `✅ COMPLIANT` | Patched directly against `eu-discoveryengine.googleapis.com` (`locations/eu`) and stored in `gs://antig-dave-f35-staging-europe-west1/assets/`. |

---

## 3. Fix & Code Changes Applied

### 3.1 Summary of Resolution
1. Downloaded `gs://f35sa/f35-RAF.png` (`1408x768`, featuring RAF F-35B `ZM151` with RAF roundels and tail markings), framed the full nose-to-afterburner aircraft into a seamless `1:1` square, and downsampled with `Image.Resampling.LANCZOS` to `128x128` (`34,987` bytes, `app/assets/f35_raf_icon_128.png`) and `256x256` (`121,496` bytes, `app/assets/f35_raf_icon_256.png`).
2. Uploaded the resized icons to `gs://f35sa/f35_raf_icon_128.png`, `gs://f35sa/f35_raf_icon_256.png`, and `gs://antig-dave-f35-staging-europe-west1/assets/`.
3. Patched agent `1346484961578743940` (`F-35 Fleet Sustainment Coordinator`) in Gemini Enterprise (`f35-support`) via `PATCH .../agents/1346484961578743940?updateMask=icon` using base64 `"icon": {"content": "<base64_png>"}`.
4. Added `ensure_gemini_enterprise_agent_icon()` to [`scripts/setup_demo_infra.py`](../../scripts/setup_demo_infra.py) so re-running infrastructure provisioning or agent publishing automatically restores the RAF F-35 (`ZM151`) icon.

### 3.2 Modified Files & Symbols
| File Path | Symbol / Function / Class Modified | Change Type | Description |
| :--- | :--- | :---: | :--- |
| `[app/assets/f35_raf_icon_128.png](../../app/assets/f35_raf_icon_128.png)` | Binary PNG asset (`128x128`) | `Added` | Square-framed, Lanczos-resized RAF F-35B (`ZM151`) avatar icon (35 KB). |
| `[app/assets/f35_raf_icon_256.png](../../app/assets/f35_raf_icon_256.png)` | Binary PNG asset (`256x256`) | `Added` | High-DPI 256x256 square RAF F-35B (`ZM151`) icon. |
| `[scripts/setup_demo_infra.py](../../scripts/setup_demo_infra.py)` | `ensure_gemini_enterprise_agent_icon` | `Added` | Idempotent Discovery Engine `eu` `PATCH ?updateMask=icon` helper for agent `1346484961578743940`. |

### 3.3 Key Code Diff
```diff
--- a/scripts/setup_demo_infra.py
+++ b/scripts/setup_demo_infra.py
@@ -532,6 +532,48 @@ def ensure_gemini_enterprise_app(
+def ensure_gemini_enterprise_agent_icon(
+    project_id: str,
+    de_location: str = "eu",
+    engine_id: str = "f35-support",
+    agent_display_name: str = "F-35 Fleet Sustainment Coordinator",
+    icon_path: Path | None = None,
+) -> dict[str, Any]:
+    """Patch the Gemini Enterprise registered ADK agent icon with the RAF F-35 (ZM151) aircraft logo."""
```

---

## 4. Dead Ends & Approaches Rejected

> [!WARNING]
> **Do Not Repeat These Approaches:** Future agents and engineers modifying these files must avoid the rejected approaches documented below.

| Rejected Approach | Why It Failed or Was Rejected | Guardrail / Constraint Violated |
| :--- | :--- | :--- |
| Passing raw `gs://f35sa/f35-RAF.png` in `icon.uri` | Discovery Engine `Agent.icon.uri` requires browser-accessible HTTPS or inline `icon.content` base64 bytes, and the uncropped `1408x768` (1.64 MB) image is non-square and oversized for an avatar icon. | UI rendering & payload size |
| Tight 768x768 center crop without framing | Clips the nose cone and horizontal stabilizer tips when Gemini Enterprise applies a circular avatar mask. Framing `x=230..1230` (`1000x1000`) preserves the entire nose-to-afterburner silhouette of `ZM151`. | Visual quality |

---

## 5. Verification, Regression Tests & Benchmarks

### 5.1 Automated Test & Evaluation Verification
```bash
uv run pytest tests/unit/ -q
```

### 5.2 Before vs. After Telemetry / Verification Metrics
| Metric / Check | Pre-Fix Baseline | Post-Fix Result | Target / SLA Gate | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| Agent `1346484961578743940` `icon` | `smart_toy/default/24px.svg` (Robot SVG) | `icon.content` (`46,652` base64 chars, `128x128` RAF `ZM151` PNG) | RAF F-35 Aircraft Logo (`gs://f35sa/f35-RAF.png`) | **✅ PASS** |

---

## 6. Prevention & Guardrail Updates

- [x] **Idempotent Infra Hook Added:** Added `ensure_gemini_enterprise_agent_icon` in [`scripts/setup_demo_infra.py`](../../scripts/setup_demo_infra.py).
- [x] **Index Updated:** Added `ISS-006` entry to [`docs/issues/INDEX.md`](./INDEX.md).
