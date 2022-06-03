package ru.onemedia.search

import java.io.IOException
import java.nio.file.Paths
import kotlin.concurrent.thread
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.withContext
import org.apache.lucene.analysis.Analyzer
import org.apache.lucene.analysis.ru.RussianAnalyzer
import org.apache.lucene.document.*
import org.apache.lucene.index.*
import org.apache.lucene.queryparser.classic.ParseException
import org.apache.lucene.queryparser.classic.QueryParser
import org.apache.lucene.search.*
import org.apache.lucene.store.Directory
import org.apache.lucene.store.FSDirectory
import org.slf4j.LoggerFactory
import org.tartarus.snowball.ext.RussianStemmer
import ru.onemedia.database.enrichResult


object LuceneSearch {
    private val log = LoggerFactory.getLogger(this::class.toString())

    private val indexKeeperThread: Thread = thread(
        name = "IndexKeeperThread",
        start = true,
        isDaemon = true,
        block = IndexKeeper()::run
    )

    fun start() {
        log.info("LuceneSearch started")
    }

    fun stopIndexKeeper() {
        indexKeeperThread.interrupt()
    }

    @Throws(IOException::class, ParseException::class)
    @JvmStatic
    fun main(args: Array<String>) {
//        buildIndex()
//        runQuery()
//        val tlgLastLoadedUid = getLastLoadedUid(Source.TELEGRAM)
//        println(tlgLastLoadedUid)
        Thread.sleep(100_000_000)
    }

    private fun runQueryExample() {
        // https://stackoverflow.com/questions/4690983/committed-changes-visibility-in-lucene-best-practices
        val analyzer: Analyzer = RussianAnalyzer()
        val index: Directory = FSDirectory.open(Paths.get("./index"))
        val queryStr = "Путин"
        val q = QueryParser("content", analyzer).parse(queryStr)
        val hitsPerPage = 10
        DirectoryReader.open(index).use { reader ->
            val searcher = IndexSearcher(reader)
            val docs = searcher.search(q, hitsPerPage)
            val hits = docs.scoreDocs
            println("Found " + hits.size + " hits.")
            hits.asSequence()
                .map { searcher.doc(it.doc) }
                .map { DocMessageResult.fromIndexDocument(it) }
                .forEach {
                    println(it)
                }
        }
    }


    fun runRequest(request: SearchRequest): List<DocMessageResult> {
        FSDirectory.open(Paths.get("./index")).use { index ->
            DirectoryReader.open(index).use { reader ->
                val searcher = IndexSearcher(reader)

                val query = constructQuery(request)
                val docs = searcher.search(query, request.number_of_best_hits)

                val hits = docs.scoreDocs
                log.info("Found " + hits.size + " hits.")
                return@runRequest hits.map { it to searcher.doc(it.doc) }
                    .map { (hit, doc) -> DocMessageResult.fromIndexDocument(doc, hit.score) }
                    .toList()
            }
        }
    }


    suspend fun enrich(searchRequest: SearchRequest, results: List<DocMessageResult>): List<DocMessageResult> {
        val startTime = System.currentTimeMillis()
        withContext(Dispatchers.IO) {
            results.groupBy { it.source }.map {
                async {
                    enrichResult(it.key, it.value)
                }
            }.awaitAll()
        }
        val endTime = System.currentTimeMillis()
        val elapsedTime = endTime - startTime
        log.info("Enrich time for $searchRequest : ${elapsedTime / 1000.0}")
        return results
    }

    private fun Analyzer.getTermQuery(term: String): Query {
//        return QueryParser("content", this).parse("\"$term\"")
        val russianStemmer = RussianStemmer().apply {
            current = term
        }
        russianStemmer.stem()
        return TermQuery(Term("content", russianStemmer.current))
    }

