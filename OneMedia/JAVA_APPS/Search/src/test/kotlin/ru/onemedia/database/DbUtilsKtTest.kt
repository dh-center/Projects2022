package ru.onemedia.database

import BaseTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class DbUtilsKtTest : BaseTest() {

    @Test
    fun testGetTlgMessages() {
        val actual = getAllTlgMessagesSequence(maxNotToTakeUid = 10).take(1000).map { it.uid }.toList()
        val expected = (11L..1010L).toList()
        assertEquals(expected, actual)
    }

    @Test
    fun testGetWebMessages() {
        val actual = getAllWebMessagesSequence(maxNotToTakeUid = 10).take(1000).map { it.uid }.toList()
        val expected = (11L..1010L).toList()
        assertEquals(expected, actual)
    }

    @Test
    fun testGetVkMessages() {
        val actual = getAllVkMessagesSequence(maxNotToTakeUid = 10).take(1000).map { it.uid }.toList()
        val expected = (11L..1010L).toList()
        assertEquals(expected, actual)
    }
}