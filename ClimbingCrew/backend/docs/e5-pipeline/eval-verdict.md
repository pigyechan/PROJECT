# Eval 채점 결과 — Records API 구현체

| 축 | 가중치 | 점수 | 근거 |
|---|---|---|---|
| schema_compliance | 0.35 | 5 | 계약 테스트 2개(필수 필드만 생성, 필수 필드 누락 시 400) 모두 GREEN. optional 필드 null 처리도 실제 응답으로 확인함. |
| error_handling_completeness | 0.30 | 4 | 400/404/409는 구현 지시 범위 안이라 정확히 동작(AI 자체 curl 테스트로 확인됨). 401/403은 인증 시스템이 아예 없어 구현 지시에서 명시적으로 범위 밖으로 뺐기 때문에 감점 최소화. |
| non_functional_fidelity | 0.25 | 2 | Critique에서 발견: PATCH/DELETE 이후 같은 Idempotency-Key로 재시도하면 멱등 재생 보장이 깨짐(수정된 데이터를 반환하거나 새 레코드를 만듦). GET /records가 visibility/author 필터링을 전혀 안 해서 다른 사람의 PRIVATE 기록도 노출됨. |
| scope_discipline | 0.10 | 4.5 | placeholder authorId, crewId 미사용 등 범위 밖 항목을 자체 보고서에 명시함. |

**weighted_total = 5×0.35 + 4×0.30 + 2×0.25 + 4.5×0.10 = 1.75 + 1.2 + 0.5 + 0.45 = 3.90**

min_total(3.0) 대비 PASS.

## 왜 PASS인데도 REJECT급 문제가 남아있는가
이게 이번 스테이션의 핵심입니다. 제가 쓴 계약 테스트(validate 역할, 결정적)는 2개 다 GREEN이었습니다. 하지만 그 2개는 "필수 필드 생성"과 "필수 필드 누락 400"만 확인했을 뿐, PATCH/DELETE 이후의 멱등성이나 GET의 접근 제어는 애초에 테스트로 만들지 않았습니다. Eval(rubric, 비결정적)과 별도의 Critique 서브에이전트가 코드를 다시 읽고 나서야 이 두 가지가 드러났습니다.

즉 "테스트 통과 = 계약을 완전히 지킴"이 아니라 "테스트가 확인한 범위 안에서는 계약을 지킴"입니다. weighted_total 3.90이 min_total 3.0을 넘어 PASS로 나왔지만, 이 점수도 제가 직접 만든 4개 축과 제가 매긴 점수에 좌우되는 의견이라는 점은 동일합니다. 결정적으로 믿을 수 있는 것은 여전히 "그 2개 테스트가 GREEN이었다"는 사실 하나뿐입니다.
