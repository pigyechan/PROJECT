"""
기존 콘텐츠를 Blog_Writer Critique → Eval → Validate 파이프라인에 태운다.
Gen 단계를 건너뛰고 직접 content를 주입한다.

사용법 (Blog_Writer/ 루트에서):
  python pipeline/eval_existing.py <content_file.md> [label]
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from steps.critique import critique
from steps.evaluator import evaluate
from steps import validate

RUNS_DIR = Path("runs")


def make_run_dir(label: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = hashlib.sha256(label.encode()).hexdigest()[:8]
    run_dir = RUNS_DIR / f"{ts}_{uid}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def main() -> None:
    if len(sys.argv) < 2:
        print("사용법: python pipeline/eval_existing.py <content_file.md> [label]")
        sys.exit(1)

    content_path = Path(sys.argv[1])
    label = sys.argv[2] if len(sys.argv) >= 3 else content_path.stem
    content = content_path.read_text(encoding="utf-8")

    brief_hash = hashlib.sha256(label.encode()).hexdigest()[:16]
    run_dir = make_run_dir(label)

    # 01_input.json (메타 기록용)
    input_data = {
        "brief_hash": brief_hash,
        "brief": {"label": label, "source_file": str(content_path)},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    (run_dir / "01_input.json").write_text(
        json.dumps(input_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 02_output.json — Gen 건너뜀, 기존 콘텐츠 직접 주입
    output_data = {
        "brief_hash": brief_hash,
        "content": content,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_model": "human",
    }
    output_path = run_dir / "02_output.json"
    output_path.write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    critique_path = run_dir / "02b_critique.json"
    verdict_path = run_dir / "03_verdict.json"

    print(f"\n[{label}] run_dir: {run_dir}")

    print("=== Critique ===")
    critique(output_path, critique_path)
    critique_data = json.loads(critique_path.read_text(encoding="utf-8"))
    for w in critique_data["weaknesses"]:
        print(f"  [{w['axis']}] {w['reason']}")

    print("=== Eval ===")
    evaluate(output_path, verdict_path)

    print("=== Validate ===")
    validate.validate_contract(output_path, verdict_path)

    verdict_data = json.loads(verdict_path.read_text(encoding="utf-8"))
    scores = verdict_data["rubric_scores"]["scores"]
    total = verdict_data["rubric_scores"]["weighted_total"]
    result = verdict_data["verdict"]
    contract_errors = verdict_data.get("contract_errors", [])

    print("\n--- 점수 ---")
    for axis, score in scores.items():
        print(f"  {axis:20s}: {score}")
    print(f"  weighted_total      : {total:.4f}")
    print(f"  verdict             : {result}")
    if contract_errors:
        print(f"  contract_errors     : {contract_errors}")

    print(f"\n결과 저장: {run_dir}")
    return result, total


if __name__ == "__main__":
    main()
