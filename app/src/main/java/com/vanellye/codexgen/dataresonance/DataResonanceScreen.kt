package com.vanellye.codexgen.dataresonance

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.Button
import androidx.compose.material.MaterialTheme
import androidx.compose.material.OutlinedButton
import androidx.compose.material.OutlinedTextField
import androidx.compose.material.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.text.DateFormat
import java.util.Date

@Composable
fun DataResonanceScreen() {
    val context = LocalContext.current
    val store = remember { DataResonanceStore(context) }
    var channel by remember { mutableStateOf("signal-a") }
    var sample by remember { mutableStateOf("") }
    var unit by remember { mutableStateOf("") }
    var biomarker by remember { mutableStateOf("") }
    var frequencyHz by remember { mutableStateOf("11") }
    var notes by remember { mutableStateOf("") }
    var channelA by remember { mutableStateOf("signal-a") }
    var channelB by remember { mutableStateOf("signal-b") }
    var observations by remember { mutableStateOf(store.recent()) }
    var analysis by remember { mutableStateOf("Enter observations in two channels to calculate an exploratory correlation.") }
    var error by remember { mutableStateOf<String?>(null) }

    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text("DATA RESONANCE", style = MaterialTheme.typography.h6)
        Text("Local signal and measurement notebook. Frequency and biomarker fields are metadata only.")
        OutlinedTextField(channel, { channel = it }, label = { Text("Channel") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(sample, { sample = it }, label = { Text("Measured value") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(unit, { unit = it }, label = { Text("Unit (optional)") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(biomarker, { biomarker = it }, label = { Text("Biomarker label (optional)") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(
            frequencyHz, { frequencyHz = it },
            label = { Text("Reference frequency in Hz (11 Hz = 11; 11 GHz = 11000000000)") },
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(notes, { notes = it }, label = { Text("Notes (optional)") }, modifier = Modifier.fillMaxWidth())
        Button(
            onClick = {
                error = null
                runCatching {
                    val value = sample.toDouble()
                    val frequency = frequencyHz.trim().takeIf { it.isNotEmpty() }?.toDouble()
                    store.add(channel, value, unit, biomarker, frequency, notes)
                    observations = store.recent()
                    sample = ""
                    notes = ""
                }.onFailure { error = it.message ?: "Could not save observation." }
            },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Save local observation") }
        error?.let { Text(it, color = MaterialTheme.colors.error) }

        Text("Exploratory channel comparison", style = MaterialTheme.typography.subtitle1)
        OutlinedTextField(channelA, { channelA = it }, label = { Text("Channel A") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(channelB, { channelB = it }, label = { Text("Channel B") }, modifier = Modifier.fillMaxWidth())
        OutlinedButton(
            onClick = {
                val (count, r) = store.correlation(channelA, channelB)
                analysis = if (r == null) "Not enough varying paired samples (n=$count)."
                else "Index-aligned Pearson correlation: r = %.4f (n=$count).".format(r)
            },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Calculate correlation") }
        Text(analysis)

        Text("Recent observations (${observations.size})", style = MaterialTheme.typography.subtitle1)
        observations.forEach { item ->
            val date = DateFormat.getDateTimeInstance().format(Date(item.timestampMs))
            Text(
                "${item.channel}: ${item.value} ${item.unit} • $date" +
                    (item.biomarker?.let { " • biomarker: $it" } ?: "") +
                    (item.referenceFrequencyHz?.let { " • reference: $it Hz" } ?: ""),
                style = MaterialTheme.typography.body2
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(onClick = { observations = store.recent() }) { Text("Refresh") }
            OutlinedButton(onClick = { store.close(); observations = emptyList() }) { Text("Close store") }
        }
        Text(
            "Interpretation limits: correlation is not causation. Frequency annotations do not emit signals or demonstrate effects on DNA/RNA. Data is stored in this app's private SQLite database; it is not uploaded, but the database itself is not encrypted.",
            style = MaterialTheme.typography.caption
        )
    }
}
