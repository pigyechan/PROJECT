import json
import re
import yaml
from pathlib import Path
from google import genai

client = genai.Client()

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "eval_system.md"
RUBRIC_PATH = Path(__file__).parent.parent.parent / "config" / "rubric.yaml"
MODEL = "gemini-2.5-flash-lite"


def evaluate(draft_path: Path, verdict_path: Path) -> None:
    draft_data = json.loads(draft_path.read_text(encoding="utf-8"))
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    rubric = yaml.safe_load(RUBRIC_PATH.read_text(encoding="utf-8"))

    # content + brief_hash만 전달 (격리 원칙)
    user_message = {
        "content": draft_data["full_text"],
        "brief_hash": draft_data["brief_hash"],
        "rubric": rubric
    }

    response = client.models.generate_content(
        model=MODEL,
        contents=json.dumps(user_message, ensure_ascii=False),
        config={"system_instruction": system_prompt}
    )

    raw = re.sub(r"```json\s*", "", response.text)
    raw = re.sub(r"```\s*", "", raw)

    result = json.loads(raw.strip())
    verdict_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Eval] 완료 → {verdict_path.name} | weighted_total: {result['weighted_total']} | {result['status']}")
