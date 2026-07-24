package ticket;

import io.cucumber.junit.platform.engine.Constants;
import org.junit.platform.suite.api.ConfigurationParameter;
import org.junit.platform.suite.api.IncludeEngines;
import org.junit.platform.suite.api.SelectClasspathResource;
import org.junit.platform.suite.api.Suite;

// gradle test 를 돌릴 때 이 클래스가 진입점이 되어,
// classpath 상의 "ticket" 폴더 밑 .feature 파일들을 전부 찾아서 실행한다.
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("ticket")
@ConfigurationParameter(key = Constants.GLUE_PROPERTY_NAME, value = "ticket.acceptance")
public class CucumberRunnerTest {
}
