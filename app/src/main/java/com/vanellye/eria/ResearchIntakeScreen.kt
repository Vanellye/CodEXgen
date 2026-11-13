package com.vanellye.eria

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.Button
import androidx.compose.material.Checkbox
import androidx.compose.material.DropdownMenu
import androidx.compose.material.DropdownMenuItem
import androidx.compose.material.MaterialTheme
import androidx.compose.material.OutlinedTextField
import androidx.compose.material.Surface
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.vanellye.eria.evolutionary.DataSensitivity
import com.vanellye.eria.evolutionary.IntakeOrigin
import com.vanellye.eria.evolutionary.QuestionnaireAuthority
import com.vanellye.eria.evolutionary.ResearchIntakeQuestionnaire
import com.vanellye.eria.evolutionary.SequenceFormat

@Composable
fun ResearchIntakeScreen(onOpenCodeGenerator: () -> Unit) {
    var projectId by remember { mutableStateOf("") }
    var purpose by remember { mutableStateOf("") }
    var organism by remember { mutableStateOf("") }
    var accession by remember { mutableStateOf("") }
    var assembly by remember { mutableStateOf("") }
    var authorizationReference by remember { mutableStateOf("") }
    var origin by remember { mutableStateOf(IntakeOrigin.EXISTING_SEQUENCE) }
    var format by remember { mutableStateOf(SequenceFormat.FASTA) }
    var authorityConfirmed by remember { mutableStateOf(false) }
    var clinicalAuthorization by remember { mutableStateOf(false) }
    var directIdentifiers by remember { mutableStateOf(false) }
    var submitted by remember { mutableStateOf(false) }
    var captured by remember { mutableStateOf<ResearchIntakeQuestionnaire?>(null) }
    var errors by remember { mutableStateOf(emptyList<String>()) }

    val sensitivity = when (origin) {
        IntakeOrigin.EXISTING_SEQUENCE -> DataSensitivity.RESTRICTED_GENOMIC
        IntakeOrigin.PUBLIC_REFERENCE -> DataSensitivity.PUBLIC
        IntakeOrigin.SYNTHETIC -> DataSensitivity.SYNTHETIC_ONLY
    }
    val authority = when (origin) {
        IntakeOrigin.EXISTING_SEQUENCE -> if (authorityConfirmed) QuestionnaireAuthority.USER_AUTHORITY_RECORDED else QuestionnaireAuthority.NOT_CONFIRMED
        IntakeOrigin.PUBLIC_REFERENCE -> if (authorityConfirmed) QuestionnaireAuthority.PUBLIC_TERMS_RECORDED else QuestionnaireAuthority.NOT_CONFIRMED
        IntakeOrigin.SYNTHETIC -> QuestionnaireAuthority.SYNTHETIC_FIXTURE
    }

    Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colors.background) {
        Column(
            modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text("ERIA · Research intake", style = MaterialTheme.typography.h5)
            Text(
                "Complete the source and study declarations before sequence intake. This screen records declarations; it does not verify institutional approvals or clinical authorization.",
                style = MaterialTheme.typography.body2
            )

            OutlinedTextField(projectId, { projectId = it }, label = { Text("Project ID") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(purpose, { purpose = it }, label = { Text("Research purpose") }, modifier = Modifier.fillMaxWidth(), minLines = 2)
            OutlinedTextField(organism, { organism = it }, label = { Text("Organism (or unknown)") }, modifier = Modifier.fillMaxWidth())
            Text("Sequence source", style = MaterialTheme.typography.subtitle1)
            ChoiceMenu(
                label = when (origin) {
                    IntakeOrigin.EXISTING_SEQUENCE -> "Existing sequence file"
                    IntakeOrigin.PUBLIC_REFERENCE -> "Public reference"
                    IntakeOrigin.SYNTHETIC -> "Synthetic test fixture"
                },
                options = listOf("Existing sequence file", "Public reference", "Synthetic test fixture"),
                onSelect = {
                    origin = when (it) {
                        "Public reference" -> IntakeOrigin.PUBLIC_REFERENCE
                        "Synthetic test fixture" -> IntakeOrigin.SYNTHETIC
                        else -> IntakeOrigin.EXISTING_SEQUENCE
                    }
                    authorityConfirmed = false
                    captured = null
                    submitted = false
                }
            )
            Text("Sequence format", style = MaterialTheme.typography.subtitle1)
            ChoiceMenu(
                label = format.name,
                options = listOf("FASTA", "FASTQ"),
                onSelect = { format = if (it == "FASTQ") SequenceFormat.FASTQ else SequenceFormat.FASTA; captured = null; submitted = false }
            )
            if (origin == IntakeOrigin.PUBLIC_REFERENCE) {
                OutlinedTextField(accession, { accession = it }, label = { Text("Exact accession and version") }, modifier = Modifier.fillMaxWidth())
            }
            OutlinedTextField(assembly, { assembly = it }, label = { Text("Reference assembly (optional)") }, modifier = Modifier.fillMaxWidth())

            if (origin != IntakeOrigin.SYNTHETIC) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(checked = authorityConfirmed, onCheckedChange = { authorityConfirmed = it; captured = null; submitted = false })
                    Text(if (origin == IntakeOrigin.PUBLIC_REFERENCE) "I reviewed the public source license/terms" else "I confirm I have authority to use this sequence data")
                }
            } else {
                Text("Synthetic fixture · classified as non-biological test data")
            }

            Text("Clinical / ethics authorization declaration", style = MaterialTheme.typography.subtitle1)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Checkbox(checked = clinicalAuthorization, onCheckedChange = { clinicalAuthorization = it; captured = null; submitted = false })
                Text("I declare that applicable clinical/ethics authorization has been obtained")
            }
            if (clinicalAuthorization) {
                OutlinedTextField(
                    authorizationReference,
                    { authorizationReference = it; captured = null; submitted = false },
                    label = { Text("Approval or protocol reference (do not enter patient identifiers)") },
                    modifier = Modifier.fillMaxWidth()
                )
            }
            Text(
                "This is a submitter attestation only. ERIA does not validate the approval, consent, scope, or issuing institution. It does not authorize diagnosis, treatment, sample handling, or biological modification.",
                style = MaterialTheme.typography.caption
            )

            Row(verticalAlignment = Alignment.CenterVertically) {
                Checkbox(checked = directIdentifiers, onCheckedChange = { directIdentifiers = it; captured = null; submitted = false })
                Text("The sequence or attached metadata contains direct personal identifiers")
            }
            Text("Genomic sequence can itself be identifying even without names or contact details.", style = MaterialTheme.typography.caption)

            Button(
                onClick = {
                    val form = ResearchIntakeQuestionnaire(
                        projectId = projectId.trim(),
                        researchPurpose = purpose.trim(),
                        organism = organism.trim(),
                        sourceOrigin = origin,
                        sequenceFormat = format,
                        authority = authority,
                        dataSensitivity = sensitivity,
                        declaredAccession = accession.trim().ifBlank { null },
                        referenceAssembly = assembly.trim().ifBlank { null },
                        containsDirectIdentifiers = directIdentifiers,
                        clinicalAuthorizationDeclared = clinicalAuthorization,
                        clinicalAuthorizationReference = authorizationReference.trim().ifBlank { null }
                    )
                    val issues = buildList {
                        if (projectId.isBlank()) add("Project ID is required")
                        if (purpose.isBlank()) add("Research purpose is required")
                        if (organism.isBlank()) add("Organism is required; enter unknown if not established")
                        if (origin == IntakeOrigin.PUBLIC_REFERENCE && accession.isBlank()) add("Exact public accession is required")
                        if (origin != IntakeOrigin.SYNTHETIC && !authorityConfirmed) add("Confirm the applicable data-use authority or public terms review")
                        if (clinicalAuthorization && authorizationReference.isBlank()) add("Add an approval/protocol reference or leave the authorization declaration unchecked")
                        if (directIdentifiers) add("Remove direct personal identifiers before sequence intake")
                    }
                    errors = issues
                    captured = if (issues.isEmpty()) form else null
                    submitted = true
                },
                modifier = Modifier.fillMaxWidth()
            ) { Text("Validate and capture questionnaire") }

            if (submitted && errors.isNotEmpty()) {
                Text("Not ready", color = MaterialTheme.colors.error, style = MaterialTheme.typography.subtitle1)
                errors.forEach { Text("• $it", color = MaterialTheme.colors.error) }
            }
            if (captured != null) {
                Text("Questionnaire captured in this screen session", color = MaterialTheme.colors.primary, style = MaterialTheme.typography.subtitle1)
                Text("Source: ${captured!!.sourceOrigin} · Format: ${captured!!.sequenceFormat}")
                Text("Data-use declaration: ${captured!!.authority} · Sensitivity: ${captured!!.dataSensitivity}")
                Text("Clinical authorization declared: ${captured!!.clinicalAuthorizationDeclared}")
                Text("The captured form is held in memory only. No sequence file has been selected, uploaded, or ingested.")
            }
            Spacer(Modifier.height(8.dp))
            Button(onClick = onOpenCodeGenerator, modifier = Modifier.fillMaxWidth()) {
                Text("Open code generator")
            }
        }
    }
}

@Composable
private fun ChoiceMenu(label: String, options: List<String>, onSelect: (String) -> Unit) {
    var expanded by remember { mutableStateOf(false) }
    Column {
        Button(onClick = { expanded = true }, modifier = Modifier.fillMaxWidth()) { Text(label) }
        DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            options.forEach { option ->
                DropdownMenuItem(onClick = { expanded = false; onSelect(option) }) { Text(option) }
            }
        }
    }
}
