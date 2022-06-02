package com.dh.logic.query

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.ObjectMapper
import java.security.Principal
import java.sql.ResultSet
import org.postgresql.util.PGobject
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/userQuery")
class UserQueryController(val jdbcTemplate: NamedParameterJdbcTemplate) {

    @ResponseStatus(HttpStatus.ACCEPTED)
    @PostMapping("/validateUserQuery")
    fun validateUserQuery(@RequestBody query: QueryContainer){
        objectMapper.readValue(query.query, UserQueryContent::class.java)
    }

    @GetMapping("/userQuery")
    fun getRestQueries(principal: Principal): List<UserQuery> = getQueries(principal.name)

    @ResponseStatus(HttpStatus.ACCEPTED)
    @PostMapping("/userQuery")
    fun addQuery(@RequestBody query: UserQuery, principal: Principal) = insertQuery(query, principal.name.toLong())

    @ResponseStatus(HttpStatus.ACCEPTED)
    @PostMapping("/removeUserQuery")
    fun removeUserQuery(@RequestBody query: UserQuery) = deleteQuery(query)

    @ResponseStatus(HttpStatus.ACCEPTED)
    @PostMapping("/updateUserQuery")
    fun updateUserQuery(@RequestBody query: UserQuery) = updateQuery(query)


    private fun getQueries(id: String): List<UserQuery> =
        jdbcTemplate.query("SELECT * FROM USER_QUERY WHERE user_id = $id", USER_QUERY_ROW_MAPPER)

    private fun insertQuery(query: UserQuery, userId: Long) = jdbcTemplate.update(
        "INSERT INTO USER_QUERY(USER_ID, NAME, QUERY) VALUES (:user_id, :name, :query)",
        getNewQueryMap(query, userId)
    )

    private fun deleteQuery(query: UserQuery) = jdbcTemplate.update(
        "DELETE FROM USER_QUERY WHERE user_id = :user_id AND name = :name",
        mapOf("user_id" to query.userId.toLong(), "name" to query.name)
    )

    private fun updateQuery(query: UserQuery) = jdbcTemplate.update(
        "UPDATE USER_QUERY SET query = :query WHERE name = :name and user_id = :user_id",
        getNewQueryMap(query)
    )

    private fun getNewQueryMap(query: UserQuery, userId: Long? = null) =
        mapOf("user_id" to (userId ?: query.userId.toLong()), "name" to query.name, "query" to PGobject().apply {
            type = "json"
            value = query.query
        }.also {
            objectMapper.readValue(query.query, UserQueryContent::class.java)
        })


    private companion object {
        val objectMapper = ObjectMapper()

        val USER_QUERY_ROW_MAPPER = { resultSet: ResultSet, rowNum: Int ->
            UserQuery(
                id = resultSet.getString("uid"),
                userId = resultSet.getString("user_id"),
                name = resultSet.getString("name"),
                query = resultSet.getString("query"),
                createdTime = resultSet.getString("created_time")
            )
        }
    }
}

data class QueryContainer(val query: String)

data class UserQuery(
    val id: String?,
    val userId: String,
    val name: String,
    val query: String,
    val createdTime: String?
)

data class UserQueryContent(
    @JsonProperty("channels_excluded")
    val channelsExcluded: List<List<String>> = listOf(),
    @JsonProperty("channels_included")
    val channelsIncluded: List<List<String>> = listOf(),

    @JsonProperty("excluded_terms")
    val excludedTerms: List<List<String>> = listOf(),
    @JsonProperty("must_terms")
    val mustTerms: List<List<String>> = listOf(),
    @JsonProperty("should_terms")
    val shouldTerms: List<List<String>> = listOf(),
    @JsonProperty("sources")
    val sources: List<String>? = listOf()
)