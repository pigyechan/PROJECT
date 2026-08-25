// 가짜 데이터입니다. 실제 백엔드 API가 생기면 이 파일 대신 fetch() 호출로 교체합니다.
// docs/decisions/2026-08-12.md 참고: 화면은 mock 데이터로 먼저 만들고, API가 준비되는 대로 하나씩 실제 데이터로 교체.

const TODAY = new Date(2026, 7, 12); // 2026-08-12

// photo는 내프로필 화면에서만 등록/수정한다. 다른 화면(크루 멤버 카드 등)은 이 값을 그대로 가져다 쓴다.
const MOCK_ME = { id: 1, name: "박찬민", photo: null };

// createdYear/createdMonth: 크루가 만들어진 달 (createdMonth는 1~12). 캘린더 탐색 가능 범위의 시작점.
const MOCK_CREWS = [
  { id: 1, name: "주말 클라이머즈", emoji: "🧗", role: "OWNER", memberCount: 12, createdYear: 2025, createdMonth: 3 },
  { id: 2, name: "야간등반 모임", emoji: "🌙", role: "MANAGER", memberCount: 8, createdYear: 2025, createdMonth: 9 },
  { id: 3, name: "볼더링 스터디", emoji: "🪨", role: "MEMBER", memberCount: 21, createdYear: 2024, createdMonth: 6 },
];

// 크루별 멤버 명단 (전체 인원이 아니라, mock 리뷰/이벤트에 등장하는 멤버만 표시용으로 나열)
const MOCK_CREW_MEMBERS = {
  1: ["박찬민", "김도영", "이서준"],
  2: ["박찬민", "최유나"],
  3: ["박찬민", "김도영", "최유나", "이서준"],
};

// 크루원 상세 정보 — "크루 정보" 화면에서 보여줄 프로필. memberCount 전체가 아니라
// 이야기가 있는 멤버들(리뷰/글에 등장하는 사람들)만 실제 데이터로 채워뒀다. 나머지는 "외 N명"으로 뭉뚱그려 표시.
const MOCK_CREW_MEMBER_INFO = {
  1: [
    { name: "박찬민", role: "OWNER", joinedDate: "2025-03-15", bio: "크루 개설자입니다. 주말마다 등반해요." },
    { name: "김도영", role: "MANAGER", joinedDate: "2025-04-02", bio: "장비 관리를 맡고 있어요." },
    { name: "이서준", role: "MEMBER", joinedDate: "2025-06-20", bio: "입문 3개월차, 열심히 배우는 중입니다." },
  ],
  2: [
    { name: "최유나", role: "OWNER", joinedDate: "2025-09-01", bio: "이 크루를 만들었어요. 야간 등반 좋아합니다." },
    { name: "박찬민", role: "MANAGER", joinedDate: "2025-09-10", bio: "" },
  ],
  3: [
    { name: "김도영", role: "OWNER", joinedDate: "2024-06-01", bio: "볼더링 스터디 운영진입니다." },
    { name: "최유나", role: "MANAGER", joinedDate: "2024-08-15", bio: "" },
    { name: "박찬민", role: "MEMBER", joinedDate: "2024-07-01", bio: "" },
    { name: "이서준", role: "MEMBER", joinedDate: "2024-09-01", bio: "" },
  ],
};

// "크루 찾아보기"에 나오는, 아직 가입하지 않은 크루들.
// 가입 방식은 신청+승인(docs/decisions/2026-08-12.md 0001) — 신청하면 PENDING 상태가 된다.
const MOCK_DISCOVER_CREWS = [
  { id: 101, name: "새벽 클라이밍", emoji: "🌅", memberCount: 15, desc: "평일 새벽에 모여서 출근 전에 한 세션 하는 크루예요." },
  { id: 102, name: "여성 클라이머 모임", emoji: "💪", memberCount: 30, desc: "여성 클라이머들끼리 편하게 정보를 나누는 크루입니다." },
  { id: 103, name: "가족 클라이밍", emoji: "👨‍👩‍👧", memberCount: 9, desc: "아이와 함께 즐기는 클라이밍, 주말 위주로 모여요." },
];

