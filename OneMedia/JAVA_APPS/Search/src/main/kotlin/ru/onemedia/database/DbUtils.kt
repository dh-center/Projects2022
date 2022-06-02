package ru.onemedia.database

import com.github.jasync.sql.db.QueryResult
import com.github.jasync.sql.db.RowData
import kotlinx.coroutines.*
import kotlinx.coroutines.future.await
import org.joda.time.LocalDate
import org.joda.time.LocalDateTime
import org.slf4j.LoggerFactory
import ru.onemedia.search.DocMessageResult
import ru.onemedia.search.DocMessageResultEnriched
import ru.onemedia.search.Source


const val STEP: Int = 1000

val log = LoggerFactory.getLogger("DbUtils.kt")

fun getTlgMessagesBatch(batchNumber: Int, offsetUid: Long = 0): List<TlgMessage> {
    log.info("getTlgMessagesBatch(${batchNumber}) invoked (offset : ${STEP * batchNumber}, offsetUid : $offsetUid)")
    val res: QueryResult = runBlocking {
        withContext(Dispatchers.IO) {
            ConnectionPool.CONNECTION_POOL.use {
                it.sendPreparedStatement(
                    """
                        select m.message_id,
                               m.channel_id,
                               m.channel_name,
                               m.channel_title,
                               m.sender_username,
                               m.sender_id,
                               m.publish_date,
                               m.content,
                               m.source_id,
                               m.forward_channel_id,
                               m.forward_message_id,
                               m.meta_image,
                               m.uid,
                               m.created_time,
                               oa.subscribers,
                               oa.channel_type,
                               oa.channel_display_name
                        from message m
                        join ono_anchors oa on m.channel_id = oa.channel_id
                        where m.uid > $offsetUid
                        order by uid
                        limit $STEP
                        offset ${STEP * batchNumber};
                """.trimIndent()
                )
            }.await()
        }
    }
    return res.rows.map {
        TlgMessage(
            message_id = it.getString("message_id")!!,
            channel_id = it.getString("channel_id"),
            channel_name = it.getString("channel_name")!!,
            channel_title = it.getString("channel_title"),
            sender_username = it.getString("sender_username"),
            sender_id = it.getString("sender_id"),
            publish_date = if (it.get("publish_date") != null) it.get("publish_date") as LocalDate else null,
            content = it.getString("content")!!,
            source_id = it.getString("source_id"),
            forward_channel_id = it.getString("forward_channel_id"),
            forward_message_id = it.getString("forward_message_id"),
            meta_image = it.getString("meta_image"),
            uid = it.getLong("uid")!!,
            created_time = it.get("created_time") as LocalDateTime,
            // anchor part
            participants = it.getInt("subscribers"),
            channel_type = it.getString("channel_type"),
            channel_display_name = it.getString("channel_display_name"),
        )
    }.toList()
}


fun getAllTlgMessagesSequence(maxNotToTakeUid: Long = 0): Sequence<TlgMessage> = sequence {
    var batchNumber: Int = 0
    var curBatch: List<TlgMessage> = getTlgMessagesBatch(0, maxNotToTakeUid)
    while (curBatch.isNotEmpty()) {
        curBatch.forEach {
            yield(it)
        }
        batchNumber += 1
        curBatch = getTlgMessagesBatch(batchNumber, maxNotToTakeUid)
    }
}

fun getWebMessagesBatch(batchNumber: Int, offsetUid: Long = 0): List<WebMessage> {
    log.info("getWebMessagesBatch(${batchNumber}) invoked (offset : ${STEP * batchNumber}, offsetUid : $offsetUid)")
    val res: QueryResult = runBlocking {
        withContext(Dispatchers.IO) {
            ConnectionPool.CONNECTION_POOL.use {
                it.sendPreparedStatement(
                    """
                        select m.message_id,
                               m.link,
                               m.channel_name,
                               m.sender_name,
                               m.publish_date,
                               m.title,
                               m.content,
                               m.meta_image,
                               m.uid,
                               m.created_time
                        from web_message m
                        where m.uid > $offsetUid
                        order by uid
                        limit $STEP
                        offset ${STEP * batchNumber};
                """.trimIndent()
                )
            }.await()
        }
    }
    return res.rows.map {
        WebMessage(
            link = it.getString("link")!!,
            channel_name = it.getString("channel_name")!!,
            sender_name = it.getString("sender_name"),
            publish_date = if (it.get("publish_date") != null) it.get("publish_date") as LocalDate else null,
            title = it.getString("title")!!,
            content = it.getString("content")!!,
            meta_image = it.getString("meta_image"),
            uid = it.getLong("uid")!!,
            created_time = it.get("created_time") as LocalDateTime,
        )
    }.toList()
}


fun getAllWebMessagesSequence(maxNotToTakeUid: Long = 0): Sequence<WebMessage> = sequence {
    var batchNumber: Int = 0
    var curBatch: List<WebMessage> = getWebMessagesBatch(0, maxNotToTakeUid)
    while (curBatch.isNotEmpty()) {
        curBatch.forEach {
            yield(it)
        }
        batchNumber += 1
        curBatch = getWebMessagesBatch(batchNumber, maxNotToTakeUid)
    }
}

