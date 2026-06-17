# validate.py — 코드 기반 계약 게이트
# 체크 항목: JSON 스키마, 금지 패턴(Then 절), rubric min_total

import json
import yaml
from pathlib import Path
from jsonschema import validate as jsonschema_validate, ValidationError

_ROOT = Path(__file__).parent.parent.parent
_RUBRIC = yaml.safe_load((_ROOT / "config" / "rubric.yaml").read_text(encoding="utf-8"))

ARTIFACT_SCHEMA = {
    "type": "object",
    "required": ["brief_hash", "unit_tests", "scenarios", "generated_at"],
    "properties": {
        "brief_hash":  {"type": "string", "pattern": "^[a-f0-9]{8,}$"},
        "unit_tests": {
            "type": "array", "minItems": 1,
            "items": {
                "type": "object",
                "required": ["name", "given", "when", "then"],
                "properties": {
                    "name":  {"type": "string", "minLength": 1},
                    "given": {"type": "string", "minLength": 1},
                    "when":  {"type": "string", "minLength": 1},
                    "then":  {"type": "string", "minLength": 1},
                },
            },
        },
        "scenarios": {
            "type": "array", "minItems": 1,
            "items": {
                "type": "object",
                "required": ["title", "given", "when", "then"],
                "properties": {
                    "title": {"type": "string", "minLength": 1},
                    "given": {"type": "string", "minLength": 1},
                    "when":  {"type": "string", "minLength": 1},
                    "then":  {"type": "string", "minLength": 1},
                },
            },
        },
        "generated_at": {"type": "string"},
    },
    "additionalProperties": True,
}

QUALITY_MIN = _RUBRIC.get("min_total", 2.5)

# Then 절에서 허용하지 않는 모호한 단언 패턴
FORBIDDEN_THEN_PATTERNS = [
    "should work",
    "works correctly",
    "정상 동작",
    "올바르게 동작",
    "정상적으로",
    "기대대로",
    "올바른 결과",
    "제대로 동작",
]


def _check_schema(artifact: dict) -> list[str]:
    try:
        jsonschema_validate(artifact, ARTIFACT_SCHEMA)
        return []
    except ValidationError as e:
        return [f"schema: {e.message}"]


def _check_forbidden_then(artifact: dict) -> list[str]:
    errors = []
    for test in artifact.get("unit_tests", []):
        then_text = test.get("then", "")
        for pattern in FORBIDDEN_THEN_PATTERNS:
            if pattern in then_text:
                errors.append(f"forbidden_then: unit_test '{test.get('name', '?')}' — '{pattern}'")
    for scenario in artifact.get("scenarios", []):
        then_text = scenario.get("then", "")
        for pattern in FORBIDDEN_THEN_PATTERNS:
            if pattern in then_text:
                errors.append(f"forbidden_then: scenario '{scenario.get('title', '?')}' — '{pattern}'")
    return errors


def _check_quality(rubric_scores: dict) -> list[str]:
    scores = rubric_scores.get("scores", {})
    weights = rubric_scores.get("weights", {})
    if not scores or not weights:
        return ["quality: scores 또는 weights 없음"]
    total = sum(scores[k] * weights[k] for k in scores if k in weights)
    if total < QUALITY_MIN:
        return [f"quality: {total:.2f} < {QUALITY_MIN}"]
    return []


def validate_contract(artifact_path: Path, verdict_path: Path) -> dict:
    artifact = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
    verdict_existing = {}
    if Path(verdict_path).exists():
        verdict_existing = json.loads(Path(verdict_path).read_text(encoding="utf-8"))
    rubric_scores = verdict_existing.get("rubric_scores", {})

    errors = []
    errors += _check_schema(artifact)
    errors += _check_forbidden_then(artifact)
    errors += _check_quality(rubric_scores)

    verdict = {
        **verdict_existing,
        "contract_errors": errors,
        "verdict": "REJECT" if errors else "PASS",
    }
    Path(verdict_path).write_text(json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
    status = verdict["verdict"]
    print(f"[Validate] {status} | contract_errors: {errors if errors else '없음'}")
    return verdict
