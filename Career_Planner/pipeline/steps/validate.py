import json
import yaml
from pathlib import Path

RUBRIC_PATH = Path(__file__).parent.parent.parent / "config" / "rubric.yaml"


def validate(draft_path: Path, verdict_path: Path) -> dict:
    draft_data = json.loads(draft_path.read_text(encoding="utf-8"))
    verdict_data = json.loads(verdict_path.read_text(encoding="utf-8"))
    rubric = yaml.safe_load(RUBRIC_PATH.read_text(encoding="utf-8"))

    errors = []

    # 가중합 재계산
    weights = {axis: cfg["weight"] for axis, cfg in rubric["axes"].items()}
    recalc = sum(verdict_data["scores"].get(axis, 0) * w for axis, w in weights.items())
    validator_threshold = rubric["pass_threshold"]["validator"]
    if recalc < validator_threshold:
        errors.append(f"quality: {recalc:.2f} < {validator_threshold}")

    # 글자 수 검사
    full_text = draft_data.get("full_text", "")
    min_chars = rubric["validator_rules"]["min_chars"]
    max_chars = rubric["validator_rules"]["max_chars"]
    char_count = len(full_text)
    if not (min_chars <= char_count <= max_chars):
        errors.append(f"length: {char_count}자 (허용: {min_chars}~{max_chars}자)")

    # 금지어 검사
    for word in rubric["validator_rules"]["forbidden_words"]:
        if word in full_text:
            errors.append(f"forbidden_word: '{word}'")

    result = {
        "recalc_weighted_total": round(recalc, 4),
        "char_count": char_count,
        "contract_errors": errors,
        "status": "PASS" if not errors else "REJECT"
    }

    print(f"[Validate] {result['status']} | 재계산: {result['recalc_weighted_total']} | 글자수: {char_count} | 오류: {errors}")
    return result
