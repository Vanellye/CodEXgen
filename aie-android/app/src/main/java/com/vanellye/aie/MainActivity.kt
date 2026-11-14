package com.vanellye.aie

import android.annotation.SuppressLint
import android.app.Activity
import android.os.Bundle
import android.view.Gravity
import android.view.ViewGroup
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private val executor = Executors.newSingleThreadExecutor()
    private lateinit var web: WebView
    private lateinit var apiInput: EditText
    private lateinit var connectionLabel: TextView
    private val prefs by lazy { getSharedPreferences("aie_settings", MODE_PRIVATE) }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(12, 10, 12, 0)
        }
        val bar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        apiInput = EditText(this).apply {
            singleLine = true
            textSize = 13f
            hint = "ERIA API origin (e.g. http://127.0.0.1:8778)"
            setText(prefs.getString("api_origin", "http://127.0.0.1:8778"))
        }
        bar.addView(apiInput, LinearLayout.LayoutParams(0, 52, 1f))
        val save = Button(this).apply {
            text = "Connect"
            setOnClickListener {
                val origin = apiInput.text.toString().trim().trimEnd('/')
                if (!validOrigin(origin)) {
                    connectionLabel.text = "Enter a valid HTTP(S) origin"
                } else {
                    prefs.edit().putString("api_origin", origin).apply()
                    connectionLabel.text = "API origin saved · checking…"
                    web.evaluateJavascript("window.location.reload()", null)
                }
            }
        }
        bar.addView(save)
        root.addView(bar)
        connectionLabel = TextView(this).apply {
            textSize = 11f
            text = "API: " + apiOrigin()
            setPadding(4, 0, 4, 8)
        }
        root.addView(connectionLabel)
        web = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = true
            settings.allowContentAccess = false
            settings.allowFileAccessFromFileURLs = false
            settings.allowUniversalAccessFromFileURLs = false
            settings.javaScriptCanOpenWindowsAutomatically = false
            settings.setSupportMultipleWindows(false)
            webChromeClient = WebChromeClient()
            addJavascriptInterface(NativeApi(), "AieNative")
        }
        root.addView(web, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f
        ))
        setContentView(root)
        web.loadUrl("file:///android_asset/index.html")
    }

    private fun validOrigin(value: String): Boolean = try {
        val u = java.net.URI(value)
        (u.scheme == "http" || u.scheme == "https") &&
            !u.host.isNullOrBlank() && u.userInfo == null &&
            u.path.isNullOrEmpty() && u.query == null && u.fragment == null
    } catch (_: Exception) { false }

    private fun apiOrigin(): String =
        prefs.getString("api_origin", "http://127.0.0.1:8778") ?: "http://127.0.0.1:8778"

    inner class NativeApi {
        @JavascriptInterface
        fun request(path: String, method: String, body: String, callbackId: String) {
            val allowed = setOf("/api/platform/status", "/api/scan", "/api/decode")
            if (path !in allowed || method !in setOf("GET", "POST")) {
                deliver(callbackId, 403, JSONObject().put("error", "Route not allowed").toString())
                return
            }
            executor.execute {
                var status = 502
                var payload = JSONObject().put("error", "ERIA API unavailable").toString()
                try {
                    val origin = apiOrigin()
                    if (!validOrigin(origin)) throw IllegalArgumentException("Invalid API origin")
                    val conn = (URL(origin + path).openConnection() as HttpURLConnection).apply {
                        requestMethod = method
                        connectTimeout = 8000
                        readTimeout = 25000
                        setRequestProperty("Accept", "application/json")
                        if (method == "POST") {
                            doOutput = true
                            setRequestProperty("Content-Type", "application/json")
                            outputStream.use { it.write((body.ifBlank { "{}" }).toByteArray(Charsets.UTF_8)) }
                        }
                    }
                    status = conn.responseCode
                    val stream = if (status >= 400) conn.errorStream else conn.inputStream
                    payload = stream?.bufferedReader()?.use { it.readText() } ?: "{}"
                    conn.disconnect()
                } catch (e: Exception) {
                    payload = JSONObject().put("error", e.message ?: "Connection failed").toString()
                }
                deliver(callbackId, status, payload)
            }
        }
    }

    private fun deliver(id: String, status: Int, payload: String) {
        val safeId = JSONObject.quote(id)
        val safePayload = JSONObject.quote(payload)
        runOnUiThread {
            if (::web.isInitialized) {
                web.evaluateJavascript(
                    "window.__aieNativeResult($safeId,$status,$safePayload)", null
                )
            }
        }
    }

    override fun onDestroy() {
        if (::web.isInitialized) web.destroy()
        executor.shutdownNow()
        super.onDestroy()
    }
}
