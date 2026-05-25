# generator.py
# 역할: 입력 브리프를 받아 산출물을 만든다. 평가는 여기서 하지 않는다.

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

GEN_SYSTEM_PROMPT = Path("prompts/gen_system.md").read_text(encoding="utf-8")


def generate(input_path: Path, output_path: Path) -> None:
    brief_data = json.loads(input_path.read_text(encoding="utf-8"))
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=json.dumps(brief_data["brief"], ensure_ascii=False),
        config=types.GenerateContentConfig(
            system_instruction=GEN_SYSTEM_PROMPT,
        ),
    )
    raw = response.text.strip()
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if code_block:
        raw = code_block.group(1).strip()
    try:
        parsed = json.loads(raw)
        content = parsed.get("content", raw)
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)
    except json.JSONDecodeError:
        content = raw

    artifact = {
        "brief_hash": brief_data["brief_hash"],
        "content": content,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_model": "gemini-2.5-flash-lite",
        # 중요: 자기 평가 점수를 여기 넣지 않는다.
    }
    output_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
