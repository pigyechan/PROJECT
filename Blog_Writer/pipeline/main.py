"""
사용법 (Blog_Writer/ 루트에서 실행):
  python pipeline/main.py                              # runs/ 에서 가장 최신 폴더 자동 선택
  python pipeline/main.py runs/20260523_120000_abcd1234   # 특정 run 디렉터리 지정
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from steps.generator import generate
from steps.critique import critique
from steps.evaluator import evaluate
from steps.refine import refine
from steps import validate

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


def _write_publish_md(output_path: Path, run_dir: Path) -> None:
    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    title = artifact.get("title", "").strip()
    summary = artifact.get("summary", "").strip()
    keywords = artifact.get("keywords", [])
    content = artifact.get("content", "").strip()

    lines = []
    if title:
        lines.append(f"# {title}\n")
    if summary:
        lines.append(f"> {summary}\n")
    if keywords:
        lines.append(f"**태그:** {', '.join(f'`{k}`' for k in keywords)}\n")
    if title or summary or keywords:
        lines.append("---\n")
    lines.append(content)

    publish_path = run_dir / "publish.md"
    publish_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"발행용 파일 → {publish_path}")


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

    # Step 1: Gen — 1회만 실행
    output_path, _, _ = get_paths(run_dir, 1)
    print("\n=== [Step 1] Gen: 초안 생성 ===")
    generate(input_path, output_path)
    print(f"완료: {output_path}")

    verdict_path = None

    for iteration in range(1, MAX_ITERATIONS + 1):
        output_path, critique_path, verdict_path = get_paths(run_dir, iteration)

        # Step 2+3: Critique + Eval 병렬 실행 — 둘 다 output만 읽으므로 독립적
        print(f"\n=== [Step 2+3] Critique + Eval 병렬 실행 (iteration {iteration}) ===")
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_critique = executor.submit(critique, output_path, critique_path)
            future_eval = executor.submit(evaluate, output_path, verdict_path)
            future_critique.result()
            future_eval.result()
        print(f"완료: {critique_path}, {verdict_path}")

        # Validate — 코드 기반 이중 검문
        print(f"=== [Step 3-V] Validate: schema/길이/금지어 검증 ===")
        validate.validate_contract(output_path, verdict_path)

        verdict_data = json.loads(verdict_path.read_text(encoding="utf-8"))
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

            # 발행용 마크다운 생성
            _write_publish_md(output_path, run_dir)
            sys.exit(0)

        # 마지막 반복이면 Refine 없이 종료
        if iteration >= MAX_ITERATIONS:
            break

        # Step 4: Refine — 다음 반복을 위한 개선 초안 생성
        next_output_path, _, _ = get_paths(run_dir, iteration + 1)
        print(f"\n=== [Step 4] Refine: 퇴고 (iteration {iteration}) ===")
        refine(output_path, critique_path, verdict_path, next_output_path)

        refined_data = json.loads(next_output_path.read_text(encoding="utf-8"))
        print(f"완료: {next_output_path}")
        print(f"should_iterate: {refined_data['should_iterate']} -- {refined_data['iterate_reason']}")

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
