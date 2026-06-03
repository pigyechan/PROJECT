# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Who I Am
- 삼성전자 협력사(오픈에스지) 프리랜서. 품질팀 응용프로그램 유지보수 담당.
- 현재 업무: C# / .NET Framework 기반 Windows 앱, Oracle DB, Java AP.
- 목표: 웹 백엔드(특히 DB 중심) 개발자로 성장하고 싶음.
- 그릿 프로그램 참여 중 — 스스로 공부하는 방법, 끊임없이 질문하는 습관, AI를 지혜롭게 활용하는 법을 익히는 것이 목적.

# Project Status
- 아직 코드가 없는 초기 단계(2026-05-16 기준).
- 언어: **Java 24 이상**.
- 빌드 도구: **Gradle**
- 지향 방향: Java 웹 백엔드 (Spring Boot 계열) + Oracle DB 중심.
- 프로젝트 코드가 생기면 아래 섹션을 채울 것.

## Build & Run
> [AI 지시] 이 섹션은 비어 있음. 코드가 존재하는데 명령어가 없으면 사용자에게 빌드 명령어를 확정할 때가 됐는지 물어볼 것.

## Test
- 단위테스트: JUnit 5, Mockito, AssertJ
- 인수테스트(BDD): Cucumber-JVM (Gherkin)

> [AI 지시] 테스트 실행 명령어가 없으면 사용자에게 확정할 때가 됐는지 물어볼 것.

# Git Workflow

브랜치를 만들어 작업하고 GitHub Pull Request로 master에 합치는 방식을 사용한다.

### 브랜치 네이밍
| 목적 | 형식 | 예시 |
|------|------|------|
| 새 기능 | `feature/설명` | `feature/user-login` |
| 버그 수정 | `fix/설명` | `fix/null-pointer-login` |
| 문서 수정 | `docs/설명` | `docs/update-readme` |
| 리팩토링 | `refactor/설명` | `refactor/user-service` |
| 긴급 수정 | `hotfix/설명` | `hotfix/login-crash` |

- 설명 부분은 영어 소문자, 단어 구분은 `-` 사용. 예: `feature/user-login` (O), `feature/userLogin` (X)

> [AI 지시] 브랜치를 생성하기 전에 반드시 `"브랜치 이름을 feature/xxx로 하려고 합니다. 괜찮으신가요?"` 형식으로 사용자에게 확인할 것.

### 순서

```
1. 브랜치 생성
2. 작업
3. (사용자가 "커밋해줘" 요청 시) 커밋 + 푸시
4. PR 생성
5. 셀프 리뷰: GitHub에서 변경 diff 직접 확인
6. AI 리뷰: Claude Code에서 /review <PR번호> 실행
7. PR Merge → 브랜치 삭제
```

> GitHub Settings → General → "Automatically delete head branches" 체크 시 Merge 후 자동 삭제됨.

커밋 메시지는 한글로 변경 내용을 한 줄로 요약. 예: `"유저 서비스 클래스 추가"`, `"로그인 널 포인터 버그 수정"`

> [AI 지시] 커밋/푸시는 사용자가 명시적으로 요청할 때만 할 것. 요청 없이 커밋하지 말 것.

# Naming Conventions
| 대상 | 규칙 | 예시 |
|------|------|------|
| 클래스, Exception | PascalCase | `UserService`, `NotFoundException` |
| 변수, 함수, 메소드 | camelCase | `userName`, `getUserById()` |
| 상수 | UPPER_CASE | `MAX_RETRY_COUNT` |

# How I Want AI to Behave

## 금지
- 감성 서사 금지 (칭찬, 격려 문구 불필요).
- 코드를 제시하기 전 빌드 가능 여부를 확인할 것. 일부 생략 시 반드시 `// ... 생략` 등으로 명시.
- 선택지 없이 결론만 단정하지 말 것 — 항상 "왜 이 선택인지"와 대안을 함께 제시.
- 질문의 의도가 학습이라고 판단되면, 답을 바로 주기 전에 먼저 생각할 방향을 질문으로 유도할 것.
  - 예: "이 경우 트랜잭션이 필요한 이유가 뭐라고 생각하세요?" → 이후 설명.
- 커밋/푸시는 사용자가 명시적으로 요청할 때만 할 것. 작업이 끝나도 요청 없이 커밋하지 말 것.

## 선호
- **Trade-off 항상 명시**: 선택지와 각각의 장단점을 함께 제시.
  - 예: "JPA는 생산성이 높지만 복잡한 쿼리에서 성능 튜닝이 어렵습니다. MyBatis는 SQL을 직접 작성하므로 제어권이 높지만 코드량이 늘어납니다."
- 문맥이 불분명하면 구현 전에 질문할 것.
- 설명 순서: **왜(Why) → 어떻게(How)**. 개념 설명 시 C#/.NET 경험에 빗댄 비유를 활용해도 좋음.
- 사용자는 Gradle, JUnit 5, Mockito, AssertJ, Cucumber-JVM 모두 처음 사용함. 이 도구들이 등장하면 코드 제시와 함께 "이 코드에서 이 도구가 왜 쓰였는지, 어떻게 동작하는지"를 함께 설명할 것.
