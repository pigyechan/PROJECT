import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from steps.analyzer import analyze
from steps.reporter import report
from steps.drafter import draft
from steps.critic import critique
from steps.evaluator import evaluate
from steps.validate import validate
from steps.refiner import refine

MAX_ITERATIONS = 3
RUNS_DIR = Path(__file__).parent.parent / "runs"

MEMO_TEMPLATE = """# 무기가 되는 스토리 소화 메모

## 가장 결정적이었던 개념 1개

[책(무기가 되는 스토리)에서 이번 포지셔닝 작성에 가장 결정적이었던 개념을 적으세요]

## 어떻게 적용했는가 (200자 이내)

[위 개념을 이번 포지셔닝 초안에 어떻게 적용했는지 적으세요]

---
*글자수 가이드: 200자 이내*
"""


def run(input_path: Path) -> None:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_") + input_path.stem[:8]
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # 입력 복사
    input_data = json.loads(input_path.read_text(encoding="utf-8"))
    run_input = run_dir / "01_input.json"
    run_input.write_text(json.dumps(input_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Step 1 — Analyze
    analysis_path = run_dir / "02_analysis.json"
    analyze(run_input, analysis_path)

    # Step 2 — Report
    report_path = run_dir / "02b_report.md"
    report(analysis_path, report_path)

    # Step 3 — Draft
    draft_path = run_dir / "03_draft.json"
    draft(run_input, analysis_path, draft_path)

    for iteration in range(1, MAX_ITERATIONS + 1):
        suffix = "" if iteration == 1 else f"_v{iteration}"
        critique_path = run_dir / f"03b_critique{suffix}.json"
        verdict_path = run_dir / f"04_verdict{suffix}.json"

        # Step 4 — Critique
        critique(draft_path, critique_path)

        # Step 5 — Eval
        evaluate(draft_path, verdict_path)

        # Validate
        val_result = validate(draft_path, verdict_path)

        if val_result["status"] == "PASS":
            draft_data = json.loads(draft_path.read_text(encoding="utf-8"))
            md_path = run_dir / f"03_draft{suffix}.md"
            md_path.write_text(draft_data["full_text"], encoding="utf-8")

            final = {
                "status": "PASS",
                "iterations": iteration,
                "deliverables": {
                    "분류_로그": "01_input.json + 02_analysis.json",
                    "시장_패턴_리포트": "02b_report.md",
                    "포지셔닝_초안": md_path.name,
                    "소화_메모_템플릿": "memo_template.md"
                },
                "run_id": run_id
            }
            (run_dir / "05_next.json").write_text(
                json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            (run_dir / "memo_template.md").write_text(MEMO_TEMPLATE, encoding="utf-8")

            print(f"\n{'='*50}")
            print(f"[완료] PASS — {iteration}회 반복 | run: {run_id}")
            print(f"  채용공고 분류 로그 : 01_input.json + 02_analysis.json")
            print(f"  시장 패턴 리포트   : {report_path.name}")
            print(f"  포지셔닝 초안      : {md_path.name}")
            print(f"  소화 메모 템플릿   : memo_template.md")
            print(f"{'='*50}")
            return

        if iteration < MAX_ITERATIONS:
            next_draft_path = run_dir / f"03_draft_v{iteration + 1}.json"
            refine(draft_path, critique_path, verdict_path, next_draft_path)
            draft_path = next_draft_path
        else:
            verdict_data = json.loads(verdict_path.read_text(encoding="utf-8"))
            regen = {
                "status": "REJECT",
                "reason": f"최대 반복 횟수({MAX_ITERATIONS}회) 도달",
                "final_scores": verdict_data["scores"],
                "weighted_total": verdict_data["weighted_total"],
                "contract_errors": val_result["contract_errors"],
                "run_id": run_id
            }
            (run_dir / "99_regen_request.json").write_text(
                json.dumps(regen, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"\n[실패] REJECT — {MAX_ITERATIONS}회 반복 후 미통과 | run: {run_id}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python main.py <input_json_path>")
        print("예시:   python main.py ../inputs/input_abc123.json")
        sys.exit(1)
    run(Path(sys.argv[1]))
