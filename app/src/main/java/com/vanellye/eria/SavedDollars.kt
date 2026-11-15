package com.vanellye.eria

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.math.BigDecimal
import java.math.BigInteger
import java.math.MathContext
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

private const val BASE_RPC = "https://mainnet.base.org"
private const val BASE_CHAIN_ID = "0x2105"
private const val BLOCKSCOUT_API = "https://base.blockscout.com/api/v2"
private const val BASESCAN_ADDRESS = "https://basescan.org/address/"

internal object SavedDollarsMath {
    fun isAddress(value: String): Boolean =
        Regex("^0x[a-fA-F0-9]{40}$").matches(value.trim())

    fun tokenAmount(rawValue: String, decimals: Int): BigDecimal {
        require(decimals in 0..36) { "Unsupported token decimals: $decimals" }
        return BigDecimal(rawValue).movePointLeft(decimals)
    }

    fun allocationPercent(valueUsd: BigDecimal, totalUsd: BigDecimal): BigDecimal {
        if (totalUsd <= BigDecimal.ZERO) return BigDecimal.ZERO
        return valueUsd.multiply(BigDecimal("100")).divide(totalUsd, 4, java.math.RoundingMode.HALF_UP)
    }
}

private data class WalletAsset(
    val symbol: String,
    val name: String,
    val amount: BigDecimal,
    val contract: String?,
    val priceUsd: BigDecimal?,
    val valueUsd: BigDecimal?,
    val isNative: Boolean = false
)

private data class WalletActivity(
    val hash: String,
    val timestamp: String,
    val title: String,
    val detail: String,
    val explorerUrl: String
)

private data class BaseSnapshot(
    val address: String,
    val chainId: String,
    val blockNumber: String,
    val assets: List<WalletAsset>,
    val activities: List<WalletActivity>,
    val sampledAt: String,
    val indexer: String
) {
    val pricedTotal: BigDecimal
        get() = assets.mapNotNull { it.valueUsd }.fold(BigDecimal.ZERO) { total, value -> total.add(value) }
    val pricedAssetCount: Int get() = assets.count { it.valueUsd != null }
}

private object BaseReadOnlyClient {
    private fun getText(url: String): String {
        val connection = (URL(url).openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            connectTimeout = 15_000
            readTimeout = 25_000
            setRequestProperty("Accept", "application/json")
            setRequestProperty("User-Agent", "ERIA-SavedDollars/1.0")
        }
        try {
            val code = connection.responseCode
            val stream = if (code in 200..299) connection.inputStream else connection.errorStream
            val body = stream?.bufferedReader()?.use { it.readText() }.orEmpty()
            if (code !in 200..299) error("Explorer API returned HTTP $code: ${body.take(180)}")
            return body
        } finally {
            connection.disconnect()
        }
    }

    private fun rpc(method: String, params: JSONArray): String {
        val connection = (URL(BASE_RPC).openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 12_000
            readTimeout = 20_000
            doOutput = true
            setRequestProperty("Content-Type", "application/json")
            setRequestProperty("Accept", "application/json")
        }
        try {
            val request = JSONObject()
                .put("jsonrpc", "2.0")
                .put("id", 1)
                .put("method", method)
                .put("params", params)
            connection.outputStream.use { it.write(request.toString().toByteArray(Charsets.UTF_8)) }
            val code = connection.responseCode
            val stream = if (code in 200..299) connection.inputStream else connection.errorStream
            val response = stream?.bufferedReader()?.use { it.readText() }.orEmpty()
            if (code !in 200..299) error("Base RPC returned HTTP $code")
            val json = JSONObject(response)
            if (json.has("error")) error(json.optJSONObject("error")?.optString("message") ?: "Base RPC error")
            return json.optString("result").takeIf { it.isNotBlank() }
                ?: error("Base RPC response did not contain a result")
        } finally {
            connection.disconnect()
        }
    }

    private fun explorer(path: String): String = getText("$BLOCKSCOUT_API$path")

    private fun decimalOrNull(value: String?): BigDecimal? =
        value?.takeIf { it.isNotBlank() && it != "null" }?.toBigDecimalOrNull()

    private fun usdValue(amount: BigDecimal, price: BigDecimal?): BigDecimal? =
        price?.let { amount.multiply(it, MathContext.DECIMAL64) }

