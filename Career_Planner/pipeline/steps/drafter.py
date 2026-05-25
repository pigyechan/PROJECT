import json
import re
from pathlib import Path
from google import genai

client = genai.Client()

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "draft_system.md"
MODEL = "gemini-2.5-flash-lite"


def draft(input_path: Path, analysis_path: Path, output_path: Path) -> None:
    input_data = json.loads(input_path.read_text(encoding="utf-8"))
    analysis_data = json.loads(analysis_path.read_text(encoding="utf-8"))
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    user_message = {
        "brief_hash": input_data["brief_hash"],
        "user_background": input_data["user_background"],
        "patterns": analysis_data["patterns"]
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
    print(f"[Draft] 완료 → {output_path.name}")
