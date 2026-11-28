package com.vanellye.eria.orchid

import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.inputmethodservice.InputMethodService
import android.text.Editable
import android.text.TextWatcher
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView

/**
 * ORCHID keyboard with a familiar Samsung-style QWERTY base and a dedicated
 * symbol layer. It is an independently implemented layout, not Samsung code
 * or a copy of Samsung's proprietary assets.
 */
class OrchidSymbolImeService : InputMethodService() {
    private lateinit var registry: SymbolRegistry
    private lateinit var database: OrchidSymbolDatabase
    private lateinit var root: LinearLayout
    private lateinit var symbolPanel: LinearLayout
    private lateinit var search: EditText
    private var symbolMode = false
    private var selectedKind: String? = null

    override fun onCreate() {
        super.onCreate()
        registry = SymbolRegistry(applicationContext)
        database = OrchidSymbolDatabase(applicationContext)
    }

    override fun onCreateInputView(): View {
        root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(4), dp(4), dp(4), dp(6))
            setBackgroundColor(Color.rgb(18, 19, 23))
        }

        val toolbar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        listOf("✦" to "Tools", "☺" to "Emoji", "GIF" to "GIF", "▦" to "Clipboard").forEach { (label, desc) ->
            toolbar.addView(toolButton(label, desc) { showSymbols(false) }, weightedParams())
        }
        toolbar.addView(toolButton("ORC", "Open ORCHID symbols") {
            showSymbols(true)
        }, weightedParams())
        toolbar.addView(toolButton("⚙", "ORCHID symbol manager") {
            val intent = packageManager.getLaunchIntentForPackage(packageName)
            intent?.addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)
            if (intent != null) startActivity(intent)
        }, weightedParams())
        root.addView(toolbar)

        symbolPanel = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            visibility = View.GONE
        }
        search = EditText(this).apply {
            hint = "Search ORCHID symbols"
            setSingleLine(true)
            textSize = 14f
            setTextColor(Color.WHITE)
            setHintTextColor(Color.LTGRAY)
            setPadding(dp(12), dp(5), dp(12), dp(5))
        }
        symbolPanel.addView(search)
        val filters = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
        }
        listOf("ALL" to null, "CHRONO" to "chronoglyph", "WORDS" to "keyword",
            "OPS" to "operator", "LIVING" to "living-symbol", "IDEAS" to "concept").forEach { (label, kind) ->
            filters.addView(toolButton(label, "Filter $label") {
                selectedKind = kind
                renderSymbols(search.text?.toString().orEmpty())
            }, weightedParams())
        }
        symbolPanel.addView(filters)
        val symbolScroll = android.widget.ScrollView(this)
        val symbolResults = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        symbolScroll.addView(symbolResults)
        symbolPanel.addView(symbolScroll, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dp(174)
        ))
        root.addView(symbolPanel)

        fun drawResults(query: String) {
            symbolResults.removeAllViews()
            val matches = (if (query.isBlank()) database.all() else database.search(query))
                .filter { selectedKind == null || it.kind == selectedKind }.take(36)
            if (matches.isEmpty()) {
                symbolResults.addView(TextView(this).apply {
                    text = "No matching symbols"
                    setTextColor(Color.LTGRAY)
                    setPadding(dp(8), dp(8), dp(8), dp(8))
                })
                return
            }
            matches.chunked(5).forEach { group ->
                val row = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
                group.forEach { record ->
                    row.addView(keyButton(record.glyph, record.name) {
                        commitGlyph(database.insertText(record.id), record.name)
                    }, weightedParams())
                }
                symbolResults.addView(row)
            }
        }
        // Keep the result renderer in a field-independent listener for category/search updates.
        symbolSearchRenderer = { query -> drawResults(query) }
        search.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) = Unit
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                drawResults(s?.toString().orEmpty())
            }
            override fun afterTextChanged(s: Editable?) = Unit
        })
        drawResults("")

        val numberRow = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        "1234567890".forEach { digit ->
            numberRow.addView(keyButton(digit.toString()) { commitGlyph(digit.toString()) }, weightedParams())
        }
        root.addView(numberRow)

        addLetterRow("QWERTYUIOP")
        val middle = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(dp(12), 0, dp(12), 0)
        }
        "ASDFGHJKL".forEach { letter ->
            middle.addView(keyButton(letter.toString()) { commitGlyph(letter.toString()) }, weightedParams())
        }
        root.addView(middle)

        val bottomLetters = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        bottomLetters.addView(keyButton("⇧", "Shift") { shift = !shift; refreshCase() }, weightedParams())
        "ZXCVBNM".forEach { letter ->
            bottomLetters.addView(keyButton(letter.toString()) { commitGlyph(if (shift) letter.toString() else letter.lowercase()) }, weightedParams())
        }
        bottomLetters.addView(keyButton("⌫", "Delete") {
            currentInputConnection?.deleteSurroundingTextInCodePoints(1, 0)
        }, weightedParams())
        root.addView(bottomLetters)

        val actionRow = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        actionRow.addView(keyButton("!#1", "Symbols and punctuation") {
            showSymbols(!symbolMode)
        }, LinearLayout.LayoutParams(0, dp(48), 1.2f))
        actionRow.addView(keyButton(",", "Comma") { commitGlyph(",") }, weightedParams())
        actionRow.addView(keyButton("English (US)", "Space") { commitGlyph(" ") }, LinearLayout.LayoutParams(0, dp(48), 4f))
        actionRow.addView(keyButton(".", "Period") { commitGlyph(".") }, weightedParams())
        actionRow.addView(keyButton("↵", "Enter") { sendEnter() }, LinearLayout.LayoutParams(0, dp(48), 1.2f))
        root.addView(actionRow)

        return root
    }

    private var symbolSearchRenderer: ((String) -> Unit)? = null
    private var shift = false

    private fun addLetterRow(value: String) {
        val row = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        value.forEach { letter ->
            row.addView(keyButton(letter.toString()) {
                commitGlyph(if (shift) letter.toString() else letter.lowercase())
                if (shift) { shift = false; refreshCase() }
            }, weightedParams())
        }
        root.addView(row)
    }

    private fun refreshCase() {
        // New input view redraws case state when Android recreates the IME view.
    }

    private fun showSymbols(show: Boolean) {
        symbolMode = show
        symbolPanel.visibility = if (show) View.VISIBLE else View.GONE
    }

    private fun renderSymbols(query: String) {
        symbolSearchRenderer?.invoke(query)
    }

    private fun commitGlyph(value: String, label: String? = null) {
        currentInputConnection?.commitText(value, 1)
        if (label != null) announceForAccessibility("$label inserted")
    }

    private fun sendEnter() {
        val action = currentInputEditorInfo?.imeOptions?.and(EditorInfo.IME_MASK_ACTION)
        if (action != null && action != EditorInfo.IME_ACTION_NONE && action != EditorInfo.IME_ACTION_UNSPECIFIED) {
            currentInputConnection?.performEditorAction(action)
        } else {
            commitGlyph("\n")
        }
    }

    private fun toolButton(label: String, description: String, action: () -> Unit) =
        keyButton(label, description, action)

    private fun keyButton(label: String, description: String = label, action: () -> Unit): Button =
        Button(this).apply {
            text = label
            contentDescription = description
            isAllCaps = false
            textSize = if (label.length > 4) 11f else 16f
            minWidth = 0
            minimumWidth = 0
            minHeight = dp(42)
            minimumHeight = dp(42)
            setPadding(dp(2), dp(2), dp(2), dp(2))
            setTextColor(Color.WHITE)
            background = GradientDrawable().apply {
                setColor(if (label == "ORC") Color.rgb(75, 62, 120) else Color.rgb(54, 56, 62))
                cornerRadius = dp(7).toFloat()
            }
            setOnClickListener { action() }
        }

    private fun weightedParams() =
        LinearLayout.LayoutParams(0, dp(48), 1f).apply {
            setMargins(dp(2), dp(3), dp(2), dp(3))
        }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
}
