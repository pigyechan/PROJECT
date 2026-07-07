# generator.py
# 역할: 소스 코드를 받아 SOLID 위반 후보 + 리팩토링 제안 초안을 생성한다.
# 평가는 여기서 하지 않는다.
# Test_Writer(1-1) generator.py 의 구조를 그대로 재사용하고, 출력 필드만
# (unit_tests/scenarios) -> (violations/refactor_suggestions) 로 교체했다.

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
    violations = parsed.get("violations", [])
    refactor_suggestions = parsed.get("refactor_suggestions", [])

    # content: Critique / Eval 에 전달할 텍스트 표현 (Gen 내부 상태는 포함하지 않음)
    content = json.dumps(
        {"violations": violations, "refactor_suggestions": refactor_suggestions},
        ensure_ascii=False, indent=2,
    )

    artifact = {
        "brief_hash": brief_data["brief_hash"],
        "violations": violations,
        "refactor_suggestions": refactor_suggestions,
        "content": content,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_model": MODEL,
        # 중요: 자기 평가 점수를 여기 넣지 않는다.
    }
    output_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Gen] violations: {len(violations)}개, refactor_suggestions: {len(refactor_suggestions)}개")
