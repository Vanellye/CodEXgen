package com.vanellye.eria.orchid

import android.content.Context
import android.content.Intent

class OrchidKeyboardApi(context: Context) {
    private val registry = SymbolRegistry(context.applicationContext)
    private val composer = ExpressionComposer(registry)
    fun symbols(): List<OrchidSymbol> = registry.all()
    fun compose(symbolIds: List<String>): OrchidExpression = composer.compose(symbolIds)
    fun addPrivateSymbol(name: String, glyph: String, meaning: String) = registry.addPrivate(name,glyph,meaning)
    fun importPrivatePack(json: String): Int = registry.importPrivate(json)
    fun createShareIntent(): Intent = Intent(Intent.ACTION_SEND).apply {
        type = "application/json"
        putExtra(Intent.EXTRA_SUBJECT, "ORCHID private symbol pack")
        putExtra(Intent.EXTRA_TEXT, registry.exportPrivatePack())
    }
}
