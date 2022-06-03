package ru.onemedia

class AppConfig {
    companion object {
        val app_port: String
            get() = System.getenv("search_app_port") ?: "8083"
    }
}

class DBConfig {
    companion object {
        val db_host: String
            get() = System.getenv("POSTGRES_HOST") ?: "database"
        val db_port: String
            get() = System.getenv("POSTGRES_PORT") ?: "5432"
        val db_user: String
            get() = System.getenv("POSTGRES_USER") ?: "postgres"
        val db_password: String
            get() = System.getenv("POSTGRES_PASSWORD") ?: "pass"

        const val db_max_pool_size : Int = 5
    }
}