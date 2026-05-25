import json
import re
from pathlib import Path
from google import genai

client = genai.Client()

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "analyze_system.md"
MODEL = "gemini-2.5-flash-lite"


def analyze(input_path: Path, output_path: Path) -> None:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    user_message = {
        "brief_hash": data["brief_hash"],
        "job_postings": data["job_postings"]
    }

    response = client.models.generate_content(
        model=MODEL,
        contents=json.dumps(user_message, ensure_ascii=False),
        config={"system_instruction": system_prompt}
    )

    raw = re.sub(r"```json\s*", "", response.text)
    raw = re.sub(r"```\s*", "", raw)

    result = json.loads(raw.strip())
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Analyze] 완료 → {output_path.name} | 공고 {len(result['classified'])}개 분류")
