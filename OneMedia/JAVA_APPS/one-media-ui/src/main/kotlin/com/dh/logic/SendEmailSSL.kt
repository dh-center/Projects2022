package com.dh.logic


import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.PropertySource
import org.springframework.stereotype.Component

import javax.annotation.PostConstruct
import javax.mail.*
import javax.mail.internet.InternetAddress
import javax.mail.internet.MimeMessage
import java.util.Properties

@PropertySource("classpath:email.properties")
@Component
class SendEmailSSL {
    var log = LoggerFactory.getLogger(SendEmailSSL::class.java)

    @Value("\${email.username}")
    private val ourEmail: String? = null

    @Value("\${email.signature}")
    private val signature: String? = null

    @Value("\${email.password}")
    private val password: String? = null

    private var session: Session? = null

    @PostConstruct
    fun init() {
        val prop = Properties()
        //        prop.put("mail.smtp.host", "smtp.gmail.com");
        //        prop.put("mail.smtp.port", "465");
        prop["mail.smtp.host"] = "smtp.mail.ru"
        prop["mail.smtp.port"] = "465"

        //        prop.put("mail.debug","true");
        prop["mail.smtp.auth"] = "true"
        prop["mail.smtp.socketFactory.port"] = "465"
        prop["mail.smtp.ssl.enable"] = "true"

        prop["mail.smtp.socketFactory.class"] = "javax.net.ssl.SSLSocketFactory"

        session = Session.getInstance(prop,
                object : javax.mail.Authenticator() {
                    override fun getPasswordAuthentication(): PasswordAuthentication {
                        return PasswordAuthentication(ourEmail, password)
                    }
                })
    }

    fun sendEmail(messageText: String, name: String, emailTo: String) : Boolean{
        if (!sendEmailAttemptServer(messageText, name, emailTo)) {
            init()
            return sendEmailAttemptServer(messageText, name, emailTo)
        }

        if (!sendEmailAttemptClient(messageText, name, emailTo)) {
            init()
            return sendEmailAttemptServer(messageText, name, emailTo)
        }
        return true;
    }

    /*
    send feedback to client (some confirmation letter)
     */
    private fun sendEmailAttemptClient(messageText: String, name: String, emailTo: String) : Boolean{
        try {
            val message = MimeMessage(session)
            message.setFrom(InternetAddress(ourEmail!!))
            message.setRecipients(
                    Message.RecipientType.TO,
                    InternetAddress.parse(emailTo)
            )
            message.subject = "$signature (Клиентское обращение)"
            message.setText("Спасибо, $name, ваше обращение принято!")

            Transport.send(message)
            return true
        } catch (e: MessagingException) {
            log.error("Failed attempt to send a message! ", e)
            return false
        }
    }


    /*
    send feedback to us
     */
    private fun sendEmailAttemptServer(messageText: String, name: String, emailTo: String): Boolean {
        try {
            val message = MimeMessage(session)
            message.setFrom(InternetAddress(ourEmail!!))
            message.setRecipients(
                    Message.RecipientType.TO,
                    InternetAddress.parse(ourEmail)
            )
            message.subject = "$signature (Клиентское обращение)"
            message.setText("Имя клиента: $name \n\n" +
                    "Email клиента: $emailTo\n\n" +
                    "---------------------------------------------------------------------------------------------------\n\n" +
                    "Текст обращения: $messageText")

            Transport.send(message)
            return true
        } catch (e: MessagingException) {
            log.error("Failed attempt to send a message! ", e)
            return false
        }

    }

}