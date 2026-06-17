# generator.py
# 역할: 자연어 요구사항을 받아 단위 테스트 케이스와 Gherkin 시나리오 초안을 생성한다.
# 평가는 여기서 하지 않는다.

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

_PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
GEN_SYSTEM_PROMPT = (_PROMPTS_DIR / "gen_system.md").read_text(encoding="utf-8")

MODEL = "gemini-3.1-flash-lite"


def generate(input_path: Path, output_path: Path) -> None:
    brief_data = json.loads(input_path.read_text(encoding="utf-8"))
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=MODEL,
        contents=json.dumps(brief_data["brief"], ensure_ascii=False),
        config=types.GenerateContentConfig(system_instruction=GEN_SYSTEM_PROMPT),
    )
    raw = response.text.strip()
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if code_block:
        raw = code_block.group(1).strip()

    parsed = json.loads(raw)
    unit_tests = parsed.get("unit_tests", [])
    scenarios = parsed.get("scenarios", [])

    # content: Critique / Eval 에 전달할 텍스트 표현 (Gen 내부 상태는 포함하지 않음)
    content = json.dumps({"unit_tests": unit_tests, "scenarios": scenarios}, ensure_ascii=False, indent=2)

    artifact = {
        "brief_hash": brief_data["brief_hash"],
        "unit_tests": unit_tests,
        "scenarios": scenarios,
        "content": content,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_model": MODEL,
        # 중요: 자기 평가 점수를 여기 넣지 않는다.
    }
    output_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Gen] unit_tests: {len(unit_tests)}개, scenarios: {len(scenarios)}개")
