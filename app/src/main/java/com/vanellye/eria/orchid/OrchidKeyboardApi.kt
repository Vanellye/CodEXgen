package com.vanellye.eria.orchid

import android.content.Context
import android.content.Intent

class OrchidKeyboardApi(context: Context) {
    private val registry = SymbolRegistry(context.applicationContext)
    private val composer = ExpressionComposer(registry)
    private val database = OrchidSymbolDatabase(context.applicationContext)
    fun symbols(): List<OrchidSymbol> = registry.all()
    fun databaseRecords(): List<OrchidDatabaseRecord> = database.all()
    fun searchDatabase(query: String, kind: String? = null): List<OrchidDatabaseRecord> = database.search(query, kind)
    fun databaseInsertText(recordId: String): String = database.insertText(recordId)
    fun compose(symbolIds: List<String>): OrchidExpression = composer.compose(symbolIds)
    fun addPrivateSymbol(name: String, glyph: String, meaning: String) = registry.addPrivate(name,glyph,meaning)
    fun importPrivatePack(json: String): Int = registry.importPrivate(json)
    fun createShareIntent(): Intent = Intent(Intent.ACTION_SEND).apply {
        type = "application/json"
        putExtra(Intent.EXTRA_SUBJECT, "ORCHID private symbol pack")
        putExtra(Intent.EXTRA_TEXT, registry.exportPrivatePack())
    }
}
