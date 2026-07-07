"""
사용법 (CodeQuality_Reviewer/ 루트에서 실행): python pipeline/create_input.py
feature_name, code(파일 경로), context(선택), test_project_dir(선택)를 입력하면
runs/{timestamp_uuid}/01_input.json 을 생성한다.

Test_Writer(1-1) create_input.py 의 brief_hash 생성 방식을 그대로 재사용했다.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def build_brief() -> dict:
    print("=== CodeQuality Reviewer — 입력 생성 ===\n")

    feature_name = input("feature_name (필수, 예: TicketService): ").strip()
    if not feature_name:
        raise ValueError("feature_name은 필수입니다.")

    code_path = input("code 파일 경로 (필수, 리뷰할 소스 파일): ").strip()
    if not code_path or not Path(code_path).exists():
        raise ValueError("존재하는 code 파일 경로가 필요합니다.")
    code = Path(code_path).read_text(encoding="utf-8")

    context = input("context (선택, 언어·프레임워크·제약 등, 생략 가능): ").strip()
    test_project_dir = input(
        "test_project_dir (선택, gradle test 로 GREEN 확인할 프로젝트 경로, 생략 가능): "
    ).strip()

    brief: dict = {"feature_name": feature_name, "code": code}
    if context:
        brief["context"] = context
    if test_project_dir:
        brief["test_project_dir"] = test_project_dir

    return brief


def make_brief_hash(brief: dict) -> str:
    serialized = json.dumps(brief, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(serialized).hexdigest()[:16]


def make_run_dir() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:8]
    run_dir = Path("runs") / f"{timestamp}_{short_id}"
    run_dir.mkdir(parents=True)
    return run_dir


def main() -> None:
    brief = build_brief()
    brief_hash = make_brief_hash(brief)

    payload = {
        "brief_hash": brief_hash,
        "brief": brief,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    run_dir = make_run_dir()
    output_path = run_dir / "01_input.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n생성 완료: {output_path}")
    print(f"brief_hash: {brief_hash}")
    print(f"\n실행: python pipeline/main.py {run_dir}")


if __name__ == "__main__":
    main()
