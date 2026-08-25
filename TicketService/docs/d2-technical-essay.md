# D-2: 기술 에세이 (데이터 기반 4-Step)

> **상태**: D-5 하네스(`docs/d5-writing-harness/`) 통과 및 퇴고 완료. 발행(블로그 게시)만 남음 — 발행 후 아래 "발행 정보"에 링크 추가.

## 발행 전 초안

# 인터페이스 하나가 막아준 회귀 버그 — 결제 수단을 추가했는데 기존 코드가 한 줄도 안 바뀐 이유

### 문제 정의

TicketService에 새로운 요구사항이 들어왔다 — 카드 결제뿐 아니라 포인트로도 티켓을 예약 결제할 수 있어야 한다는 것이었다. 문제는 "포인트 결제 로직을 어떻게 짤 것인가"가 아니라, **"이 새 기능을 추가하는 과정에서 이미 검증된 카드 결제 로직을 건드리지 않을 수 있는가"**였다. 만약 결제 로직이 `TicketService` 안에 하드코딩되어 있었다면, 포인트 결제를 추가하기 위해 그 메서드 본문에 if-else 분기를 새로 끼워 넣어야 했을 것이다. 그 경우 이미 테스트를 통과하고 실제로 잘 작동하던 카드 결제 코드를, 관련 없는 새 기능을 추가하려다가 실수로 함께 망가뜨릴 위험이 있었다.

### 증거/관찰

`TicketService`의 생성자를 보면, 필드 타입이 구체적인 결제사 이름(`TossPaymentAdapter`)이 아니라 추상화된 `PaymentGateway` 인터페이스로 되어 있었다.

```java
// PaymentGateway.java — 결제라는 "능력"만 정의한 인터페이스. 구체적인 결제사 이름이 없다.
public interface PaymentGateway {
    boolean charge(int amount, PaymentInfo info);
}

// TicketService.java — 구체 클래스가 아니라 이 인터페이스 타입으로만 필드를 갖는다.
public class TicketService implements TicketReservationUseCase {
    private final PaymentGateway paymentGateway;   // ← TossPaymentAdapter가 아니라 인터페이스

    public TicketService(UserRepository userRepository, TicketRepository ticketRepository, PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
        ...
    }
}
```

이걸 보고 "결제 수단이 무엇이든, `PaymentGateway`를 구현하는 새 클래스 하나만 추가하면 안전하게 끼워 넣을 수 있을 것"이라고 예측했다. 이 예측이 맞다면, 포인트 결제를 추가했을 때 신규 파일만 늘고 기존 파일은 전혀 손대지 않아도 될 것이었다.

### 대안 분석과 의사결정

if-else 방식과 Port/Adapter 방식, 두 가지를 놓고 봤을 때 Port/Adapter 방식을 선택했다. 실제로 추가한 어댑터는 이렇게 완전히 독립된 새 클래스 하나였다.

```java
// PointPaymentAdapter.java — 신규 파일. PaymentGateway를 구현할 뿐, TicketService는 이 클래스의 존재조차 모른다.
public class PointPaymentAdapter implements PaymentGateway {
    private int balance;

    public PointPaymentAdapter(int balance) {
        this.balance = balance;
    }

    @Override
    public boolean charge(int amount, PaymentInfo info) {
        if (balance < amount) {
            return false;
        }
        balance -= amount;
        return true;
    }
}
```

다만 이 선택에는 대가가 있다 — 파일이 하나(`TicketService`)에 다 모여 있는 게 아니라, 인터페이스(`PaymentGateway`)와 그걸 구현하는 여러 클래스(`TossPaymentAdapter`, `PointPaymentAdapter`)로 쪼개지기 때문에, 코드를 처음 보는 사람 입장에서는 "실제로 무슨 일이 일어나는지" 파악하려면 인터페이스와 구현체 사이를 왔다갔다 해야 한다. 파일 개수도 늘어나서, 단순한 기능치고 과하게 분리되어 있다는 인상을 줄 수 있다.

그럼에도 이 방식을 선택한 이유는, 결제라는 도메인이 **돈이 오가는 만큼 기존 로직의 회귀 버그(regression) 비용이 크다**고 판단했기 때문이다. 코드를 읽기 조금 더 번거로워지는 대가를 치르더라도, 이미 검증된 카드 결제 로직을 새 기능 추가 때마다 다시 열어보지 않아도 된다는 안전성이 더 중요하다고 봤다.

### 검증

이 예측이 맞았는지는 감이 아니라 두 가지 구체적인 증거로 확인했다.

첫째, 실제로 변경된 파일 목록(`git diff --stat`)을 확인했다.

