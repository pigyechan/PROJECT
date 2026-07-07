"""
사용법 (CodeQuality_Reviewer/ 루트에서 실행):
  python pipeline/main.py                              # runs/ 에서 가장 최신 폴더 자동 선택
  python pipeline/main.py runs/20260707_120000_abcd1234   # 특정 run 디렉터리 지정

Test_Writer(1-1) pipeline/main.py 를 그대로 재사용했다 (골격 변경 없음).
유일한 차이: validate_contract 호출 시 01_input.json 의 brief.test_project_dir 을
읽어서 넘겨준다 — 코드 품질 도메인에서만 필요한 "실제 테스트 GREEN 확인"을 위해서다.
"""

import json
import sys
from pathlib import Path

from steps.generator import generate
from steps.critique import critique
from steps.evaluator import evaluate
from steps.refine import refine
from steps.validate import validate_contract

MAX_ITERATIONS = 3


def find_latest_run() -> Path:
    runs_dir = Path("runs")
    candidates = [p for p in runs_dir.iterdir() if p.is_dir() and (p / "01_input.json").exists()]
    if not candidates:
        raise FileNotFoundError("runs/ 아래에 01_input.json이 있는 폴더가 없습니다.")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def get_paths(run_dir: Path, iteration: int) -> tuple[Path, Path, Path]:
    """반복 횟수에 따라 output / critique / verdict 경로를 반환한다."""
    if iteration == 1:
        return (
            run_dir / "02_output.json",
            run_dir / "02b_critique.json",
            run_dir / "03_verdict.json",
        )
    return (
        run_dir / f"02_output_v{iteration}.json",
        run_dir / f"02b_critique_v{iteration}.json",
        run_dir / f"03_verdict_v{iteration}.json",
    )


def main() -> None:
    if len(sys.argv) >= 2:
        run_dir = Path(sys.argv[1])
    else:
        run_dir = find_latest_run()
        print(f"run_dir 자동 선택: {run_dir}")

    input_path = run_dir / "01_input.json"
    if not input_path.exists():
        print(f"ERROR: {input_path} 가 없습니다.", file=sys.stderr)
        sys.exit(1)

    input_data = json.loads(input_path.read_text(encoding="utf-8"))
    test_project_dir = input_data.get("brief", {}).get("test_project_dir")

    # Step 1: Gen — 1회만 실행
    output_path, _, _ = get_paths(run_dir, 1)
    print("\n=== [Step 1] Gen: SOLID 위반 진단 + 리팩토링 제안 초안 생성 ===")
    generate(input_path, output_path)
    print(f"완료: {output_path}")

    verdict_path = None

    for iteration in range(1, MAX_ITERATIONS + 1):
        output_path, critique_path, verdict_path = get_paths(run_dir, iteration)

        # Step 2: Critique — 새 호출, content만 전달
        print(f"\n=== [Step 2] Critique: 시니어 리뷰어 비평 (iteration {iteration}) ===")
        critique(output_path, critique_path)
        print(f"완료: {critique_path}")

        # Step 3: Eval — rubric 기반 채점
        print(f"=== [Step 3] Eval: 품질 평가 (iteration {iteration}) ===")
        evaluate(output_path, verdict_path)
        print(f"완료: {verdict_path}")

        # Step 4: Validate — 코드 기반 계약 게이트 (+ 실제 gradle test GREEN 확인)
        print(f"=== [Step 4] Validate: 스키마/금지패턴/품질/테스트 GREEN 검증 ===")
        verdict_data = validate_contract(output_path, verdict_path, test_project_dir)

        weighted_total = verdict_data["rubric_scores"]["weighted_total"]
        result = verdict_data["verdict"]
        contract_errors = verdict_data.get("contract_errors", [])

        print(f"\n판정: {result}  (weighted_total={weighted_total}, iteration={iteration})")
        if contract_errors:
            print(f"contract_errors: {contract_errors}")

        if result == "PASS":
            next_path = run_dir / "04_next.json"
            next_payload = {
                "brief_hash": verdict_data["brief_hash"],
                "status": "PASS",
                "output": str(output_path),
                "critique": str(critique_path),
                "verdict": str(verdict_path),
                "iterations": iteration,
            }
            next_path.write_text(json.dumps(next_payload, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"PASS → {next_path}")
            sys.exit(0)

        # 마지막 반복이면 Refine 없이 종료
        if iteration >= MAX_ITERATIONS:
            break

        # Refine — 다음 반복을 위한 개선 초안 생성
        next_output_path, _, _ = get_paths(run_dir, iteration + 1)
        print(f"\n=== [Refine] 진단/제안 개선 (iteration {iteration}) ===")
        refine(output_path, critique_path, verdict_path, next_output_path)
        print(f"완료: {next_output_path}")

    # 최종 REJECT
    regen_path = run_dir / "99_regen_request.json"
    final_verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    regen_payload = {
        "brief_hash": final_verdict["brief_hash"],
        "status": "REJECT",
        "weighted_total": final_verdict["rubric_scores"]["weighted_total"],
        "scores": final_verdict["rubric_scores"]["scores"],
        "iterations": MAX_ITERATIONS,
        "action": "재생성 필요",
    }
    regen_path.write_text(json.dumps(regen_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"REJECT → {regen_path}")
    sys.exit(1)


if __name__ == "__main__":
    main()
