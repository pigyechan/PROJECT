# evaluator.py
# 역할: output.json을 입력으로 받아 점수와 판정을 verdict.json으로 낸다.
# Generator의 대화 히스토리나 내부 상태를 받지 않는다.

import json
import os
import re
import yaml
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

EVAL_SYSTEM_PROMPT = Path("prompts/eval_system.md").read_text(encoding="utf-8")
RUBRIC = yaml.safe_load(Path("config/rubric.yaml").read_text(encoding="utf-8"))

assert abs(sum(a["weight"] for a in RUBRIC["axes"]) - 1.0) < 1e-6, \
    "rubric weight sum is not 1.0"


def evaluate(artifact_path: Path, verdict_path: Path) -> None:
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    weights = {a["name"]: a["weight"] for a in RUBRIC["axes"]}
    axis_names = list(weights.keys())

    user_message = {
        "rubric": RUBRIC,
        "artifact": artifact["content"],
        # brief_hash만 참조용. 내용은 Evaluator가 독립 판단한다.
        "brief_hash": artifact["brief_hash"],
        "instruction": (
            "위 rubric의 각 axis(name 필드)를 1~5점으로 평가하세요. "
            "반드시 JSON만 반환하세요: "
            "{\"scores\": {\"<axis_name>\": <1-5>, ...}, \"reasons\": {\"<axis_name>\": \"<reason>\", ...}}"
        ),
    }
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=json.dumps(user_message, ensure_ascii=False),
        config=types.GenerateContentConfig(
            system_instruction=EVAL_SYSTEM_PROMPT,
            temperature=0.2,
        ),
    )
    raw = response.text.strip()
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if code_block:
        raw = code_block.group(1).strip()
    # JSON 객체 부분만 추출
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if json_match:
        raw = json_match.group(0)

    eval_result = json.loads(raw)

    scores: dict[str, float] = {}
    if "scores" in eval_result and isinstance(eval_result["scores"], dict):
        scores = {k: float(v) for k, v in eval_result["scores"].items() if k in axis_names}
    elif "axes" in eval_result:
        for axis in eval_result["axes"]:
            name = axis.get("name", "")
            if name in axis_names:
                scores[name] = float(axis.get("score", 0))

    weighted_total = sum(scores.get(k, 0) * weights[k] for k in axis_names)
    min_total = RUBRIC.get("min_total", 2.5)

    verdict = {
        "brief_hash": artifact["brief_hash"],
        "rubric_scores": {
            "scores": scores,
            "weights": weights,
            "weighted_total": round(weighted_total, 4),
        },
        "evaluator_model": "gemini-3.1-flash-lite",
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "verdict": "PASS" if weighted_total >= min_total else "REJECT",
    }
    verdict_path.write_text(json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
