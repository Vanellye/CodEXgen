package com.vanellye.codexgen

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
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
import com.vanellye.codexgen.dataresonance.DataResonanceScreen
import com.vanellye.codexgen.gitbridge.GitBridgeScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                var destination by remember { mutableStateOf("CodeGen") }
                Surface(Modifier.fillMaxSize()) {
                    Column(Modifier.fillMaxSize()) {
                        Row(Modifier.fillMaxWidth().padding(4.dp)) {
                            listOf("CodeGen", "Git", "Resonance").forEach { item ->
                                Button(
                                    onClick = { destination = item },
                                    modifier = Modifier.weight(1f).padding(2.dp)
                                ) { Text(item) }
                            }
                        }
                        when (destination) {
                            "Git" -> GitBridgeScreen()
                            "Resonance" -> DataResonanceScreen()
                            else -> CodeGenRoute(Modifier.weight(1f))
                        }
                    }
                }
            }
        }
    }
}