    private fun constructQuery(searchRequest: SearchRequest): Query {
        val resQuery = BooleanQuery.Builder().add(MatchAllDocsQuery(), BooleanClause.Occur.MUST)
        RussianAnalyzer().use { analyzer ->
            with(searchRequest) {
                if (sources.isNotEmpty()) {
                    val sourceQuery = BooleanQuery.Builder()
                    sources.forEach {
                        sourceQuery.add(TermQuery(Term("source", it)), BooleanClause.Occur.SHOULD)
                        sourceQuery.setMinimumNumberShouldMatch(1) // at least one must match
                    }
                    resQuery.add(sourceQuery.build(), BooleanClause.Occur.MUST)
                }
                if (contentDocTermsMust.isNotEmpty()) {
                    val contentDocTermsQueryMust = BooleanQuery.Builder()
                    contentDocTermsMust.forEach { requestTerm ->
                        val termQuery = BooleanQuery.Builder()
                        requestTerm.synonyms.forEach { synonym ->
                            termQuery.add(analyzer.getTermQuery(synonym), BooleanClause.Occur.SHOULD)
                            termQuery.setMinimumNumberShouldMatch(1) // at least one must match
                        }
                        contentDocTermsQueryMust.add(termQuery.build(), BooleanClause.Occur.MUST)
                    }
                    resQuery.add(contentDocTermsQueryMust.build(), BooleanClause.Occur.MUST)
                }
                if (contentDocTermsShould.isNotEmpty()) {
                    val contentDocTermsQueryShould = BooleanQuery.Builder()
                    contentDocTermsShould.forEach { requestTerm ->
                        val termQuery = BooleanQuery.Builder()
                        requestTerm.synonyms.forEach { synonym ->
                            termQuery.add(analyzer.getTermQuery(synonym), BooleanClause.Occur.SHOULD)
                            termQuery.setMinimumNumberShouldMatch(1) // at least one must match
                        }
                        contentDocTermsQueryShould.add(termQuery.build(), BooleanClause.Occur.SHOULD)
                    }
                    resQuery.add(contentDocTermsQueryShould.build(), BooleanClause.Occur.SHOULD)
                }
                if (contentDocTermsExcluded.isNotEmpty()) {
                    val contentDocTermsQueryExcluded = BooleanQuery.Builder()
                    contentDocTermsExcluded.forEach { requestTerm ->
                        val termQuery = BooleanQuery.Builder()
                        requestTerm.synonyms.forEach { synonym ->
                            termQuery.add(analyzer.getTermQuery(synonym), BooleanClause.Occur.SHOULD)
                            termQuery.setMinimumNumberShouldMatch(1) // at least one must match
                        }
                        contentDocTermsQueryExcluded.add(termQuery.build(), BooleanClause.Occur.SHOULD)
                    }
                    resQuery.add(contentDocTermsQueryExcluded.build(), BooleanClause.Occur.MUST_NOT)
                }
                if (contentLuceneQuery != null && contentLuceneQuery.isNotEmpty()) {
                    resQuery.add(QueryParser("content", analyzer).parse(contentLuceneQuery), BooleanClause.Occur.MUST)
                }
                if (createdTimeRange != null) {
                    var from = createdTimeRange.from
                    var to = createdTimeRange.to
                    if (!createdTimeRange.includeUpper) {
                        to -= 1
                    }
                    if (!createdTimeRange.includeLower) {
                        from += 1
                    }
                    val createdTimeRangeQuery = LongPoint.newRangeQuery(
                        "created_time", from, to
                    )
                    resQuery.add(createdTimeRangeQuery, BooleanClause.Occur.MUST)
                }
                if (publishTimeRange != null) {
                    var from = publishTimeRange.from
                    var to = publishTimeRange.to
                    if (!publishTimeRange.includeUpper) {
                        to -= 1
                    }
                    if (!publishTimeRange.includeLower) {
                        from += 1
                    }
                    val createdTimeRangeQuery = LongPoint.newRangeQuery(
                        "publish_date", from, to
                    )
                    resQuery.add(createdTimeRangeQuery, BooleanClause.Occur.MUST)
                }
                if (channelNamesIncluded.isNotEmpty()) {
                    val channelNamesQuery = BooleanQuery.Builder()
                    channelNamesIncluded.forEach {
                        val exactChannelQuery = BooleanQuery.Builder()
                        exactChannelQuery.add(TermQuery(Term("source", it.source)), BooleanClause.Occur.MUST)
                        exactChannelQuery.add(TermQuery(Term("channel_name", it.channelName)), BooleanClause.Occur.MUST)
                        channelNamesQuery.add(exactChannelQuery.build(), BooleanClause.Occur.SHOULD)
                    }
                    channelNamesQuery.setMinimumNumberShouldMatch(1)
                    resQuery.add(channelNamesQuery.build(), BooleanClause.Occur.MUST)
                }
                if (channelNamesExcluded.isNotEmpty()) {
                    val channelNamesQuery = BooleanQuery.Builder()
                    channelNamesExcluded.forEach {
                        val exactChannelQuery = BooleanQuery.Builder()
                        exactChannelQuery.add(TermQuery(Term("source", it.source)), BooleanClause.Occur.MUST)
                        exactChannelQuery.add(TermQuery(Term("channel_name", it.channelName)), BooleanClause.Occur.MUST)
                        channelNamesQuery.add(exactChannelQuery.build(), BooleanClause.Occur.SHOULD)
                    }
                    channelNamesQuery.setMinimumNumberShouldMatch(1)
                    resQuery.add(channelNamesQuery.build(), BooleanClause.Occur.MUST_NOT)
                }
                if (participantsRange != null) {
                    var from = participantsRange.from
                    var to = participantsRange.to
                    if (!participantsRange.includeUpper) {
                        to -= 1
                    }
                    if (!participantsRange.includeLower) {
                        from += 1
                    }
                    val participantsRangeQuery = IntPoint.newRangeQuery(
                        "participants", from.toInt(), to.toInt()
                    )
                    resQuery.add(participantsRangeQuery, BooleanClause.Occur.MUST)
                }
            }
        }
        return resQuery.build()
    }

