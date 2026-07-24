# === 1단계: 빌드 전용 컨테이너 ===
# Gradle 8.10.2 + JDK 21 버전이 고정된 이미지를 쓴다.
# "내 컴퓨터에 설치된 Gradle 버전"이 아니라, 항상 이 버전으로만 빌드되게 해서
# "제 컴퓨터에선 됐는데요"를 원천적으로 없앤다.
FROM gradle:8.10.2-jdk21 AS builder
WORKDIR /app
COPY build.gradle settings.gradle ./
COPY src ./src
RUN gradle build -x test --no-daemon

# === 2단계: 실행 전용 컨테이너 ===
# 빌드 도구(Gradle) 없이, 실행에 필요한 JRE(자바 실행기)만 담아서 이미지를 가볍게 만든다.
FROM eclipse-temurin:21-jre AS runtime
WORKDIR /app

# docker-compose 헬스체크에서 /actuator/health 를 확인할 때 쓸 curl 설치.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/build/libs/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
