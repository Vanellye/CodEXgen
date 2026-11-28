package com.vanellye.eria

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.Button
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Surface
import androidx.compose.material.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.vanellye.eria.orchid.OrchidSymbolManagerActivity

/**
 * Lightweight, stable launcher. The heavier code-generation route is created only
 * after an explicit tap, so its ViewModel cannot prevent the home screen from opening.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    var showCodeGenerator by remember { mutableStateOf(false) }
                    Column(modifier = Modifier.fillMaxSize()) {
                        if (showCodeGenerator) {
                            Button(
                                onClick = { showCodeGenerator = false },
                                modifier = Modifier.padding(12.dp)
                            ) { Text("Back to ERIA tools") }
                            CodeGenRoute(modifier = Modifier.weight(1f))
                        } else {
                            Button(
                                onClick = {
                                    startActivity(Intent(this@MainActivity, OrchidSymbolManagerActivity::class.java))
                                },
                                modifier = Modifier.padding(12.dp)
                            ) { Text("ORCHID • Private Symbols & Keyboard") }
                            Button(
                                onClick = { showCodeGenerator = true },
                                modifier = Modifier.padding(horizontal = 12.dp)
                            ) { Text("Open Code Generator") }
                        }
                    }
                }
            }
        }
    }
}
