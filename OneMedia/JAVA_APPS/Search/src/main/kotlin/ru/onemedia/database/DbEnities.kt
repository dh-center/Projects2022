package ru.onemedia.database

import org.joda.time.LocalDate
import org.joda.time.LocalDateTime


data class TlgMessage(
    val message_id: String,
    val channel_id: String?,
    val channel_name: String,
    val channel_title: String?,
    val sender_username: String?,
    val sender_id: String?,
    val publish_date: LocalDate?,
    val content: String,
    val source_id: String?,
    val forward_channel_id: String?,
    val forward_message_id: String?,
    val meta_image: String?,
    val uid: Long,
    val created_time: LocalDateTime,
    // anchor part
    val participants: Int?,
    val channel_type: String?,
    val channel_display_name: String?,
)

data class WebMessage(
    val link: String,
    val channel_name: String,
    val sender_name: String?,
    val publish_date: LocalDate?,
    val title: String,
    val content: String,
    val meta_image: String?,
    val uid: Long,
    val created_time: LocalDateTime,
)

data class VkMessage(
    val message_id: Int,
    val owner_id: Int,
    val from_id: Int?,
    val message_content: String?,
    val publish_date: Int?,
    val meta_image: String?,
    val uid: Long,
    val created_time: LocalDateTime,
    // anchor part
    val channel_name: String?,
    val channel_id: Int,
    val screen_name: String?,
    val participants: Int,
)