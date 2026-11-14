package com.vanellye.eria

import android.os.Bundle
import android.graphics.Bitmap
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.Button
import androidx.compose.material.CircularProgressIndicator
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Surface
import androidx.compose.material.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                var pageStatus by remember { mutableStateOf("Connecting to ERIA server…") }
                var loading by remember { mutableStateOf(true) }
                var reloadKey by remember { mutableIntStateOf(0) }
                var showRepositoryDashboard by remember { mutableStateOf(false) }

                Surface(modifier = Modifier.fillMaxSize()) {
                    Column(modifier = Modifier.fillMaxSize()) {
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text("ERIA", style = MaterialTheme.typography.h6)
                                Text(
                                    if (showRepositoryDashboard) {
                                        "Native repository dashboard · local Termux API"
                                    } else {
                                        pageStatus
                                    },
                                    style = MaterialTheme.typography.caption
                                )
                            }
                            if (loading && !showRepositoryDashboard) {
                                CircularProgressIndicator(
                                    modifier = Modifier.padding(end = 12.dp),
                                    strokeWidth = 2.dp
                                )
                            }
                            Button(
                                onClick = {
                                    showRepositoryDashboard = !showRepositoryDashboard
                                    if (showRepositoryDashboard) {
                                        loading = false
                                    } else {
                                        reloadKey++
                                        loading = true
                                    }
                                }
                            ) {
                                Text(if (showRepositoryDashboard) "Conversation" else "Dashboard")
                            }
                            if (!showRepositoryDashboard) {
                                Button(onClick = { reloadKey++ }) { Text("Reload") }
                            }
                        }

                        if (showRepositoryDashboard) {
                            RepositoryDashboardScreen()
                        } else {
                            key(reloadKey) {
                                AndroidView(
                                    modifier = Modifier.fillMaxWidth().weight(1f),
                                    factory = { context ->
                                        WebView(context).apply {
                                            settings.javaScriptEnabled = true
                                            settings.domStorageEnabled = true
                                            settings.allowFileAccess = false
                                            settings.allowContentAccess = false
                                            settings.javaScriptCanOpenWindowsAutomatically = false
                                            settings.setSupportMultipleWindows(false)
                                            settings.mixedContentMode =
                                                android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW

                                            webViewClient = object : WebViewClient() {
                                                override fun shouldOverrideUrlLoading(
                                                    view: WebView,
                                                    request: WebResourceRequest
                                                ): Boolean {
                                                    val uri = request.url
                                                    return !(uri.scheme == "http" &&
                                                        uri.host == EriaServerConfig.HOST &&
                                                        uri.port == EriaServerConfig.PORT)
                                                }

                                                override fun onPageStarted(
                                                    view: WebView,
                                                    url: String?,
                                                    favicon: Bitmap?
                                                ) {
                                                    pageStatus = "Loading " + EriaServerConfig.BASE_URL
                                                    loading = true
                                                }

                                                override fun onPageFinished(
                                                    view: WebView,
                                                    url: String?
                                                ) {
                                                    pageStatus = "Connected · " +
                                                        (url ?: EriaServerConfig.BASE_URL)
                                                    loading = false
                                                }

                                                override fun onReceivedError(
                                                    view: WebView,
                                                    request: WebResourceRequest,
                                                    error: android.webkit.WebResourceError
                                                ) {
                                                    if (request.isForMainFrame) {
                                                        pageStatus = "Server unavailable · " +
                                                            error.description
                                                        loading = false
                                                    }
                                                }
                                            }
                                            loadUrl(EriaServerConfig.BASE_URL)
                                        }
                                    },
                                    update = { }
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
