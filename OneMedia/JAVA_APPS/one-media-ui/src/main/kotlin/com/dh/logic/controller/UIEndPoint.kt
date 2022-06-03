package com.dh.logic.controller

import com.dh.logic.SendEmailSSL
import com.dh.logic.entity.ContactMe
import org.slf4j.LoggerFactory
import org.springframework.http.HttpHeaders
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*


@RestController
@RequestMapping("/rest")
class UIEndPoint(val sendEmailSSL: SendEmailSSL) {
    var log = LoggerFactory.getLogger(UIEndPoint::class.java)

    @GetMapping("/starter")
    fun toShow() = "Hello"

    @PostMapping("/contact")
        fun contactUs(@RequestBody contactMe: ContactMe) : ResponseEntity<Any> {
        if(!sendEmailSSL.sendEmail("subject: ${contactMe.subject}\n\n${contactMe.message}", contactMe.name, contactMe.email)){
            log.error("we are failing with email! $contactMe");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
        log.info(contactMe.toString())
        return ResponseEntity.ok().build()
    }

    @GetMapping("/redirect")
    fun redirect(@RequestParam redirectUrl: String) : ResponseEntity<String> {
        val headers = HttpHeaders()
        headers.add("Location", redirectUrl)
        return ResponseEntity<String>(headers, HttpStatus.FOUND)
    }
}