    fun <T> loadSequenceToIndex(
        sequence: Sequence<T>, docMapper: (T) -> DocMessage
    ): Long? {
        // https://stackoverflow.com/questions/8878448/lucene-good-practice-and-thread-safety
        val analyzer: Analyzer = RussianAnalyzer()
        analyzer.use {
            val index: Directory = FSDirectory.open(Paths.get("./index"))
            index.use {
                val config = IndexWriterConfig(analyzer)
                val indexWriter = IndexWriter(index, config)
                indexWriter.use {
                    sequence.take(10_000).map {
                        val doc = docMapper(it)
                        addDoc(indexWriter, doc)
                        doc
                    }.lastOrNull().apply {
                        return@loadSequenceToIndex this?.uid
                    }
                }
            }
        }
    }

    fun getLastLoadedUid(source: Source): Long? {
        val index: Directory = FSDirectory.open(Paths.get("./index"))
        val query: Query = TermQuery(Term("source", source.name))
        val uidSort: SortField = SortedNumericSortField("uid", SortField.Type.LONG, true)
        val sort = Sort(uidSort)

        try {
            DirectoryReader.open(index).use { reader ->
                val searcher = IndexSearcher(reader)
                val docs = searcher.search(query, 1, sort)
                val hits = docs.scoreDocs
                hits.map { searcher.doc(it.doc) }
                    .map { DocMessageResult.fromIndexDocument(it) }
                    .lastOrNull().apply {
                        return@getLastLoadedUid this?.uid
                    }
            }
        } catch (exp: IndexNotFoundException) {
            log.info("Can not find index!!!")
            return null
        }
    }

    @Throws(IOException::class, IOException::class)
    private fun addDoc(indexWriter: IndexWriter, message: DocMessage) {
        val doc = Document().apply {
            add(StringField("source", message.source.lowercase(), Field.Store.YES))
            if (message.channel_id != null) {
                add(StringField("channel_id", message.channel_id.lowercase(), Field.Store.YES))
            }
            add(StringField("channel_name", message.channel_name.lowercase(), Field.Store.YES))
            if (message.channel_title != null) {
                add(StringField("channel_title", message.channel_title.lowercase(), Field.Store.YES))
            }
            // publish_date
            if (message.publish_date != null) {
                add(LongPoint("publish_date", message.publish_date))
                add(StoredField("publish_date", message.publish_date))
            }
            // We do not store content here!!!
            add(TextField("content", message.content.lowercase(), Field.Store.NO))
            // uid
            add(NumericDocValuesField("uid", message.uid))
            add(StoredField("uid", message.uid))
            // created_time
            add(LongPoint("created_time", message.created_time))
            add(StoredField("created_time", message.created_time))
            // participants
            if (message.participants != null) {
                add(IntPoint("participants", message.participants))
                add(StoredField("participants", message.participants))
            }
            if (message.channel_display_name != null) {
                add(StringField("channel_display_name", message.channel_display_name.lowercase(), Field.Store.YES))
            }
            if (message.title != null) {
                add(TextField("title", message.title.lowercase(), Field.Store.NO))
            }
        }
        indexWriter.addDocument(doc)
    }
}