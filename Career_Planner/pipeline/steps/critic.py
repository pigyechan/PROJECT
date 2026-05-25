import json
import re
from pathlib import Path
from google import genai

client = genai.Client()

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "critique_system.md"
MODEL = "gemini-2.5-flash-lite"


def critique(draft_path: Path, output_path: Path) -> None:
    draft_data = json.loads(draft_path.read_text(encoding="utf-8"))
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    # full_text만 전달 (격리 원칙)
    user_message = {"content": draft_data["full_text"]}

    response = client.models.generate_content(
        model=MODEL,
        contents=json.dumps(user_message, ensure_ascii=False),
        config={"system_instruction": system_prompt}
    )

    raw = re.sub(r"```json\s*", "", response.text)
    raw = re.sub(r"```\s*", "", raw)

    result = json.loads(raw.strip())

    if len(result.get("weaknesses", [])) != 3:
        raise ValueError(f"약점 개수 오류: {len(result.get('weaknesses', []))}개 (3개 필요)")

    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Critique] 완료 → {output_path.name}")