const MOCK_GYMS = [
  { id: 1, name: "더클라임 강남점", address: "서울 강남구", x: "38%", y: "40%" },
  { id: 2, name: "클라이밍파크 홍대", address: "서울 마포구", x: "20%", y: "25%" },
  { id: 3, name: "더클라임 성수점", address: "서울 성동구", x: "62%", y: "55%" },
];

// 날짜는 TODAY(2026-08-12) 기준으로 "최근 1주일" 데모가 되도록 일부러 최근 날짜를 섞어뒀다.
// photo는 실제 이미지가 없어서 감성만 보여주는 이모지 자리표시자.
const MOCK_REVIEWS = {
  1: [
    { author: "김도영", date: "2026-08-11", visibility: "CREW_ONLY", rating: 4, photo: "🧗‍♂️", content: "홀드가 또 바뀌었네요. 이번 세팅 재밌어요." },
    { author: "박찬민", date: "2026-08-10", visibility: "PUBLIC", rating: 3, photo: "🪨", content: "홀드 세팅이 자주 바뀌어서 질리지 않아요. 주차가 좀 불편." },
    { author: "이서준", date: "2026-07-20", visibility: "PUBLIC", rating: 3, photo: "🧗", content: "저녁 시간대는 좀 붐벼요." },
    { author: "박찬민", date: "2026-07-10", visibility: "PRIVATE", rating: 4, photo: "📝", content: "다음엔 평일 오전에 가보기." },
  ],
  2: [
    { author: "최유나", date: "2026-08-08", visibility: "PUBLIC", rating: 5, photo: "🧗‍♀️", content: "천장 각도가 재밌는 문제가 많아요." },
    { author: "박찬민", date: "2026-07-15", visibility: "CREW_ONLY", rating: 4, photo: "🪨", content: "크루원들이랑 같이 가기 좋은 규모." },
  ],
  3: [
    { author: "박찬민", date: "2026-08-09", visibility: "PUBLIC", rating: 5, photo: "🏔️", content: "신생 지점이라 시설이 깨끗함." },
    { author: "김도영", date: "2026-08-07", visibility: "CREW_ONLY", rating: 4, photo: "🧗‍♂️", content: "장비 대여도 잘 돼있어요." },
  ],
};

const MOCK_EVENTS = [
  { date: "2026-08-15", title: "주말 정기 등반", crew: "주말 클라이머즈" },
  { date: "2026-08-15", title: "볼더링 스터디", crew: "볼더링 스터디" },
  { date: "2026-08-19", title: "야간 등반", crew: "야간등반 모임" },
  { date: "2026-08-22", title: "신입 환영 모임", crew: "주말 클라이머즈" },
  { date: "2026-08-29", title: "월말 정기 등반", crew: "주말 클라이머즈" },
];

// 커뮤니티 글 — 아직 CLAUDE.md 도메인 설계엔 없는 개념. 화면 탐색용 mock.
const MOCK_POSTS = {
  1: [
    { author: "김도영", date: "2026-08-10", content: "이번 주 토요일 정기 등반 다들 참석 가능하신가요? 준비물은 평소랑 동일합니다.",
      comments: [
        { author: "박찬민", date: "2026-08-10", content: "저는 참석입니다!" },
        { author: "이서준", date: "2026-08-11", content: "저도 갑니다~" },
      ] },
    { author: "박찬민", date: "2026-08-08", content: "강남점 신규 세팅 후기 남겨주실 분~", comments: [] },
    { author: "이서준", date: "2026-08-03", content: "다음 달 크루 티셔츠 제작 의견 받습니다.",
      comments: [
        { author: "김도영", date: "2026-08-04", content: "검정색으로 하나 통일하면 좋을 것 같아요." },
      ] },
  ],
  2: [
    { author: "최유나", date: "2026-08-09", content: "야간 등반 시간 21시로 조정 어떠세요?",
      comments: [
        { author: "박찬민", date: "2026-08-09", content: "좋습니다, 저는 21시 편해요." },
      ] },
    { author: "박찬민", date: "2026-08-01", content: "홍대점 야간 할인 정보 공유드려요.", comments: [] },
  ],
  3: [
    { author: "김도영", date: "2026-08-11", content: "볼더링 스터디 이번 주제는 슬로퍼 홀드입니다.", comments: [] },
    { author: "최유나", date: "2026-08-06", content: "스터디 자료 정리해서 올렸어요, 확인 부탁드려요.",
      comments: [
        { author: "이서준", date: "2026-08-06", content: "감사합니다, 잘 볼게요!" },
        { author: "박찬민", date: "2026-08-07", content: "고생하셨어요 ㅎㅎ" },
      ] },
    { author: "박찬민", date: "2026-08-02", content: "다음 스터디 장소 투표 부탁드립니다.", comments: [] },
    { author: "이서준", date: "2026-07-30", content: "지난 주 스터디 잘 봤습니다!", comments: [] },
  ],
};

