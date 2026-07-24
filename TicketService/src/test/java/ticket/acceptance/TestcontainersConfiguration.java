package ticket.acceptance;

import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;

// 인수테스트가 실제로 띄우는 Postgres 컨테이너.
// @ServiceConnection 덕분에 Spring Boot가 이 컨테이너의 접속정보(호스트/포트/계정)를
// application.yml의 spring.datasource.* 설정 없이도 자동으로 datasource에 연결해준다.
@Configuration(proxyBeanMethods = false)
public class TestcontainersConfiguration {

    @Bean
    @ServiceConnection
    PostgreSQLContainer<?> postgresContainer() {
        return new PostgreSQLContainer<>(DockerImageName.parse("postgres:16-alpine"));
    }
}
