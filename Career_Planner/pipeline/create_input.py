import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "inputs"
BACKGROUND_PATH = Path(__file__).parent.parent / "config" / "user_background.json"
OUTPUT_DIR.mkdir(exist_ok=True)


def get_user_background() -> dict:
    if BACKGROUND_PATH.exists():
        data = json.loads(BACKGROUND_PATH.read_text(encoding="utf-8"))
        print("\n=== 사용자 배경 (config/user_background.json에서 로드) ===")
        print(f"  경력 요약   : {data['experience'][:60]}...")
        print(f"  타깃 도메인 : {data['target_domain']}")
        print(f"  커리어 목표 : {data['career_goal']}")
        print("  (변경하려면 config/user_background.json 파일을 직접 수정하세요)\n")
        return data

    print("\n=== 사용자 배경 입력 ===")
    print("config/user_background.json이 없어 직접 입력합니다.")
    experience = input("경력 요약: ").strip()
    target_domain = input("타깃 도메인 (예: 핀테크 백엔드, 제조IT, 커머스): ").strip()
    career_goal = input("커리어 목표 (예: Java 백엔드 개발자 전환): ").strip()
    return {
        "experience": experience,
        "target_domain": target_domain,
        "career_goal": career_goal
    }


def get_job_postings() -> list:
    postings = []
    print("\n=== 채용공고 입력 ===")
    print("채용 사이트에서 공고 전체 텍스트를 복사해서 붙여넣으세요.")
    print("회사명·직무명은 AI가 자동으로 추출합니다.")
    print("입력 완료: 빈 줄에서 Enter 두 번 → 다음 공고")
    print("전체 완료: 공고 입력 없이 Enter 두 번\n")

    i = 1
    while True:
        print(f"[{i}] 공고 텍스트 붙여넣기 (완료 시 빈 줄 두 번):")
        lines = []
        blank_count = 0
        while True:
            line = input()
            if line == "":
                blank_count += 1
                if blank_count >= 2:
                    break
            else:
                blank_count = 0
            lines.append(line)

        text = "\n".join(lines).rstrip()

        if not text:
            break

        postings.append({"id": i, "text": text})
        print(f"  → 저장됨\n")
        i += 1

    return postings


def main():
    user_background = get_user_background()
    job_postings = get_job_postings()

    if not job_postings:
        print("채용공고가 없습니다. 종료합니다.")
        return

    content_str = json.dumps(
        {"job_postings": job_postings, "user_background": user_background},
        ensure_ascii=False, sort_keys=True
    )
    brief_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]

    data = {
        "brief_hash": brief_hash,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "job_postings": job_postings,
        "user_background": user_background
    }

    output_path = OUTPUT_DIR / f"input_{brief_hash}.json"
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n입력 파일 저장됨: {output_path}")
    print(f"채용공고 {len(job_postings)}개")
    print(f"\n실행 명령어:")
    print(f"  python main.py ../inputs/input_{brief_hash}.json")


if __name__ == "__main__":
    main()
