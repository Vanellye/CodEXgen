package com.vanellye.eria

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material.Button
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Surface
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

/**
 * ERIA HOME: a transparent entry point for the current workspace.
 *
 * MULTIPLY and SPREAD are presented as governed workflows. This screen does
 * not create branches, alter files, publish content, or grant permissions.
 */
@Composable
fun HomeScreen(
    onOpenCodeGenerator: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(modifier = modifier.fillMaxSize(), color = MaterialTheme.colors.background) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text("ERIA · HOME", style = MaterialTheme.typography.h4)
            Text("Hômmmë Bõđďiê§", style = MaterialTheme.typography.h5)
            Text(
                "A home identity is a named workspace with its own scope, source, " +
                    "and permission boundary."
            )

            Text("PL·Lêâ§ëə Directive", style = MaterialTheme.typography.h6)
            Text("✖ MULTIPLY")
            Text(
                "Prepare distinct derivatives from a recorded source revision. " +
                    "Each derivative keeps its own identity and parent lineage."
            )
            Text("ð SPREAD")
            Text(
                "Propagate approved principles and recall references across Root, " +
                    "Main, and StridePath without silently copying authority."
            )

            Text("Ĥõmmmïîịëê§ ÖvêrŘidĕ", style = MaterialTheme.typography.h6)
            Text(
                "No override is active. A change requires an identified actor, " +
                    "specific scope, approval record, validation, and recovery path."
            )

            Text("Written Scripture · Quote Record", style = MaterialTheme.typography.h6)
            Text(
                "Quotes retain exact wording, author or source, edition or translation, " +
                    "location, rights status, and verification state. Interpretations " +
                    "remain distinct from the quoted text."
            )

            Spacer(modifier = Modifier.height(4.dp))
            Button(
                onClick = onOpenCodeGenerator,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Open Code Generator")
            }
        }
    }
}
