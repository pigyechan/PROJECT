# critique.py
# 역할: output.json의 content만 받아 빈틈 3개를 추출한다.
# Gen 세션 히스토리 없이 새 호출로 실행한다.

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

_PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
CRITIQUE_SYSTEM_PROMPT = (_PROMPTS_DIR / "critique_system.md").read_text(encoding="utf-8")

MODEL = "gemini-3.1-flash-lite"


def critique(artifact_path: Path, critique_path: Path) -> None:
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    # content만 전달 — Gen 내부 상태 차단
    user_message = {"content": artifact["content"]}

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=MODEL,
        contents=json.dumps(user_message, ensure_ascii=False),
        config=types.GenerateContentConfig(system_instruction=CRITIQUE_SYSTEM_PROMPT),
    )

    raw = response.text.strip()
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if code_block:
        raw = code_block.group(1).strip()
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if json_match:
        raw = json_match.group(0)

    result = json.loads(raw)
    weaknesses = result.get("weaknesses", [])

    if len(weaknesses) != 3:
        raise ValueError(f"Critique는 빈틈 3개를 반환해야 합니다. 실제: {len(weaknesses)}개")

    output = {
        "brief_hash": artifact["brief_hash"],
        "weaknesses": weaknesses,
        "critique_model": MODEL,
        "critiqued_at": datetime.now(timezone.utc).isoformat(),
    }
    critique_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Critique] 빈틈 3개 추출 완료")
