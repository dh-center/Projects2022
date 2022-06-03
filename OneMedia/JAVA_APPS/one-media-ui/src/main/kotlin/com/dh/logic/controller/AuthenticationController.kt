package com.dh.logic.controller

import com.auth0.jwt.JWT
import com.auth0.jwt.algorithms.Algorithm
import org.springframework.beans.factory.annotation.Value
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/auth")
class AuthenticationController(
    @Value("\${jwt.auth.secret}") secret: String
) {
    private val algorithmHS = Algorithm.HMAC256(secret)

    @GetMapping("/isAuthenticated")
    fun isAuthenticated(): Boolean {
        val authentication = SecurityContextHolder.getContext().authentication
        return authentication.isAuthenticated && !authentication.name.equals("anonymousUser")
    }

    @GetMapping("/jwt")
    fun jwt(): String {
        val authentication = SecurityContextHolder.getContext().authentication
        if (authentication.isAuthenticated && !authentication.name.equals("anonymousUser")) {
            return JWT.create()
                    .withClaim("name", authentication.name)
                    .sign(algorithmHS)
        }
        throw IllegalAccessError("Cannot get token as anonymous!")
    }
}