```
 .../docs/new-requirement-point-payment.md          | 50 +++++++++++++++++++++
 .../src/main/java/ticket/PointPaymentAdapter.java  | 25 +++++++++++
 .../test/java/ticket/PointPaymentAdapterTest.java  | 51 ++++++++++++++++++++++
 .../ticket/TicketServiceWithPointPaymentTest.java  | 46 +++++++++++++++++++
 .../test-logs/test-log-07-point-payment-ocp.txt    | 33 ++++++++++++++
 5 files changed, 205 insertions(+)
```

전부 **신규 생성(+)**뿐이고, `TicketService.java`를 포함한 기존 파일 삭제/수정 줄은 **단 한 줄도 없다.**

둘째, 기존에 있던 카드 결제 테스트(`TicketServiceTest`)를 포함해 전체 테스트를 다시 돌렸을 때 **11개 전부 GREEN**으로 통과했다 — 이 테스트들은 이번에 전혀 수정하지 않았는데도 여전히 통과했다는 것이, 기존 카드 결제 로직이 이번 변경으로 전혀 영향받지 않았음을 보여주는 증거다.

만약 파일 개수가 예상보다 많았거나, 기존 테스트 중 하나라도 깨졌다면, "결합이 `PaymentGateway` 경계 안에 갇혔다"는 예측은 틀린 것이었다. 두 증거가 모두 예측과 정확히 일치했기 때문에, 이 설계가 실제로 안전한 확장 지점 역할을 했다고 확신할 수 있었다.

## 4-Step 자가 점검 메모 (제출물)

이 글은 문제 정의 → 증거/관찰 → 대안 분석과 의사결정 → 검증의 4단계 구조를 그대로 따랐다. 문제 정의 단계에서는 인터페이스가 없었다면 기존 카드 결제 로직을 직접 수정해야 했을 거라는 반사실적 상황을 제시해 위험을 구체화했다. 증거/관찰 단계에서는 PaymentGateway가 추상 인터페이스로 되어 있다는 근거를 먼저 제시하고, 그 예측을 뒷받침하는 실제 수치(신규 파일 3개, 기존 파일 수정 0줄)를 이어 붙였다. 대안 분석 단계에서는 Port/Adapter 방식을 선택한 이유뿐 아니라 파일이 여러 개로 쪼개져 복잡해 보일 수 있다는 트레이드오프까지 솔직히 적어, 장점만 나열하는 교과서식 서술을 피했다. 검증 단계에서는 "안 바뀌었다"는 주장을 감이 아니라 신규 파일 개수, 기존 테스트 11개 GREEN이라는 구체적 수치로 뒷받침했다. 4단계 전체가 하나의 예측(변경이 PaymentGateway 경계 안에 갇힐 것이다)을 세우고, 그 예측이 맞았는지를 실제 파일 diff와 테스트 결과로 확인하는 하나의 흐름으로 이어진다는 점에서 '추정 → 소거 → 확신 → 검증'의 논리 구조를 갖췄다고 판단했다.

## D-5 하네스 판정 로그

`docs/d5-writing-harness/`의 rubric·프롬프트로, 이 글이 어떻게 쓰였는지 전혀 모르는 독립된 새 세션(Claude Code 서브에이전트) 2개에게 Critique와 Eval을 각각 맡겼다.

**Eval**: message_clarity 4, four_step_fidelity 4, no_fluff 2, reader_alignment 2 → 가중합 3.2, PASS.

**Critique 3건과 본인 판단**:

| # | axis | 지적 | 판단 | 이유 |
|---|---|---|---|---|
| 1 | four_step_fidelity | "증거/관찰"에서 이미 검증 결과(파일 3개, 테스트 11개)를 먼저 제시해 "검증" 단계와 경계가 흐려짐 | **채택** | 직접 재확인 결과 사실이었음. "증거/관찰"에서 예측까지만 남기고 결과 수치는 삭제, "검증"에서 처음 등장하도록 수정함 |
| 2 | no_fluff | 파일 3개·테스트 11개라는 동일 수치가 "증거/관찰"과 "검증"에서 반복 | **채택** | 1번과 같은 원인이라 함께 수정됨 |
| 3 | reader_alignment | 제목("막아준 회귀 버그")은 실제 사건을 암시하지만 본문은 가정법("만약 ~했다면")으로만 위험을 서술 — 제목과 본문의 사건성 간극 | **기각** | "실제로 안 터진 버그를 막았다"는 게 이 글의 핵심 메시지이며, 가정법으로 위험을 서술한 것은 과장 없이 정직하게 쓴 것이라 판단. 제목의 긴장감을 위해 본문에 없는 사건을 지어내지 않기로 함 |

## 발행 정보 (발행 후 채울 것)

- 발행 링크: _(미정 — 발행 후 채움)_
- 발행 플랫폼: 기존 블로그/플랫폼에 직접 발행 예정
