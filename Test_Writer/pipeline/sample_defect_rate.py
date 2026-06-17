"""
DefectRateCalculator 샘플 입력 생성기.
실행: python pipeline/sample_defect_rate.py
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


BRIEF = {
    "feature_name": "DefectRateCalculator",
    "requirements": (
        "calculateDefectRate(defective, total): 불량 수와 전체 수를 입력받아 불량률(%)을 반환한다.\n"
        "  - 공식: (defective / total) * 100\n"
        "  - total이 0 이하이면 IllegalArgumentException('전체 수는 1 이상이어야 합니다.')를 던진다.\n"
        "  - defective가 음수이면 IllegalArgumentException('불량 수는 0 이상이어야 합니다.')를 던진다.\n"
        "  - defective가 total을 초과하면 IllegalArgumentException('불량 수는 전체 수를 초과할 수 없습니다.')를 던진다.\n"
        "\n"
        "evaluateGrade(defectRate): 불량률(double)을 받아 품질 등급 문자열을 반환한다.\n"
        "  - defectRate < 0 또는 defectRate > 100이면 IllegalArgumentException을 던진다.\n"
        "  - defectRate < 1.0 이면 '양호'를 반환한다.\n"
        "  - 1.0 <= defectRate < 5.0 이면 '주의'를 반환한다.\n"
        "  - defectRate >= 5.0 이면 '불량'을 반환한다."
    ),
    "context": "Java 클래스. JUnit 5 + Gherkin(Cucumber) 스타일 테스트 케이스 생성 대상.",
}


def main() -> None:
    brief_hash = hashlib.sha256(
        json.dumps(BRIEF, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()[:16]

    payload = {
        "brief_hash": brief_hash,
        "brief": BRIEF,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:8]
    run_dir = Path("runs") / f"{timestamp}_{short_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    output_path = run_dir / "01_input.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"생성 완료: {output_path}")
    print(f"brief_hash: {brief_hash}")
    print(f"\n실행: python pipeline/main.py {run_dir}")


if __name__ == "__main__":
    main()