    suspend fun load(address: String): BaseSnapshot = withContext(Dispatchers.IO) {
        require(SavedDollarsMath.isAddress(address)) { "Enter a valid public wallet address." }

        val chainId = rpc("eth_chainId", JSONArray())
        require(chainId.equals(BASE_CHAIN_ID, ignoreCase = true)) {
            "RPC chain ID mismatch: expected Base 8453, received $chainId."
        }
        val blockHex = rpc("eth_blockNumber", JSONArray())
        val blockNumber = BigInteger(blockHex.removePrefix("0x").ifBlank { "0" }, 16).toString()
        val nativeHex = rpc("eth_getBalance", JSONArray().put(address).put("latest"))
        val nativeWei = BigInteger(nativeHex.removePrefix("0x").ifBlank { "0" }, 16)
        val ethAmount = BigDecimal(nativeWei).movePointLeft(18)

        val addressInfo = JSONObject(explorer("/addresses/$address"))
        val nativePrice = decimalOrNull(addressInfo.optString("exchange_rate", null))
        val assets = mutableListOf(
            WalletAsset(
                symbol = "ETH",
                name = "Ether",
                amount = ethAmount,
                contract = null,
                priceUsd = nativePrice,
                valueUsd = usdValue(ethAmount, nativePrice),
                isNative = true
            )
        )

        // Blockscout's address token-balances endpoint enumerates indexed token holdings.
        // It cannot prove the existence of tokens that the indexer has not discovered.
        val tokenArray = JSONArray(explorer("/addresses/$address/token-balances"))
        for (i in 0 until tokenArray.length()) {
            val row = tokenArray.optJSONObject(i) ?: continue
            val token = row.optJSONObject("token") ?: continue
            if (!token.optString("type").equals("ERC-20", ignoreCase = true)) continue
            val decimals = token.optString("decimals").toIntOrNull() ?: continue
            if (decimals !in 0..36) continue
            val raw = row.optString("value")
            val amount = runCatching { SavedDollarsMath.tokenAmount(raw, decimals) }.getOrNull() ?: continue
            if (amount.compareTo(BigDecimal.ZERO) <= 0) continue
            val symbol = token.optString("symbol").ifBlank { "TOKEN" }
            val name = token.optString("name").ifBlank { symbol }
            val contract = token.optString("address_hash").ifBlank {
                token.optString("address").ifBlank { null }
            }
            val price = decimalOrNull(token.optString("exchange_rate", null))
            assets += WalletAsset(symbol, name, amount, contract, price, usdValue(amount, price))
        }

        val activities = mutableListOf<WalletActivity>()
        val txResponse = JSONObject(explorer("/addresses/$address/transactions"))
        val txItems = txResponse.optJSONArray("items") ?: JSONArray()
        for (i in 0 until minOf(txItems.length(), 25)) {
            val tx = txItems.optJSONObject(i) ?: continue
            val hash = tx.optString("hash")
            if (hash.isBlank()) continue
            val from = tx.optJSONObject("from")?.optString("hash").orEmpty()
            val to = tx.optJSONObject("to")?.optString("hash").orEmpty()
            val direction = when {
                to.equals(address, true) -> "Incoming native transaction"
                from.equals(address, true) -> "Outgoing transaction / contract call"
                else -> "Transaction"
            }
            val timestamp = tx.optString("timestamp").ifBlank { "Timestamp unavailable" }
            val valueWei = tx.optString("value").toBigDecimalOrNull() ?: BigDecimal.ZERO
            val valueEth = valueWei.movePointLeft(18).stripTrailingZeros().toPlainString()
            activities += WalletActivity(
                hash, timestamp, direction, "Value: $valueEth ETH · Block ${tx.optString("block")}",
                "https://basescan.org/tx/$hash"
            )
        }

        val transferResponse = JSONObject(explorer("/addresses/$address/token-transfers?type=ERC-20"))
        val transferItems = transferResponse.optJSONArray("items") ?: JSONArray()
        for (i in 0 until minOf(transferItems.length(), 30)) {
            val transfer = transferItems.optJSONObject(i) ?: continue
            val hash = transfer.optString("transaction_hash")
            if (hash.isBlank()) continue
            val token = transfer.optJSONObject("token") ?: JSONObject()
            val from = transfer.optJSONObject("from")?.optString("hash").orEmpty()
            val to = transfer.optJSONObject("to")?.optString("hash").orEmpty()
            val direction = if (to.equals(address, true)) "Received" else "Sent"
            val symbol = token.optString("symbol").ifBlank { "ERC-20" }
            val raw = transfer.optJSONObject("total")?.optString("value")
                ?: transfer.optString("total").takeIf { it.isNotBlank() }
                ?: "?"
            val decimals = token.optString("decimals").toIntOrNull() ?: 0
            val quantity = raw.toBigDecimalOrNull()?.movePointLeft(decimals)?.stripTrailingZeros()?.toPlainString() ?: raw
            activities += WalletActivity(
                hash,
                transfer.optString("timestamp").ifBlank { "Timestamp unavailable" },
                "$direction $symbol",
                "Amount: $quantity · Contract: ${token.optString("address_hash")}",
                "https://basescan.org/tx/$hash"
            )
        }

        val time = SimpleDateFormat("yyyy-MM-dd HH:mm:ss 'UTC'", Locale.US).apply {
            timeZone = TimeZone.getTimeZone("UTC")
        }.format(Date())

        BaseSnapshot(
            address = address,
            chainId = chainId,
            blockNumber = blockNumber,
            assets = assets.sortedByDescending { it.valueUsd ?: BigDecimal.ZERO },
            activities = activities.distinctBy { it.hash + it.title }.sortedByDescending { it.timestamp }.take(40),
            sampledAt = time,
            indexer = "Base Blockscout API v2"
        )
    }
}

