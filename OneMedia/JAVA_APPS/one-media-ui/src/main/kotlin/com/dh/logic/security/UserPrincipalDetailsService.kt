package com.dh.logic.security

import java.sql.ResultSet
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate
import org.springframework.security.core.userdetails.UserDetails
import org.springframework.security.core.userdetails.UserDetailsService
import org.springframework.security.core.userdetails.UsernameNotFoundException
import org.springframework.security.crypto.password.PasswordEncoder

class UserPrincipalDetailsService(
    private val passwordEncoder: PasswordEncoder,
    private val jdbcTemplate: NamedParameterJdbcTemplate
) : UserDetailsService {
    @Throws(UsernameNotFoundException::class)
    override fun loadUserByUsername(name: String): UserDetails {
        val id = getByName(name)
        return UserPrincipal(name, id, passwordEncoder)
    }

    private fun getByName(name: String): String =
        jdbcTemplate.query(
            "SELECT * FROM USER_INFO WHERE login=:name", mapOf(
                "name" to name
            ), USER_INFO_ROW_MAPPER
        ).first()

    private companion object {
        val USER_INFO_ROW_MAPPER = { resultSet: ResultSet, rowNum: Int -> resultSet.getString("user_id") }
    }
}