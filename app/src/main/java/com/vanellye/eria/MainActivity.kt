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
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.vanellye.eria.orchid.OrchidSymbolManagerActivity

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    Column {
                        Button(
                            onClick = { startActivity(Intent(this@MainActivity, OrchidSymbolManagerActivity::class.java)) },
                            modifier = Modifier.padding(12.dp)
                        ) { Text("ORCHID • Private Symbols & Keyboard") }
                        CodeGenRoute()
                    }
                }
            }
        }
    }
}
