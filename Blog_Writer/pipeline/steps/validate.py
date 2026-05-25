# validate.py — P3 Sprint Contract 실전 구현
# 사용: python validate.py <output.json> <verdict.json>
# 의존: pip install jsonschema pyyaml

import json
import sys
from pathlib import Path
from jsonschema import validate as jsonschema_validate, ValidationError
import yaml

# ----- 1. 스키마 정의 (파이프라인마다 교체) ----
ARTIFACT_SCHEMA = {
	"type": "object",
	"required": ["content", "brief_hash", "generated_at"],
	"properties": {
		"content": {"type": "string", "minLength": 1},
		"brief_hash": {"type": "string", "pattern": "^[a-f0-9]{8,}$"},
		"generated_at": {"type": "string", "format": "date-time"},
		"generator_model": {"type": "string"},
	},
	"additionalProperties": True,
}

_rubric = yaml.safe_load(Path("config/rubric.yaml").read_text(encoding="utf-8"))

LENGTH_MIN = 300
LENGTH_MAX = 4000
QUALITY_MIN = _rubric.get("min_total", 2.5)
BANNED_WORDS = ["무조건", "완벽보장", "절대안전", "반드시성공"]

# ----- 2. 개별 체크 ----
def check_schema(artifact: dict) -> list[str]:
	try:
		jsonschema_validate(artifact, ARTIFACT_SCHEMA)
		return []
	except ValidationError as e:
		return [f"schema: {e.message}"]
		
def check_length(content: str) -> list[str]:
	n = len(content)
	if n < LENGTH_MIN:
		return [f"length: {n} < {LENGTH_MIN}"]
	if n > LENGTH_MAX:
		return [f"length: {n} > {LENGTH_MAX}"]
	return []
	
def check_banned(content: str) -> list[str]:
	return [f"banned: '{w}'" for w in BANNED_WORDS if w in content]
	
def check_quality(rubric_scores: dict) -> list[str]:
	scores = rubric_scores.get("scores", {})
	weights = rubric_scores.get("weights", {})
	if not scores or not weights:
		return ["quality: missing scores or weights"]
	total = sum(scores[k] * weights[k] for k in scores if k in weights)
	if total < QUALITY_MIN:
		return [f"quality: {total:.2f} < {QUALITY_MIN}"]
	return []

# ----- 3. 합친 contract ----

def validate_contract(artifact_path: Path, verdict_path: Path) -> dict:
	artifact = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
	verdict_existing = {}
	if Path(verdict_path).exists():
		verdict_existing = json.loads(Path(verdict_path).read_text(encoding="utf-8"))
	rubric_scores = verdict_existing.get("rubric_scores", {})

	errors = []
	errors += check_schema(artifact)
	errors += check_length(artifact.get("content", ""))
	errors += check_banned(artifact.get("content", ""))
	errors += check_quality(rubric_scores)

	verdict = {
		**verdict_existing,
		"contract_errors": errors,
		"verdict": "REJECT" if errors else "PASS",
	}
	Path(verdict_path).write_text(json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
	return verdict

if __name__ == "__main__":
	out = validate_contract(Path(sys.argv[1]), Path(sys.argv[2]))
	print(json.dumps(out, ensure_ascii=False, indent=2))
    
# QUALITY_MIN, LENGTH_MIN, BANNED_WORDS 만 파이프라인에 맞춰 바꾸면 80% 재사용.
# 스키마 정의는 ARTIFACT_SCHEMA 한 블록을 도메인에 맞게 교체.