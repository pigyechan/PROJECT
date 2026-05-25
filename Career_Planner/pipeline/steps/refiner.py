import json
import re
from pathlib import Path
from google import genai

client = genai.Client()

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "refine_system.md"
MODEL = "gemini-2.5-flash-lite"


def refine(draft_path: Path, critique_path: Path, verdict_path: Path, output_path: Path) -> dict:
    draft_data = json.loads(draft_path.read_text(encoding="utf-8"))
    critique_data = json.loads(critique_path.read_text(encoding="utf-8"))
    verdict_data = json.loads(verdict_path.read_text(encoding="utf-8"))
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    user_message = {
        "brief_hash": draft_data["brief_hash"],
        "content": draft_data["full_text"],
        "user_background_hint": {
            "target_company": draft_data["target_company"],
            "guide_competencies": draft_data["guide_competencies"]
        },
        "weaknesses": critique_data["weaknesses"],
        "rubric_scores": verdict_data["scores"]
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
    print(f"[Refine] 완료 → {output_path.name} | should_iterate: {result.get('should_iterate')}")
    return result