// 사이트 전체가 공유하는 커뮤니티(크루 무관). 4개 게시판.
const MOCK_COMMUNITY_POSTS = {
  free: [
    { title: "클라이밍 시작한 지 3개월, 팁 좀 주세요", author: "정하늘", date: "2026-08-11", content: "손힘이 부족한 것 같은데 다들 어떻게 기르셨나요? 그립감 좋은 홀드 잡는 것도 어렵네요.",
      comments: [
        { author: "박찬민", date: "2026-08-11", content: "행잉보드 조금씩 하시는 걸 추천드려요. 무리하지 않는 선에서요." },
        { author: "김도영", date: "2026-08-12", content: "손힘보다 발 씀씀이가 더 중요할 때가 많아요. 발부터 신경써보세요." },
      ] },
    { title: "비 오는 날 실내 암장 습도 관리 어떻게 하세요", author: "박찬민", date: "2026-08-09", content: "요즘 장마철이라 홀드가 미끌거려서 고생중입니다. 초크 자주 바르는 것 말고 다른 팁 있을까요.",
      comments: [
        { author: "최유나", date: "2026-08-09", content: "액체 초크 한 번 발라두면 훨씬 오래 가더라고요." },
      ] },
    { title: "클라이밍화 사이즈 고민", author: "이서준", date: "2026-08-05", content: "평소 신발 사이즈보다 얼마나 작게 신는 게 적당한가요?", comments: [] },
  ],
  trade: [
    { title: "라스포르티바 클라이밍화 팝니다 (260)", author: "김도영", date: "2026-08-10", price: "80,000원", status: "판매중", content: "3번 정도 착용, 상태 좋습니다. 강남 직거래 가능해요.",
      comments: [
        { author: "정하늘", date: "2026-08-10", content: "혹시 265는 안 맞으실까요?" },
      ] },
    { title: "초크백 + 초크 세트 나눔", author: "최유나", date: "2026-08-07", price: "무료나눔", status: "예약중", content: "이사 정리하다 나온 여분입니다. 홍대 근처에서 픽업 가능하신 분.", comments: [] },
    { title: "볼더링 매트 삽니다", author: "박찬민", date: "2026-08-02", price: "가격제안", status: "구매희망", content: "야외 볼더링용 크래시패드 찾고 있어요. 중고 괜찮습니다.", comments: [] },
  ],
  events: [
    { title: "2026 가을 볼더링 오픈 대회", author: "관리자", date: "2026-08-06", eventDate: "2026-09-20", content: "성수동 클라이밍파크에서 열리는 오픈 대회입니다. 참가 신청은 9월 초까지.",
      comments: [
        { author: "이서준", date: "2026-08-06", content: "작년에도 참가했었는데 재밌었어요, 이번에도 신청하려구요." },
      ] },
    { title: "크루 연합 등반 모임 참가자 모집", author: "이서준", date: "2026-08-04", eventDate: "2026-08-30", content: "여러 크루가 같이 모여서 등반하는 자리예요. 관심 있으신 분들 댓글 남겨주세요.", comments: [] },
  ],
  gyms: [
    { title: "잠실에 신규 암장 오픈했네요", author: "최유나", date: "2026-08-11", gymName: "클라임베이스 잠실", content: "이번 달 초에 오픈한 곳인데 시설이 깨끗하고 루트도 다양해요. 오픈 이벤트로 할인 중입니다.",
      comments: [
        { author: "박찬민", date: "2026-08-11", content: "오 위치가 어디쯤인가요?" },
        { author: "최유나", date: "2026-08-11", content: "잠실역 8번 출구 도보 5분 정도예요." },
      ] },
    { title: "홍대 근처 24시간 운영 암장 아시는 분", author: "정하늘", date: "2026-08-08", gymName: "-", content: "야근 끝나고 갈 수 있는 곳 찾고 있어요.", comments: [] },
    { title: "성수점 vs 강남점 시설 비교", author: "김도영", date: "2026-08-03", gymName: "더클라임", content: "둘 다 다녀봤는데 성수점이 신생이라 그런지 확실히 더 깨끗하고, 강남점은 루트 난이도가 더 다양한 편이에요.", comments: [] },
  ],
};

