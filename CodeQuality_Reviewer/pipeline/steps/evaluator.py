# evaluator.py
# 역할: output.json을 받아 rubric 4축 점수와 판정을 verdict.json으로 낸다.
# Generator / Critique 의 히스토리나 내부 상태를 받지 않는다.
# Test_Writer(1-1) evaluator.py 를 그대로 재사용 (구조 변경 없음, rubric/prompt만 교체).

import json
import os
import re
import yaml
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

_ROOT = Path(__file__).parent.parent.parent
EVAL_SYSTEM_PROMPT = (_ROOT / "prompts" / "eval_system.md").read_text(encoding="utf-8")
RUBRIC = yaml.safe_load((_ROOT / "config" / "rubric.yaml").read_text(encoding="utf-8"))

assert abs(sum(a["weight"] for a in RUBRIC["axes"]) - 1.0) < 1e-6, \
    "rubric weight 합이 1.0이 아닙니다."

MODEL = "gemini-3.1-flash-lite"


def evaluate(artifact_path: Path, verdict_path: Path) -> None:
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    weights = {a["name"]: a["weight"] for a in RUBRIC["axes"]}
    axis_names = list(weights.keys())

    user_message = {
        "rubric": RUBRIC,
        "artifact": artifact["content"],
        # brief_hash는 참조용만. Evaluator는 내용을 독립 판단한다.
        "brief_hash": artifact["brief_hash"],
        "instruction": (
            "위 rubric의 각 axis(name 필드)를 1~5점으로 평가하세요. "
            "반드시 JSON만 반환하세요: "
            "{\"scores\": {\"<axis_name>\": <1-5>, ...}, \"reasons\": {\"<axis_name>\": \"<reason>\", ...}}"
        ),
    }
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=MODEL,
        contents=json.dumps(user_message, ensure_ascii=False),
        config=types.GenerateContentConfig(system_instruction=EVAL_SYSTEM_PROMPT),
    )
    raw = response.text.strip()
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if code_block:
        raw = code_block.group(1).strip()
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if json_match:
        raw = json_match.group(0)

    eval_result = json.loads(raw)
    scores: dict[str, float] = {}
    if "scores" in eval_result and isinstance(eval_result["scores"], dict):
        scores = {k: float(v) for k, v in eval_result["scores"].items() if k in axis_names}

    weighted_total = sum(scores.get(k, 0) * weights[k] for k in axis_names)
    min_total = RUBRIC.get("min_total", 2.5)

    verdict = {
        "brief_hash": artifact["brief_hash"],
        "rubric_scores": {
            "scores": scores,
            "weights": weights,
            "weighted_total": round(weighted_total, 4),
        },
        "reasons": eval_result.get("reasons", {}),
        "evaluator_model": MODEL,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "verdict": "PASS" if weighted_total >= min_total else "REJECT",
    }
    verdict_path.write_text(json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Eval] weighted_total={weighted_total:.4f}, verdict={verdict['verdict']}")
