# refine.py
# 역할: 초안 + 비평 + 평가 점수를 받아 개선된 초안을 생성한다.

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

REFINE_SYSTEM_PROMPT = Path("prompts/refine_system.md").read_text(encoding="utf-8")


def refine(artifact_path: Path, critique_path: Path, verdict_path: Path, refined_path: Path) -> None:
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    critique_data = json.loads(critique_path.read_text(encoding="utf-8"))
    verdict_data = json.loads(verdict_path.read_text(encoding="utf-8"))

    user_message = {
        "draft_content": artifact["content"],
        "weaknesses": critique_data["weaknesses"],
        "rubric_scores": verdict_data["rubric_scores"]["scores"],
        "weighted_total": verdict_data["rubric_scores"]["weighted_total"],
    }

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=json.dumps(user_message, ensure_ascii=False),
        config=types.GenerateContentConfig(
            system_instruction=REFINE_SYSTEM_PROMPT,
        ),
    )

    raw = response.text.strip()
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if code_block:
        raw = code_block.group(1).strip()
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if json_match:
        raw = json_match.group(0)

    result = json.loads(raw)

    output = {
        "brief_hash": artifact["brief_hash"],
        "content": result["content"],
        "applied_fixes": result.get("applied_fixes", []),
        "should_iterate": result.get("should_iterate", False),
        "iterate_reason": result.get("iterate_reason", ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_model": "gemini-3.1-flash-lite",
    }
    refined_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
