package ru.onemedia.search

import java.io.File
import java.nio.file.Paths
import kotlinx.serialization.Serializable
import org.apache.lucene.index.DirectoryReader
import org.apache.lucene.index.IndexNotFoundException
import org.apache.lucene.store.Directory
import org.apache.lucene.store.FSDirectory
import ru.onemedia.search.LuceneSearch.getLastLoadedUid


@Serializable
data class SearchAliveStatus(
    val msg: String? = null,
    val overallNumberOfDocuments: Int? = null,
    val lastUidTlg: Long? = null,
    val lastUidWeb: Long? = null,
    val lastUidVk: Long? = null,
    val indexSizeInBytes: Long? = null,
)


fun folderSize(directory: File): Long {
    var length: Long = 0
    for (file in directory.listFiles()) {
        length += if (file.isFile) file.length() else folderSize(file)
    }
    return length
}

fun getSearchAliveStatus(): SearchAliveStatus {
    val pathToIndex = Paths.get("./index")
    val index: Directory = FSDirectory.open(pathToIndex)
    try {
        DirectoryReader.open(index).use { reader ->
            val numDocs = reader.numDocs()
            return@getSearchAliveStatus SearchAliveStatus(
                overallNumberOfDocuments = numDocs,
                lastUidTlg = getLastLoadedUid(Source.tlg),
                lastUidWeb = getLastLoadedUid(Source.web),
                lastUidVk = getLastLoadedUid(Source.vk),
                indexSizeInBytes = folderSize(pathToIndex.toFile()),
            )
        }
    } catch (exp: IndexNotFoundException) {
        return SearchAliveStatus(msg = "No index found!")
    }
}