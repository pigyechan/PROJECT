"""
사용법: python create_input.py
topic, materials, tone을 입력하면 runs/{timestamp_uuid}/01_input.json 을 생성한다.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def build_brief() -> dict:
    print("=== Blog Writer — 입력 생성 ===\n")

    topic = input("topic (필수): ").strip()
    if not topic:
        raise ValueError("topic은 필수입니다.")

    print("materials (한 줄에 하나씩 입력, 빈 줄로 완료):")
    materials = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        materials.append(line)

    tone = input("tone (예: 초보자 친화적, 전문가용, 생략 가능): ").strip()

    brief: dict = {"topic": topic}
    if materials:
        brief["materials"] = materials
    if tone:
        brief["tone"] = tone

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


if __name__ == "__main__":
    main()
