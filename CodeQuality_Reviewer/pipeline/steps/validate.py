# validate.py — 코드 기반 계약 게이트
# 체크 항목: JSON 스키마, 금지 패턴(검증 불가능한 rationale), rubric min_total,
#            (신규) test_project_dir 가 주어지면 실제 gradle test 를 실행해 GREEN 확인.
#
# Test_Writer(1-1) validate.py 의 3개 체크(스키마/금지패턴/품질하한)를 그대로 재사용하고,
# 코드 품질 도메인에 필요한 _check_tests_green 하나만 새로 추가했다.
#
# 설계 결정: 파이프라인이 제안한 diff를 자동으로 코드에 적용(patch)하는 기능은
# v0 범위 밖이다. 대신 test_project_dir 에 있는 "현재" 프로젝트(예: 수작업으로 이미
# 리팩토링을 적용한 TicketService)의 테스트 스위트를 실제로 실행해, 그 저장소가
# 여전히 GREEN인지를 코드로 확인한다 — Test_Writer의 "AI 판정을 코드가 재검증한다"는
# 원칙을 그대로 따른 것이다.

import json
import os
import shutil
import subprocess
import yaml
from pathlib import Path
from jsonschema import validate as jsonschema_validate, ValidationError

_ROOT = Path(__file__).parent.parent.parent
_RUBRIC = yaml.safe_load((_ROOT / "config" / "rubric.yaml").read_text(encoding="utf-8"))

ARTIFACT_SCHEMA = {
    "type": "object",
    "required": ["brief_hash", "violations", "refactor_suggestions", "generated_at"],
    "properties": {
        "brief_hash": {"type": "string", "pattern": "^[a-f0-9]{8,}$"},
        "violations": {
            "type": "array", "minItems": 1,
            "items": {
                "type": "object",
                "required": ["principle", "location", "evidence", "severity"],
                "properties": {
                    "principle": {"type": "string", "minLength": 1},
                    "location":  {"type": "string", "minLength": 1},
                    "evidence":  {"type": "string", "minLength": 1},
                    "severity":  {"type": "string", "enum": ["low", "medium", "high"]},
                },
            },
        },
        "refactor_suggestions": {
            "type": "array", "minItems": 1,
            "items": {
                "type": "object",
                "required": ["technique", "target", "before_sketch", "after_sketch", "rationale"],
                "properties": {
                    "technique":     {"type": "string", "minLength": 1},
                    "target":        {"type": "string", "minLength": 1},
                    "before_sketch": {"type": "string", "minLength": 1},
                    "after_sketch":  {"type": "string", "minLength": 1},
                    "rationale":     {"type": "string", "minLength": 1},
                },
            },
        },
        "generated_at": {"type": "string"},
    },
    "additionalProperties": True,
}

QUALITY_MIN = _RUBRIC.get("min_total", 2.5)

# rationale / after_sketch 에서 허용하지 않는, 검증 불가능한 막연한 긍정 표현
FORBIDDEN_CLAIM_PATTERNS = [
    "should be cleaner",
    "더 좋아진다",
    "더 깔끔해진다",
    "더 나은 코드가 된다",
    "가독성이 좋아짐",
    "품질이 향상됨",
    "더 나아진다",
]

# 이 리포지토리(TicketService)에서 이번 세션에 확인한 설치 경로.
# 다른 환경에서 실행할 경우 JAVA_HOME / GRADLE_HOME 환경변수로 override 한다.
_DEFAULT_JAVA_HOME = r"C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot"
_DEFAULT_GRADLE_BIN = os.path.expandvars(r"%LOCALAPPDATA%\gradle-dist\gradle-8.10.2\bin")
_DEFAULT_GRADLE_USER_HOME = r"C:\gradle-home"


def _check_schema(artifact: dict) -> list[str]:
    try:
        jsonschema_validate(artifact, ARTIFACT_SCHEMA)
        return []
    except ValidationError as e:
        return [f"schema: {e.message}"]


def _check_forbidden_claims(artifact: dict) -> list[str]:
    errors = []
    for suggestion in artifact.get("refactor_suggestions", []):
        for field in ("rationale", "after_sketch"):
            text = suggestion.get(field, "")
            for pattern in FORBIDDEN_CLAIM_PATTERNS:
                if pattern in text:
                    errors.append(
                        f"forbidden_claim: suggestion '{suggestion.get('technique', '?')}' "
                        f"[{field}] — '{pattern}'"
                    )
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


def _check_tests_green(test_project_dir: str | None) -> tuple[list[str], bool | None]:
    """test_project_dir 가 주어지면 그 프로젝트에서 gradle test 를 실제로 실행해
    BUILD SUCCESSFUL 인지 확인한다. 주어지지 않으면 검사를 건너뛴다 (None)."""
    if not test_project_dir:
        return [], None

    project_dir = Path(test_project_dir)
    if not project_dir.exists():
        return [f"tests_green: test_project_dir 이 존재하지 않음 ({test_project_dir})"], False

    gradle_exe = shutil.which("gradle")
    gradle_bin_dir = _DEFAULT_GRADLE_BIN
    if not gradle_exe:
        gradle_exe = str(Path(gradle_bin_dir) / "gradle.bat")

    env = os.environ.copy()
    env["JAVA_HOME"] = os.environ.get("JAVA_HOME", _DEFAULT_JAVA_HOME)
    env["GRADLE_USER_HOME"] = os.environ.get("GRADLE_USER_HOME", _DEFAULT_GRADLE_USER_HOME)
    env["PATH"] = f"{env['JAVA_HOME']}\\bin;{gradle_bin_dir};" + env.get("PATH", "")

    result = subprocess.run(
        [gradle_exe, "test", "--console=plain"],
        cwd=str(project_dir),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    output = result.stdout + result.stderr
    success = "BUILD SUCCESSFUL" in output

    if not success:
        tail = "\n".join(output.strip().splitlines()[-15:])
        return [f"tests_green: gradle test 실패 (test_project_dir={test_project_dir})\n{tail}"], False
    return [], True


def validate_contract(artifact_path: Path, verdict_path: Path, test_project_dir: str | None = None) -> dict:
    artifact = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
    verdict_existing = {}
    if Path(verdict_path).exists():
        verdict_existing = json.loads(Path(verdict_path).read_text(encoding="utf-8"))
    rubric_scores = verdict_existing.get("rubric_scores", {})

    errors = []
    errors += _check_schema(artifact)
    errors += _check_forbidden_claims(artifact)
    errors += _check_quality(rubric_scores)

    tests_green_errors, tests_green = _check_tests_green(test_project_dir)
    errors += tests_green_errors

    verdict = {
        **verdict_existing,
        "contract_errors": errors,
        "tests_green": tests_green,
        "verdict": "REJECT" if errors else "PASS",
    }
    Path(verdict_path).write_text(json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
    status = verdict["verdict"]
    print(f"[Validate] {status} | tests_green={tests_green} | contract_errors: {errors if errors else '없음'}")
    return verdict
