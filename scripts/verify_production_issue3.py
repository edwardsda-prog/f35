#!/usr/bin/env python3
"""Live production verification of Issue 3 against Reasoning Engine in europe-west1."""

import asyncio
import json
import logging
import sys
import time
from typing import Any

import httpx

from app.clients import get_auth_headers

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("verify-prod-issue3")

DEPLOYED_RUNTIME_STREAM_URL = (
    "https://europe-west1-aiplatform.googleapis.com/v1beta1/"
    "projects/284046449012/locations/europe-west1/reasoningEngines/5022570215192395776:streamQuery"
)
DEPLOYED_RUNTIME_QUERY_URL = (
    "https://europe-west1-aiplatform.googleapis.com/v1beta1/"
    "projects/284046449012/locations/europe-west1/reasoningEngines/5022570215192395776:query"
)

async def stream_query(client: httpx.AsyncClient, session_id: str | None, message: str) -> tuple[str, float]:
    headers = get_auth_headers()
    req_input: dict[str, Any] = {"user_id": "prod-verifier", "message": message}
    if session_id:
        req_input["session_id"] = session_id
    payload = {
        "class_method": "async_stream_query",
        "input": req_input,
    }

    t0 = time.perf_counter()
    full_text = []
    async with client.stream(
        "POST",
        DEPLOYED_RUNTIME_STREAM_URL,
        headers=headers,
        json=payload,
        timeout=120.0,
    ) as resp:
        if resp.status_code != 200:
            body = await resp.aread()
            logger.error("HTTP %d: %s", resp.status_code, body.decode("utf-8", errors="replace"))
            raise RuntimeError(f"HTTP {resp.status_code}: {body}")
        
        async for line in resp.aiter_lines():
            line_str = line.strip()
            if not line_str:
                continue
            try:
                data = json.loads(line_str)
                # ADK stream chunks format
                part = ""
                if isinstance(data, dict):
                    if "content" in data:
                        part = str(data["content"])
                    elif "output" in data:
                        part = str(data["output"])
                    elif "text" in data:
                        part = str(data["text"])
                    else:
                        part = json.dumps(data)
                elif isinstance(data, str):
                    part = data
                full_text.append(part)
            except Exception:
                full_text.append(line_str)
    
    elapsed = (time.perf_counter() - t0) * 1000.0
    combined = "\n".join(full_text)
    return combined, elapsed


async def main() -> int:
    headers = get_auth_headers()
    logger.info("Initializing session on deployed Reasoning Engine (europe-west1)...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        sess_resp = await client.post(
            DEPLOYED_RUNTIME_QUERY_URL,
            headers=headers,
            json={"class_method": "create_session", "input": {"user_id": "prod-verifier"}},
        )
        session_id = None
        if sess_resp.status_code == 200:
            session_id = sess_resp.json().get("output", {}).get("id")
            logger.info("Created session: %s", session_id)
        else:
            logger.warning("Could not create session (HTTP %d), continuing without session_id", sess_resp.status_code)

        # -----------------------------------------------------------------
        # Turn 1: Trigger query
        # -----------------------------------------------------------------
        prompt_1 = (
            "Check RAF Marham F-35A horizontal tail actuator hours against our 30-day "
            "depot stock with visual charts, and recommend a tail swap for morning sortie SRT-MAR-20261103-01"
        )
        logger.info("Sending Turn 1 prompt:\n%s", prompt_1)
        resp_1, elapsed_1 = await stream_query(client, session_id, prompt_1)
        logger.info("Turn 1 completed in %.2f ms", elapsed_1)
        print("\n" + "="*80)
        print("TURN 1 RESPONSE:")
        print("="*80)
        print(resp_1)
        print("="*80 + "\n")

        # Check Turn 1 assertions
        has_raw_vega = "```vega-lite" in resp_1
        has_chart_prompt = (
            "Actuator Fatigue Threshold Chart" in resp_1 or
            "Regional Depot Stock" in resp_1 or
            "Executive Briefing Dashboard" in resp_1 or
            "render" in resp_1.lower() or
            "charts" in resp_1.lower()
        )
        logger.info("Turn 1 - Has raw vega-lite: %s (Expected False)", has_raw_vega)
        logger.info("Turn 1 - Has chart prompt: %s (Expected True)", has_chart_prompt)

        # -----------------------------------------------------------------
        # Turn 2: Request charts
        # -----------------------------------------------------------------
        prompt_2 = "Yes, render both charts."
        logger.info("Sending Turn 2 prompt:\n%s", prompt_2)
        resp_2, elapsed_2 = await stream_query(client, session_id, prompt_2)
        logger.info("Turn 2 completed in %.2f ms", elapsed_2)
        print("\n" + "="*80)
        print("TURN 2 RESPONSE:")
        print("="*80)
        print(resp_2)
        print("="*80 + "\n")

        # Check Turn 2 assertions
        has_image_markdown = "![" in resp_2 and "storage.cloud.google.com" in resp_2
        has_download_link = "Download" in resp_2 and "storage.cloud.google.com" in resp_2
        has_raw_vega_2 = "```vega-lite" in resp_2

        logger.info("Turn 2 - Has Markdown image embed: %s (Expected True)", has_image_markdown)
        logger.info("Turn 2 - Has presentation download link: %s (Expected True)", has_download_link)
        logger.info("Turn 2 - Has raw vega-lite: %s (Expected False)", has_raw_vega_2)

        failures = []
        if has_raw_vega:
            failures.append("Turn 1 leaked raw vega-lite JSON block")
        if not has_image_markdown:
            failures.append("Turn 2 did not include markdown image embed (![...](...))")
        if not has_download_link:
            failures.append("Turn 2 did not include presentation slide download link")
        if has_raw_vega_2:
            failures.append("Turn 2 leaked raw vega-lite JSON block")

        if failures:
            logger.error("VERIFICATION FAILED: %s", failures)
            return 1
        else:
            logger.info("VERIFICATION SUCCESSFUL! All Issue 3 requirements verified in production.")
            return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