@Composable
fun SavedDollarsScreen() {
    var address by remember { mutableStateOf("") }
    var snapshot by remember { mutableStateOf<BaseSnapshot?>(null) }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("SAVED DOLLARS", style = MaterialTheme.typography.h5, fontWeight = FontWeight.Bold)
        Text("Base Mainnet · Read-only portfolio monitor")
        OutlinedTextField(
            value = address,
            onValueChange = { address = it.trim(); error = null },
            label = { Text("Public wallet address") },
            placeholder = { Text("0x…") },
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Ascii),
            modifier = Modifier.fillMaxWidth()
        )
        Button(
            onClick = {
                if (!SavedDollarsMath.isAddress(address)) {
                    error = "Enter a valid 0x address containing 40 hexadecimal characters."
                } else {
                    loading = true
                    error = null
                    scope.launch {
                        try {
                            snapshot = BaseReadOnlyClient.load(address)
                        } catch (t: Throwable) {
                            error = t.message ?: "Unable to retrieve Base data."
                        } finally {
                            loading = false
                        }
                    }
                }
            },
            enabled = !loading,
            modifier = Modifier.fillMaxWidth()
        ) { Text(if (loading) "Refreshing…" else "Refresh portfolio") }

        Text(
            "Public-data mode only: no wallet connection, private key, seed phrase, signing, " +
                "approval, or transaction broadcast.",
            style = MaterialTheme.typography.caption
        )
        error?.let { Text(it, color = MaterialTheme.colors.error) }

        snapshot?.let { data ->
            Divider()
            Text("PORTFOLIO VALUE", style = MaterialTheme.typography.overline)
            Text(
                if (data.pricedAssetCount == 0) "USD valuation unavailable"
                else "$" + data.pricedTotal.setScale(2, java.math.RoundingMode.HALF_UP).toPlainString(),
                style = MaterialTheme.typography.h4,
                fontWeight = FontWeight.Bold
            )
            Text(
                "Priced assets: ${data.pricedAssetCount} / ${data.assets.size}. " +
                    "Unpriced tokens are shown without invented values.",
                style = MaterialTheme.typography.caption
            )
            Text("Base Mainnet · Chain ID ${data.chainId} · Block ${data.blockNumber}")
            Text("Read at ${data.sampledAt} · ${data.indexer}", style = MaterialTheme.typography.caption)
            Text("Address: ${data.address.take(8)}…${data.address.takeLast(6)}")
            Divider()
            Text("ASSET ALLOCATION", style = MaterialTheme.typography.subtitle1, fontWeight = FontWeight.Bold)
            data.assets.forEach { asset ->
                val allocation = SavedDollarsMath.allocationPercent(asset.valueUsd ?: BigDecimal.ZERO, data.pricedTotal)
                Card(modifier = Modifier.fillMaxWidth(), elevation = 2.dp) {
                    Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(3.dp)) {
                        Text("${asset.name} (${asset.symbol})", fontWeight = FontWeight.SemiBold)
                        Text(asset.amount.stripTrailingZeros().toPlainString())
                        Text(
                            asset.valueUsd?.let {
                                "$" + it.setScale(2, java.math.RoundingMode.HALF_UP).toPlainString() +
                                    " · " + allocation.toPlainString() + "%"
                            } ?: "USD price unavailable · allocation excluded",
                            style = MaterialTheme.typography.caption
                        )
                        asset.contract?.let { Text("Contract: $it", style = MaterialTheme.typography.caption) }
                    }
                }
            }
            Divider()
            Text("RECENT ACTIVITY", style = MaterialTheme.typography.subtitle1, fontWeight = FontWeight.Bold)
            if (data.activities.isEmpty()) {
                Text("No indexed transactions returned for this address.")
            } else {
                data.activities.forEach { activity ->
                    Card(modifier = Modifier.fillMaxWidth(), elevation = 1.dp) {
                        Column(Modifier.padding(10.dp)) {
                            Text(activity.title, fontWeight = FontWeight.SemiBold)
                            Text(activity.detail, style = MaterialTheme.typography.caption)
                            Text(activity.timestamp, style = MaterialTheme.typography.caption)
                            Text(activity.explorerUrl, style = MaterialTheme.typography.caption)
                        }
                    }
                }
            }
            Text("Verify independently: $BASESCAN_ADDRESS${data.address}", style = MaterialTheme.typography.caption)
        }
    }
}
