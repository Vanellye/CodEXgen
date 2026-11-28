package com.vanellye.eria.orchid

data class OrchidExpression(val symbols: List<OrchidSymbol>) {
    init { require(symbols.isNotEmpty()) { "An expression needs at least one symbol." } }
    fun text(): String = symbols.joinToString("") { it.glyph }
    fun symbolIds(): List<String> = symbols.map { it.id }
}

class ExpressionComposer(private val registry: SymbolRegistry) {
    fun compose(ids: List<String>): OrchidExpression {
        require(ids.isNotEmpty()) { "Select at least one symbol." }
        val index = registry.all().associateBy { it.id }
        return OrchidExpression(ids.map { index[it] ?: error("Unknown symbol ID: $it") })
    }
}
