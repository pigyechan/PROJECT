# refine.py
# 역할: 비평 + 평가 점수를 바탕으로 개선된 위반 진단/리팩토링 제안을 생성한다.
# Test_Writer(1-1) refine.py 를 그대로 재사용 (구조 변경 없음, 출력 필드만 교체).

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

_PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
REFINE_SYSTEM_PROMPT = (_PROMPTS_DIR / "refine_system.md").read_text(encoding="utf-8")

MODEL = "gemini-3.1-flash-lite"


def refine(artifact_path: Path, critique_path: Path, verdict_path: Path, output_path: Path) -> None:
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    critique_data = json.loads(critique_path.read_text(encoding="utf-8"))
    verdict_data = json.loads(verdict_path.read_text(encoding="utf-8"))

    user_message = {
        "brief_hash": artifact["brief_hash"],
        "content": artifact["content"],
        "weaknesses": critique_data["weaknesses"],
        "rubric_scores": verdict_data["rubric_scores"]["scores"],
    }

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=MODEL,
        contents=json.dumps(user_message, ensure_ascii=False),
        config=types.GenerateContentConfig(system_instruction=REFINE_SYSTEM_PROMPT),
    )
    raw = response.text.strip()
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if code_block:
        raw = code_block.group(1).strip()
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if json_match:
        raw = json_match.group(0)

    parsed = json.loads(raw)
    violations = parsed.get("violations", [])
    refactor_suggestions = parsed.get("refactor_suggestions", [])
    content = json.dumps(
        {"violations": violations, "refactor_suggestions": refactor_suggestions},
        ensure_ascii=False, indent=2,
    )

    artifact_refined = {
        "brief_hash": artifact["brief_hash"],
        "violations": violations,
        "refactor_suggestions": refactor_suggestions,
        "content": content,
        "applied_fixes": parsed.get("applied_fixes", []),
        "should_iterate": parsed.get("should_iterate", False),
        "iterate_reason": parsed.get("iterate_reason", ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_model": MODEL,
    }
    output_path.write_text(json.dumps(artifact_refined, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Refine] should_iterate={parsed.get('should_iterate')} — {parsed.get('iterate_reason', '')}")
