package com.vanellye.eria

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.math.BigDecimal

class SavedDollarsMathTest {
    @Test
    fun acceptsOnlyTwentyByteHexAddresses() {
        assertTrue(SavedDollarsMath.isAddress("0x" + "a".repeat(40)))
        assertFalse(SavedDollarsMath.isAddress("0x1234"))
        assertFalse(SavedDollarsMath.isAddress("not-an-address"))
    }

    @Test
    fun convertsTokenBaseUnitsUsingContractDecimals() {
        assertEquals(
            BigDecimal("12.345678"),
            SavedDollarsMath.tokenAmount("12345678", 6)
        )
        assertEquals(
            BigDecimal("1.25"),
            SavedDollarsMath.tokenAmount("1250000000000000000", 18)
        )
    }

    @Test
    fun computesAllocationOnlyAgainstPricedPortfolioValue() {
        assertEquals(
            BigDecimal("25.0000"),
            SavedDollarsMath.allocationPercent(BigDecimal("25"), BigDecimal("100"))
        )
        assertEquals(BigDecimal.ZERO, SavedDollarsMath.allocationPercent(BigDecimal("1"), BigDecimal.ZERO))
    }
}
