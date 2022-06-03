package ru.onemedia.search

import kotlinx.serialization.Serializable
import org.apache.lucene.document.Document
import org.joda.time.DateTimeZone
import ru.onemedia.database.TlgMessage
import ru.onemedia.database.VkMessage
import ru.onemedia.database.WebMessage

@Serializable
data class Range(
    val from: Long,
    val to: Long,
    val includeLower: Boolean = true,
    val includeUpper: Boolean = true,
)

enum class Source {
    tlg, web, vk
}

@Serializable
data class RequestTerm(val synonyms: List<String>) {

    constructor(term: String) : this(listOf(term))

    init {
        require(synonyms.isNotEmpty()) { "RequestTerm should have at least one term" }
    }

    fun lowercase() = copy(synonyms = synonyms.map { it.lowercase() })

    fun trim() = copy(synonyms = synonyms.map { it.trim() })
}

@Serializable
data class ChannelRequest(
    val source: String,
    val channelName: String
) {
    init {
        require(source.isNotEmpty() && channelName.isNotEmpty()) {
            "source and channelName can not be empty"
        }
    }

    fun trim() = copy(source = source.trim(), channelName = channelName.trim())
}

@Serializable
data class SearchRequest(
    val sources: List<String> = emptyList(),
    val contentDocTermsMust: List<RequestTerm> = emptyList(),
    val contentDocTermsShould: List<RequestTerm> = emptyList(),
    val contentDocTermsExcluded: List<RequestTerm> = emptyList(),
    val contentLuceneQuery: String? = null,
    val createdTimeRange: Range? = null,
    val publishTimeRange: Range? = null,
    val contentTitleTerms: List<String> = emptyList(),
    val contentTitlePart: String? = null,
    val senderName: String? = null,
    val channelNamesIncluded: List<ChannelRequest> = emptyList(),
    val channelNamesExcluded: List<ChannelRequest> = emptyList(),
    val channelIds: List<String> = emptyList(),
    val participantsRange: Range? = null,
    val enrich_content: Boolean = false,
    val number_of_best_hits: Int = 50,
) {

    fun getLowerCased() = this.copy(
        sources = sources.map { it.trim().lowercase() },
        contentDocTermsMust = contentDocTermsMust.map { it.lowercase().trim() },
        contentDocTermsShould = contentDocTermsShould.map { it.lowercase().trim() },
        contentDocTermsExcluded = contentDocTermsExcluded.map { it.lowercase().trim() },
        contentLuceneQuery = contentLuceneQuery?.lowercase()?.trim(),
        contentTitleTerms = contentTitleTerms.map { it.lowercase().trim() },
        contentTitlePart = contentTitlePart?.lowercase()?.trim(),
        senderName = senderName?.lowercase()?.trim(),
        channelNamesIncluded = channelNamesIncluded.map { it.trim() },
        channelNamesExcluded = channelNamesExcluded.map { it.trim() },
        channelIds = channelIds.map { it.lowercase().trim() }
    )

    companion object {
        val availableSources = Source.values().map { it.name.lowercase() }.toSet()

        val SEARCH_REQUEST_EXAMPLE = SearchRequest(
            sources = availableSources.toList(),
            contentDocTermsMust = listOf(RequestTerm(listOf("term1", "term2")), RequestTerm(listOf("term3"))),
            contentDocTermsShould = listOf(RequestTerm("term1Should"), RequestTerm("term2Should")),
            contentDocTermsExcluded = listOf(RequestTerm("term1Excluded"), RequestTerm("term2Excluded")),
            contentLuceneQuery = "\"Do it right\" AND right",
            createdTimeRange = Range(from = 1, to = 2, includeLower = true, includeUpper = true),
            channelNamesIncluded = listOf(
                ChannelRequest(source = "vk", channelName = "someChannelVkIncluded"),
                ChannelRequest(source = "web", channelName = "someChannelWebIncluded")
            ),
            channelNamesExcluded = listOf(
                ChannelRequest(source = "tlg", channelName = "someChannelVkExcluded")
            ),
            participantsRange = Range(from = 100_000, to = 200_000, includeLower = true, includeUpper = true),
            enrich_content = true,
            number_of_best_hits = 100,
        )
    }

    fun checkSearchRequest() {
        this.sources.forEach {
            if (it.lowercase() !in availableSources)
                throw IllegalStateException("No such source $it")
        }
    }
}


