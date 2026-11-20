package com.vanellye.eria.contracts

import android.content.Context
import java.io.File

/**
 * Application entry point for correction-aware documents.
 *
 * The journal is stored under app-private filesDir; it is not exposed to other apps
 * and is not sent to a network destination.
 */
object EriaCorrectionRuntime {
    private const val JOURNAL_FILE = "eria-correction-lineage.log"

    fun journal(context: Context): CorrectionLineageJournal =
        FileCorrectionLineageJournal(
            File(context.applicationContext.filesDir, JOURNAL_FILE)
        )

    fun document(
        context: Context,
        originalText: String,
        provenance: WritingProvenance = WritingProvenance()
    ): SkribedDocument = SkribedDocument(
        originalText = originalText,
        correctionJournal = journal(context),
        provenance = provenance
    )
}
