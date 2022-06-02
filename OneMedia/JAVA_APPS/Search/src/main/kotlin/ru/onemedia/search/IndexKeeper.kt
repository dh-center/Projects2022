package ru.onemedia.search

import java.time.Duration
import kotlin.system.exitProcess
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import ru.onemedia.database.getAllTlgMessagesSequence
import ru.onemedia.database.getAllVkMessagesSequence
import ru.onemedia.database.getAllWebMessagesSequence
import ru.onemedia.search.LuceneSearch.getLastLoadedUid
import ru.onemedia.search.LuceneSearch.loadSequenceToIndex

class IndexKeeper : Runnable {
    private val log: Logger = LoggerFactory.getLogger(this::class.toString())

    override fun run() {
        while (!Thread.currentThread().isInterrupted) {
            try {
                log.info("IndexKeeper start phase")

                val lastLoadedUidVk = getLastLoadedUid(Source.vk) ?: 0
                log.info("Start loading ${Source.vk.name} lastLoadedUidVk : $lastLoadedUidVk")
                val lastUidVk: Long? = loadSequenceToIndex(
                    sequence = getAllVkMessagesSequence(maxNotToTakeUid = lastLoadedUidVk),
                    docMapper = DocMessage::fromVkMessage
                )
                log.info("Finished loading ${Source.vk.name} lastUidVk : $lastUidVk")

                val lastLoadedUidTlg = getLastLoadedUid(Source.tlg) ?: 0
                log.info("Start loading ${Source.tlg.name} lastLoadedUidTlg : $lastLoadedUidTlg")
                val lastUidTlg: Long? = loadSequenceToIndex(
                    sequence = getAllTlgMessagesSequence(maxNotToTakeUid = lastLoadedUidTlg),
                    docMapper = DocMessage::fromTlgMessage
                )
                log.info("Finished loading ${Source.tlg.name} lastUidTlg : $lastUidTlg")

                val lastLoadedUidWeb = getLastLoadedUid(Source.web) ?: 0
                log.info("Start loading ${Source.web.name} lastLoadedUidWeb : $lastLoadedUidWeb")
                val lastUidWeb: Long? = loadSequenceToIndex(
                    sequence = getAllWebMessagesSequence(maxNotToTakeUid = lastLoadedUidWeb),
                    docMapper = DocMessage::fromWebMessage
                )
                log.info("Finished loading ${Source.web.name} lastUidWeb : $lastUidWeb")

                if (lastUidTlg == null && lastUidWeb == null && lastUidVk == null) {
                    val sleepTime = Duration.ofSeconds(30)
                    log.info("No data to load, go to sleep for ${sleepTime.toSeconds()} seconds")
                    Thread.sleep(sleepTime.toMillis()) // 30 seconds
                }
            } catch (e: InterruptedException) {
                // Restore the interrupted status
                Thread.currentThread().interrupt()
            } catch (exp: java.net.UnknownHostException) {
                log.info("java.net.UnknownHostException in IndexKeeper : $exp", exp)
                Thread.currentThread().interrupt()
                exitProcess(1)
            } catch (exp: Exception) {
                log.info("Exception in IndexKeeper : $exp", exp)
            }
        }
        log.info("IndexKeeper stopped.")
    }
}