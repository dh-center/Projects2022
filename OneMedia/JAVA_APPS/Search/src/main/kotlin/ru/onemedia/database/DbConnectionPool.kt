package ru.onemedia.database

import com.github.jasync.sql.db.ConnectionPoolConfigurationBuilder
import com.github.jasync.sql.db.pool.ConnectionPool
import com.github.jasync.sql.db.postgresql.PostgreSQLConnection
import com.github.jasync.sql.db.postgresql.PostgreSQLConnectionBuilder
import org.slf4j.LoggerFactory
import ru.onemedia.DBConfig
import java.util.concurrent.TimeUnit



class ConnectionPool {

    companion object {
        private val log = LoggerFactory.getLogger(this::class.toString())

        private val connectionPoolConfigurationBuilder = ConnectionPoolConfigurationBuilder(
            host = DBConfig.db_host,
            port = DBConfig.db_port.toInt(),
            username = DBConfig.db_user,
            database = DBConfig.db_user,
            password = DBConfig.db_password,
            applicationName = "searchEngine",
            // the number of simultaneous connection
            maxActiveConnections = 20,
            //  the number of pending queries
            maxPendingQueries = 1_000_000,
            // the millisecond before an idle connection is reclaimed
            maxIdleTime = TimeUnit.MINUTES.toMillis(5),
            // interval in milliseconds to ping the server to
            connectionValidationInterval = TimeUnit.SECONDS.toMillis(60),
        )

        // https://github.com/jasync-sql/jasync-sql
        val CONNECTION_POOL: ConnectionPool<PostgreSQLConnection> = PostgreSQLConnectionBuilder.createConnectionPool(
            connectionPoolConfigurationBuilder
        )

        init {
            // init pool
            log.info("CONNECTION_POOL initialization started...")
            CONNECTION_POOL.connect().get()
            log.info("CONNECTION_POOL initialization finished.")
        }

        fun databasePoolShutdown() {
            log.info("CONNECTION_POOL shutdown started...")
            CONNECTION_POOL.disconnect().get()
            log.info("CONNECTION_POOL shutdown finished.")
        }

        val isConnected: Boolean
            get() = CONNECTION_POOL.isConnected()
    }
}