data class DocMessage(
    val source: String,
    val channel_id: String?,
    val channel_name: String,
    val channel_title: String?,
    val sender_username: String?,
    val sender_id: String?,
    val publish_date: Long?,
    val content: String,
    val title: String? = null, // currently only for web messages
    val meta_image: String?,
    val uid: Long,
    val created_time: Long,
    // anchor part
    val participants: Int?,
    val channel_display_name: String?,
) {
    companion object {
        fun fromTlgMessage(tlgMessage: TlgMessage): DocMessage =
            DocMessage(
                source = Source.tlg.name,
                channel_id = tlgMessage.channel_id,
                channel_name = tlgMessage.channel_name,
                channel_title = tlgMessage.channel_title,
                sender_username = tlgMessage.sender_username,
                sender_id = tlgMessage.sender_id,
                publish_date = tlgMessage.publish_date?.toDateTimeAtStartOfDay(DateTimeZone.UTC)?.millis,
                content = tlgMessage.content,
                meta_image = tlgMessage.meta_image,
                uid = tlgMessage.uid,
                created_time = tlgMessage.created_time.toDateTime().millis,
                // anchor part
                participants = tlgMessage.participants,
                channel_display_name = tlgMessage.channel_display_name,
            )

        fun fromVkMessage(vkMessage: VkMessage): DocMessage =
            DocMessage(
                source = Source.vk.name,
                channel_id = vkMessage.channel_id.toString(),
                channel_name = vkMessage.screen_name ?: "",
                channel_title = vkMessage.channel_name,
                sender_username = vkMessage.from_id.toString(),
                sender_id = vkMessage.from_id.toString(),
                publish_date = (vkMessage.publish_date?.toLong() ?: 1L) * 1000,
                content = vkMessage.message_content!!,
                meta_image = vkMessage.meta_image,
                uid = vkMessage.uid,
                created_time = vkMessage.created_time.toDateTime().millis,
                // anchor part
                participants = vkMessage.participants,
                channel_display_name = vkMessage.screen_name ?: "",
            )

        fun fromWebMessage(webMessage: WebMessage): DocMessage =
            DocMessage(
                source = Source.web.name,
                channel_id = null,
                channel_name = webMessage.channel_name,
                title = webMessage.title,
                channel_title = webMessage.channel_name,
                sender_username = webMessage.sender_name,
                sender_id = null,
                publish_date = webMessage.publish_date?.toDateTimeAtStartOfDay(DateTimeZone.UTC)?.millis,
                content = webMessage.content,
                meta_image = webMessage.meta_image,
                uid = webMessage.uid,
                created_time = webMessage.created_time.toDateTime().millis,
                // anchor part
                participants = null,
                channel_display_name = webMessage.channel_name,
            )
    }
}

@Serializable
data class DocMessageResultEnriched(
    val content: String,
    val meta_image: String?,
    val sender_id: String?,
    val sender_name: String?,
    val link: String?,
    val participantsNow: Int?,
)

@Serializable
data class DocMessageResult(
    val source: String,
    val channel_id: String?,
    val channel_name: String,
    val channel_title: String?,
    val publish_date: Long?,
    val uid: Long,
    val created_time: Long,
    // anchor part
    val participants: Int?,
    val channel_display_name: String?,
    val score: Float? = null,
    // enriched part
    var enriched_part: DocMessageResultEnriched? = null,
) {
    companion object {
        fun fromIndexDocument(doc: Document, score: Float? = null): DocMessageResult =
            DocMessageResult(
                source = doc["source"],
                channel_id = doc["channel_id"],
                channel_name = doc["channel_name"],
                channel_title = doc["channel_title"],
                publish_date = doc.getField("publish_date")?.numericValue()?.toLong(),
                uid = doc.getField("uid").numericValue().toLong(),
                created_time = doc.getField("created_time").numericValue().toLong(),
                participants = doc.getField("participants")?.numericValue()?.toInt(),
                channel_display_name = doc["channel_display_name"],
                score = score,
            )
    }
}

@Serializable
data class DocMessageResultOld(
    val source: String,
    val channelId: String,
    val messageId: String,
    val channelName: String,
    val channelTitle: String?,
    val publishDate: Long,
    // anchor part
    val participants: String,
    val channelDisplayName: String,
    val score: Float? = null,
    // enriched part
    val content: String,
    val meta_image: String,
    val link: String?,
    val imageLink: String?,
    val senderName: String?
) {
    companion object {


        fun fromNewDocument(doc: DocMessageResult): DocMessageResultOld {
            return DocMessageResultOld(
                source = doc.source,
                channelId = doc.channel_id ?: "",
                channelName = doc.channel_name,
                channelTitle = doc.channel_title,
                publishDate = doc.publish_date ?: 0,
                participants = doc.participants.toString(),
                channelDisplayName = doc.channel_display_name ?: "",
                score = doc.score,
                content = doc.enriched_part?.content ?: "",
                meta_image = doc.enriched_part?.meta_image ?: "",
                link = doc.enriched_part?.link ?: "",
                messageId = doc.uid.toString(),
                imageLink = doc.enriched_part?.meta_image ?: "",
                senderName = doc.enriched_part?.sender_name ?: ""
            )
        }
    }
}

