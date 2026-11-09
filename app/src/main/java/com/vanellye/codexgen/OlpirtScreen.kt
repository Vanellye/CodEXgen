package com.vanellye.codexgen

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.vanellye.codexgen.nativebridge.OlpirtNativeBridge

@Composable
fun OlpirtScreen() {
    val report = remember { OlpirtNativeBridge.status() }
    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        Text("OLPIRT • LIGHT BRIDGE", style = MaterialTheme.typography.h6)
        Text("VelumAetheris is the boundary; Pons resolves explicit interfaces; Olpirt illuminates dependency paths; FreedomBridge exports a portable audit.")
        Text(report, style = MaterialTheme.typography.body2)
        Text("Freedom rule: dependencies stay visible, modules stay explainable, and providers remain replaceable by the host application.")
        Text("This is a software dependency auditor. It does not access an ether, infer hidden services, or claim biological effects.")
    }
}
