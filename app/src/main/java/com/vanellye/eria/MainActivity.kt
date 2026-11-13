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
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            var showIntake by mutableStateOf(true)
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    if (showIntake) {
                        ResearchIntakeScreen(onOpenCodeGenerator = { showIntake = false })
                    } else {
                        Column(modifier = Modifier.fillMaxSize()) {
                            Button(onClick = { showIntake = true }) { Text("Back to research intake") }
                            CodeGenRoute()
                        }
                    }
                }
            }
        }
    }
}