function todayStr() {
  const y = TODAY.getFullYear();
  const m = String(TODAY.getMonth() + 1).padStart(2, "0");
  const d = String(TODAY.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

const MOCK_ATTENDEES = {
  "2026-08-15|주말 정기 등반": {
    going: ["박찬민", "김도영", "이서준"],
    notGoing: ["최유나"],
  },
};

// --- 공용 헬퍼 -----------------------------------------------------------

function starString(rating) {
  return "★".repeat(rating) + "☆".repeat(5 - rating);
}

function daysAgo(dateStr) {
  const d = new Date(dateStr + "T00:00:00");
  return Math.round((TODAY - d) / (1000 * 60 * 60 * 24));
}

// "크루 활동"은 남이 쓴 공개 리뷰를 모아 보여주는 게 아니라, 이 크루 멤버가 남긴 리뷰만 모은 것.
// 그래서 먼저 작성자가 이 크루 멤버인지부터 확인하고, 그다음 내가 볼 수 있는 공개범위인지 확인한다.
// (PRIVATE은 작성자 본인 외에는 크루 화면이라도 보이지 않는다.)
function isRelevantToCrewFeed(review, memberNames) {
  if (!memberNames.includes(review.author)) return false;
  if (review.visibility === "PRIVATE" && review.author !== MOCK_ME.name) return false;
  return true;
}

// 특정 크루 기준 "최근 7일 내" 활동한 암장 + 그 리뷰만 추려서 반환
function getRecentCrewGymActivity(crewId) {
  const memberNames = MOCK_CREW_MEMBERS[crewId] || [];
  const result = [];
  MOCK_GYMS.forEach(gym => {
    const reviews = (MOCK_REVIEWS[gym.id] || []).filter(r =>
      daysAgo(r.date) <= 7 && isRelevantToCrewFeed(r, memberNames)
    );
    if (reviews.length > 0) {
      result.push({ gym, reviews });
    }
  });
  return result;
}

// 개인 페이지: 내 리뷰를 (암장 무관) 최신순 평면 목록으로 — "최근 방문 기록", 통계 계산용
function getMyReviewsFlat() {
  const result = [];
  MOCK_GYMS.forEach(gym => {
    (MOCK_REVIEWS[gym.id] || []).forEach(r => {
      if (r.author === MOCK_ME.name) result.push({ review: r, gym });
    });
  });
  return result.sort((a, b) => b.review.date.localeCompare(a.review.date));
}

// 개인 페이지: 내가 리뷰를 남긴 암장 + 내 리뷰만
function getMyGymActivity() {
  const result = [];
  MOCK_GYMS.forEach(gym => {
    const myReviews = (MOCK_REVIEWS[gym.id] || []).filter(r => r.author === MOCK_ME.name);
    if (myReviews.length > 0) {
      result.push({ gym, reviews: myReviews });
    }
  });
  return result;
}