fun getVkMessagesBatch(batchNumber: Int, offsetUid: Long = 0): List<VkMessage> {
    log.info("getVkMessagesBatch(${batchNumber}) invoked (offset : ${STEP * batchNumber}, offsetUid : $offsetUid)")
    val res: QueryResult = runBlocking {
        withContext(Dispatchers.IO) {
            ConnectionPool.CONNECTION_POOL.use {
                it.sendPreparedStatement(
                    """
                        select vm.message_id,
                               vm.owner_id,
                               vm.from_id,
                               vm.message_content,
                               vm.publish_date,
                               vm.meta_image,
                               vm.uid,
                               vm.created_time,
                               vma.channel_name,
                               vma.channel_id,
                               vma.screen_name,
                               vma.participants
                        from vk_message vm
                                 join vk_message_anchors vma on -vma.channel_id = vm.owner_id
                        where vm.uid > $offsetUid
                        order by uid
                        limit $STEP
                        offset ${STEP * batchNumber};
                """.trimIndent()
                )
            }.await()
        }
    }
    return res.rows.map {
        VkMessage(
            message_id = it.getInt("message_id")!!,
            owner_id = it.getInt("owner_id")!!,
            from_id = it.getInt("from_id"),
            message_content = it.getString("message_content"),
            publish_date = it.getInt("publish_date"),
            meta_image = it.getString("meta_image"),
            uid = it.getLong("uid")!!,
            created_time = it.get("created_time") as LocalDateTime,
            // anchor part
            channel_name = it.getString("channel_name"),
            channel_id = it.getInt("channel_id")!!,
            screen_name = it.getString("screen_name"),
            participants = it.getInt("participants")!!,
        )
    }.toList()
}


fun getAllVkMessagesSequence(maxNotToTakeUid: Long = 0): Sequence<VkMessage> = sequence {
    var batchNumber: Int = 0
    var curBatch: List<VkMessage> = getVkMessagesBatch(0, maxNotToTakeUid)
    while (curBatch.isNotEmpty()) {
        curBatch.forEach {
            yield(it)
        }
        batchNumber += 1
        curBatch = getVkMessagesBatch(batchNumber, maxNotToTakeUid)
    }
}

const val ENRICH_BATCH_SIZE: Int = 100
suspend fun enrichResult(source: String, results: List<DocMessageResult>) {
    val (query: String, enrich: (DocMessageResult, RowData) -> Unit) = when (source) {
        Source.tlg.name.lowercase() -> {
            """
                    select *
                    from message
                        join ono_anchors oa on message.channel_id = oa.channel_id
                    where uid in ?;
            """ to { doc: DocMessageResult, rowData: RowData ->
                doc.enriched_part = DocMessageResultEnriched(
                    content = rowData.getString("content")!!,
                    meta_image = rowData.getString("meta_image"),
                    sender_id = rowData.getString("sender_id"),
                    sender_name = rowData.getString("sender_username"),
                    link = "https://t.me/${rowData.getString("channel_name")}/${rowData.getString("message_id")}",
                    participantsNow = rowData.getInt("subscribers")
                )
            }
        }
        Source.web.name.lowercase() -> {
            """
                    select * from web_message
                    where uid in ?;
            """ to { doc: DocMessageResult, rowData: RowData ->
                doc.enriched_part = DocMessageResultEnriched(
                    content = rowData.getString("content")!!,
                    meta_image = rowData.getString("meta_image"),
                    sender_id = null,
                    sender_name = rowData.getString("sender_name"),
                    link = rowData.getString("link"),
                    participantsNow = null,
                )
            }
        }
        Source.vk.name.lowercase() -> {
            """
                    select *
                    from vk_message vm
                                 join vk_message_anchors vma on -vma.channel_id = vm.owner_id
                    where uid in ?;
            """ to { doc: DocMessageResult, rowData: RowData ->
                doc.enriched_part = DocMessageResultEnriched(
                    content = rowData.getString("message_content") ?: run {
                        log.error("VK empty message content!!! ${doc}")
                        return@run ""
                    },
                    meta_image = rowData.getString("meta_image"),
                    sender_id = rowData.getInt("owner_id").toString(),
                    sender_name = null,
                    link = "https://vk.com/${rowData.getString("screen_name")}?w=wall${rowData.getInt("owner_id")}_${
                        rowData.getInt(
                            "message_id"
                        )
                    }",
                    participantsNow = rowData.getInt("participants")
                )
            }
        }
        else -> throw RuntimeException("Bad source ${source}")
    }

    val uidMapping: Map<Long, DocMessageResult> = results.map { it.uid to it }.toMap()
    results.sortedBy { it.uid }.chunked(ENRICH_BATCH_SIZE).map { batch ->
        withContext(Dispatchers.IO) {
            async {
                ConnectionPool.CONNECTION_POOL.use {
                    val param = batch.map { it.uid }.joinToString(prefix = "(", separator = ",", postfix = ")")
                    val queryToRun: String = query.replace("?", param)
                    it.sendPreparedStatement(queryToRun, emptyList(), release = true)
                }.await()
            }
        }
    }.awaitAll().forEach { queryResult ->
        queryResult.rows.forEach { rowData ->
            val uid = rowData.getLong("uid")!!
            val docToEnrich = uidMapping[uid]!!
            enrich(docToEnrich, rowData)
        }
    }
}
