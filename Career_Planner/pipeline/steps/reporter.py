import json
from pathlib import Path
from google import genai

client = genai.Client()

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "report_system.md"
MODEL = "gemini-2.5-flash-lite"


def report(analysis_path: Path, output_path: Path) -> None:
    data = json.loads(analysis_path.read_text(encoding="utf-8"))
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    response = client.models.generate_content(
        model=MODEL,
        contents=json.dumps(data, ensure_ascii=False),
        config={"system_instruction": system_prompt}
    )

    output_path.write_text(response.text, encoding="utf-8")
    print(f"[Report] 완료 → {output_path.name}")
