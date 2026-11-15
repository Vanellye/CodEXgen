package com.vanellye.eria

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.math.BigDecimal
import java.math.BigInteger
import java.math.RoundingMode
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale

private const val BASE_RPC = "https://mainnet.base.org"
private const val BASE_CHAIN_ID = "0x2105"
private const val ETHERSCAN_BASE = "https://basescan.org/address/"

private data class WalletAsset(
    val symbol: String,
    val name: String,
    val amount: String,
    val contract: String? = null,
    val note: String = ""
)

private data class BaseSnapshot(
    val address: String,
    val chainId: String,
    val blockNumber: String,
    val eth: String,
    val assets: List<WalletAsset>,
    val sampledAt: String
)

/**
 * Read-only Base JSON-RPC client. It never signs, sends, or broadcasts transactions.
 * Token discovery is intentionally bounded to canonical assets; arbitrary ERC-20
 * discovery requires an indexed token-list / transfer-history provider.
 */
private object BaseReadOnlyClient {
    private fun rpc(method: String, params: String): JSONObject {
        val conn = (URL(BASE_RPC).openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 12_000
            readTimeout = 20_000
            doOutput = true
            setRequestProperty("Content-Type", "application/json")
        }
        try {
            val body = JSONObject()
                .put("jsonrpc", "2.0")
                .put("id", 1)
                .put("method", method)
                .put("params", org.json.JSONArray(params))
                .toString()
            conn.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
            val response = (if (conn.responseCode in 200..299) conn.inputStream else conn.errorStream)
                .bufferedReader().use { it.readText() }
            val json = JSONObject(response)
            if (json.has("error")) error(json.getJSONObject("error").optString("message", "RPC error"))
            return json.getJSONObject("result")
        } finally {
            conn.disconnect()
        }
    }

    private fun call(to: String, data: String): String {
        val params = org.json.JSONArray()
            .put(JSONObject().put("to", to).put("data", data))
            .put("latest")
        return rpc("eth_call", params.toString()).toString()
    }

    private fun hexQuantity(hex: String, decimals: Int): String {
        val raw = BigInteger(hex.removePrefix("0x").ifBlank { "0" }, 16)
        return BigDecimal(raw).movePointLeft(decimals)
            .stripTrailingZeros().toPlainString()
    }

    private fun balanceOf(address: String, contract: String): String {
        val encodedAddress = address.removePrefix("0x").lowercase(Locale.US).padStart(64, '0')
        val result = call(contract, "0x70a08231$encodedAddress")
        return hexQuantity(result, 6)
    }

    suspend fun load(address: String): BaseSnapshot = withContext(Dispatchers.IO) {
        val chain = rpc("eth_chainId", "[]").toString()
        require(chain.equals(BASE_CHAIN_ID, ignoreCase = true)) {
            "RPC returned chain ID $chain, expected Base mainnet 8453."
        }
        val block = rpc("eth_blockNumber", "[]").toString()
        val wei = BigInteger(rpc(
            "eth_getBalance",
            org.json.JSONArray().put(address).put("latest").toString()
        ).toString().removePrefix("0x"), 16)
        val eth = BigDecimal(wei).movePointLeft(18).stripTrailingZeros().toPlainString()

        val assets = mutableListOf(
            WalletAsset("ETH", "Ether", eth, note = "Native Base balance")
        )
        // Canonical Base USDC (native USDC) and WETH contracts.
        val tokens = listOf(
            Triple("USDC", "USD Coin", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"),
            Triple("WETH", "Wrapped Ether", "0x4200000000000000000000000000000000000006")
        )
        for ((symbol, name, contract) in tokens) {
            val decimals = if (symbol == "WETH") 18 else 6
            val encodedAddress = address.removePrefix("0x").lowercase(Locale.US).padStart(64, '0')
            val result = call(contract, "0x70a08231$encodedAddress")
            val amount = hexQuantity(result, decimals)
            assets += WalletAsset(symbol, name, amount, contract, "ERC-20 balanceOf at latest block")
        }
        BaseSnapshot(
            address = address,
            chainId = chain,
            blockNumber = BigInteger(block.removePrefix("0x"), 16).toString(),
            eth = eth,
            assets = assets,
            sampledAt = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss 'UTC'", Locale.US)
                .apply { timeZone = java.util.TimeZone.getTimeZone("UTC") }
                .format(java.util.Date())
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
        modifier = Modifier.fillMaxSize().padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        Text("SAVED DOLLARS", style = MaterialTheme.typography.h5, fontWeight = FontWeight.Bold)
        Text("Base Mainnet · Read-only wallet monitor")
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
                if (!Regex("^0x[a-fA-F0-9]{40}$").matches(address)) {
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
        ) {
            Text(if (loading) "Reading Base…" else "Check balances")
        }
        Text(
            "Only public blockchain reads are performed. No wallet connection, private key, " +
                "seed phrase, transaction signing, or transfer capability.",
            style = MaterialTheme.typography.caption
        )
        error?.let { Text(it, color = MaterialTheme.colors.error) }
        snapshot?.let { data ->
            Divider()
            Text("PORTFOLIO", style = MaterialTheme.typography.overline)
            Text("USD valuation unavailable", style = MaterialTheme.typography.h6)
            Text("Token quantities are live on-chain readings; no price feed is configured.")
            Text("Network: Base Mainnet · Chain ID 8453")
            Text("Latest block: ${data.blockNumber}")
            Text("Verified at: ${data.sampledAt}")
            Text("Address: ${data.address.take(8)}…${data.address.takeLast(6)}")
            Divider()
            Text("ASSETS", style = MaterialTheme.typography.subtitle1, fontWeight = FontWeight.Bold)
            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(data.assets) { asset ->
                    Card(modifier = Modifier.fillMaxWidth(), elevation = 2.dp) {
                        Column(Modifier.padding(12.dp)) {
                            Text("${asset.name} (${asset.symbol})", fontWeight = FontWeight.SemiBold)
                            Text(asset.amount, style = MaterialTheme.typography.h6)
                            Text(asset.note.ifBlank { asset.contract ?: "Native asset" },
                                style = MaterialTheme.typography.caption)
                        }
                    }
                }
            }
            TextButton(onClick = {
                /* Open a block explorer URL using Android intent in the host app if desired. */
            }) { Text("BaseScan: $ETHERSCAN_BASE${data.address}") }
        }
    }
}
