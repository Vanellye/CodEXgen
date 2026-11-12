package com.vanellye.eria

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material.Button
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Surface
import androidx.compose.material.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    var showCodeGenerator by remember { mutableStateOf(false) }

                    if (showCodeGenerator) {
                        Column(modifier = Modifier.fillMaxSize()) {
                            Button(onClick = { showCodeGenerator = false }) {
                                Text("Back to HOME")
                            }
                            CodeGenRoute(modifier = Modifier.weight(1f))
                        }
                    } else {
                        HomeScreen(
                            onOpenCodeGenerator = { showCodeGenerator = true }
                        )
                    }
                }
            }
        }
    }
}
