-- 컨테이너가 처음 뜰 때 데모용으로 미리 채워두는 데이터.
-- (사용자 생성/티켓 등록 API는 이번 kata 범위 밖이라, 예약 API를 바로 시연할 수 있도록 시드 데이터로 대신한다.)
INSERT INTO users (id, name) VALUES (1, '홍길동') ON CONFLICT (id) DO NOTHING;
INSERT INTO tickets (id, price, reserved, user_id) VALUES (100, 50000, false, NULL) ON CONFLICT (id) DO NOTHING;
