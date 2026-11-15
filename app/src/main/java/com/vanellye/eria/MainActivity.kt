package com.vanellye.eria

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.weight
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

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    var showSavedDollars by remember { mutableStateOf(false) }
                    Column(modifier = Modifier.fillMaxSize()) {
                        Row(modifier = Modifier.padding(8.dp)) {
                            Button(onClick = { showSavedDollars = !showSavedDollars }) {
                                Text(if (showSavedDollars) "Return to ERIA" else "Open Saved Dollars")
                            }
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            if (showSavedDollars) SavedDollarsScreen() else CodeGenRoute()
                        }
                    }
                }
            }
        }
    }
}
