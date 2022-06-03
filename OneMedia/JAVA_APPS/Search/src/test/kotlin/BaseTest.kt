import org.junit.jupiter.api.AfterAll
import ru.onemedia.database.ConnectionPool


open class BaseTest {
    companion object {
        @AfterAll
        fun shutdownDb() {
            ConnectionPool.databasePoolShutdown()
        }
    }
}