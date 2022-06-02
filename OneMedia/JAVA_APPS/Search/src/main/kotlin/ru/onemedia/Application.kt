package ru.onemedia

import io.ktor.application.ApplicationStarted
import io.ktor.application.ApplicationStopped
import io.ktor.application.call
import io.ktor.application.install
import io.ktor.features.CORS
import io.ktor.features.CallLogging
import io.ktor.features.ContentNegotiation
import io.ktor.features.StatusPages
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpMethod
import io.ktor.http.HttpStatusCode
import io.ktor.request.receive
import io.ktor.response.respond
import io.ktor.routing.get
import io.ktor.routing.post
import io.ktor.routing.routing
import io.ktor.serialization.json
import io.ktor.server.engine.embeddedServer
import io.ktor.server.engine.stop
import io.ktor.server.netty.Netty
import java.util.concurrent.TimeUnit
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.slf4j.event.Level
import ru.onemedia.database.ConnectionPool
import ru.onemedia.search.DocMessageResultOld
import ru.onemedia.search.LuceneSearch
import ru.onemedia.search.LuceneSearch.enrich
import ru.onemedia.search.LuceneSearch.runRequest
import ru.onemedia.search.LuceneSearch.stopIndexKeeper
import ru.onemedia.search.SearchRequest
import ru.onemedia.search.getSearchAliveStatus


fun main() {
    val server = embeddedServer(Netty, port = AppConfig.app_port.toInt()) {
        val log = LoggerFactory.getLogger("ktor.application")
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = true
                isLenient = true
            })
        }
        install(CORS) {
            method(HttpMethod.Options)
            header(HttpHeaders.XForwardedProto)
            header(JWT_ONE_MEDIA_HEADER)
            anyHost()
            allowCredentials = true
            allowNonSimpleContentTypes = true
        }
        install(CallLogging) {
            // The CallLogging plugin (previously known as feature) allows you to log incoming client requests.
            level = Level.INFO
        }
        install(StatusPages) {
            exception<IllegalStateException> { cause ->
                call.respond(HttpStatusCode.InternalServerError, cause.message ?: "")
                throw cause
            }
        }
        routing {
            get("/") {
                call.respond("Index is alive!")
            }
            get("/alive") {
                log.info("I'm alive!")
                call.respond(getSearchAliveStatus())
            }
            post("/search") {
                val searchRequest = call.receive<SearchRequest>().getLowerCased()
                searchRequest.checkSearchRequest()
                log.info("Got searchRequest $searchRequest")
                val res = runRequest(searchRequest)
                if (searchRequest.enrich_content) {
                    enrich(searchRequest, res)
                }
                call.respond(res)
            }
            post("/search_old") {
                val searchRequest = call.receive<SearchRequest>().getLowerCased()
                searchRequest.checkSearchRequest()
                log.info("Got searchRequest old $searchRequest")
                val res = runRequest(searchRequest)
                if (searchRequest.enrich_content) {
                    enrich(searchRequest, res)
                }

                call.respond(res.map {
                    DocMessageResultOld.fromNewDocument(it)
                })
            }
            get("/search_body_example") {
                call.respond(SearchRequest.SEARCH_REQUEST_EXAMPLE)
            }
        }
        environment.monitor.subscribe(ApplicationStarted) {
            log.info("DB initialized state : ${ConnectionPool.isConnected}")
            LuceneSearch.start()
        }
        environment.monitor.subscribe(ApplicationStopped) {
            ConnectionPool.databasePoolShutdown()
            stopIndexKeeper()
            log.info("Cleaned up.")
        }
    }.start(wait = false)

    // make time for cleanup
    // https://dev.to/viniciusccarvalho/graceful-shutdown-of-ktor-applications-1h53
    Runtime.getRuntime().addShutdownHook(Thread {
        server.stop(1, 10, TimeUnit.SECONDS)
    })
    Thread.currentThread().join()
}

private const val JWT_ONE_MEDIA_HEADER = "X-One-Media"