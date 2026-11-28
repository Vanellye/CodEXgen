package com.vanellye.eria.orchid

import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.inputmethodservice.InputMethodService
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.text.Editable
import android.text.TextWatcher
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.widget.Button
import android.widget.EditText
import android.widget.HorizontalScrollView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

/**
 * Independent ORCHID input method with a familiar QWERTY layout.
 * It does not replace or modify Samsung Keyboard; Android keeps both IMEs selectable.
 */
class OrchidSymbolImeService : InputMethodService() {
    private lateinit var registry: SymbolRegistry
    private lateinit var database: OrchidSymbolDatabase
    private lateinit var root: LinearLayout
    private lateinit var symbolPanel: LinearLayout
    private lateinit var keyboardPanel: LinearLayout
    private lateinit var search: EditText
    private var selectedCategory = "All"
    private var shift = false
    private val letterKeys = mutableListOf<Pair<Button, Char>>()
    private var keyHeight = 48
    private var keyColor = Color.rgb(47, 50, 57)
    private var panelColor = Color.rgb(22, 24, 29)
    private var accentColor = Color.rgb(128, 111, 210)

    private data class Entry(val id: String, val name: String, val glyph: String, val meaning: String, val kind: String, val origin: String)

    override fun onCreate() {
        super.onCreate()
        registry = SymbolRegistry(applicationContext)
        database = OrchidSymbolDatabase(applicationContext)
    }

    override fun onCreateInputView(): View =
        runCatching { buildInputView() }.getOrElse { error -> buildFallbackInputView(error) }

    private fun buildInputView(): View {
        applyPreferences()
        letterKeys.clear()
        root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(5), dp(5), dp(5), dp(7))
            setBackgroundColor(panelColor)
        }

        val toolbar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        toolbar.addView(toolButton("⌂", "Core symbol layer") { selectedCategory = "Core"; showSymbols(true); renderSymbols() }, weightedParams())
        toolbar.addView(toolButton("☆", "Favorites") {
            selectedCategory = "Favorites"; showSymbols(true); renderSymbols()
        }, weightedParams())
        toolbar.addView(toolButton("◷", "Clock and time layer") {
            selectedCategory = "Time"; showSymbols(true); renderSymbols()
        }, weightedParams())
        toolbar.addView(toolButton("ORCHID", "Open symbol library") {
            selectedCategory = "All"; showSymbols(!symbolPanel.isShown); renderSymbols()
        }, LinearLayout.LayoutParams(0, dp(keyHeight), 2.1f))
        toolbar.addView(toolButton("⚙", "ORCHID settings and private studio") { launchStudio() }, weightedParams())
        root.addView(toolbar)

        symbolPanel = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            visibility = View.GONE
            setPadding(dp(3), dp(4), dp(3), dp(3))
            background = rounded(panelColor, 12)
        }
        search = EditText(this).apply {
            hint = "Search symbols, meanings, keywords…"
            setSingleLine(true)
            textSize = 14f
            setTextColor(Color.WHITE)
            setHintTextColor(Color.LTGRAY)
            setPadding(dp(12), 0, dp(12), 0)
            background = rounded(Color.rgb(42, 44, 51), 10)
        }
        symbolPanel.addView(search, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(42)))

        val categoryScroller = HorizontalScrollView(this).apply { isHorizontalScrollBarEnabled = false }
        val categoryRow = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        val categories = listOf("Core", "Favorites", "Time", "All", "Recent", "Chrono", "Words", "Operators", "Living", "Concepts", "Private")
        categories.forEach { category ->
            categoryRow.addView(categoryButton(category) {
                selectedCategory = category
                renderSymbols()
            })
        }
        categoryScroller.addView(categoryRow)
        symbolPanel.addView(categoryScroller)

        val symbolScroll = ScrollView(this).apply { isFillViewport = false }
        val symbolResults = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        symbolScroll.addView(symbolResults)
        symbolPanel.addView(symbolScroll, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dp(if (keyHeight >= 52) 202 else 174)
        ))
        root.addView(symbolPanel)
        keyboardPanel = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }

        fun drawResults(query: String) {
            symbolResults.removeAllViews()
            val needle = query.trim()
            val entries = matchingEntries(needle).take(80)
            if (entries.isEmpty()) {
                symbolResults.addView(TextView(this).apply {
                    text = database.loadError?.let { "Symbol fixture unavailable — QWERTY fallback remains active. $it" } ?: "No matching symbols"
                    setTextColor(Color.LTGRAY)
                    setPadding(dp(12), dp(14), dp(12), dp(14))
                })
                return
            }
            entries.chunked(4).forEach { group ->
                val row = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
                group.forEach { entry ->
                    val tile = LinearLayout(this).apply {
                        orientation = LinearLayout.VERTICAL
                        gravity = Gravity.CENTER
                        setPadding(dp(2), dp(2), dp(2), dp(2))
                        background = rounded(Color.rgb(35, 38, 45), 9)
                    }
                    val glyphButton = keyButton(entry.glyph, "${entry.name}, ${entry.meaning}") {
                        currentInputConnection?.commitText(entry.glyph, 1)
                        registry.recordRecent(entry.id)
                        root.announceForAccessibility("${entry.name} inserted")
                    }.apply { textSize = if (entry.glyph.length > 3) 18f else 24f }
                    tile.addView(glyphButton, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(42)))
                    val meta = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER }
                    meta.addView(TextView(this).apply {
                        text = entry.name.take(10)
                        textSize = 9f
                        setTextColor(Color.LTGRAY)
                        gravity = Gravity.CENTER
                        maxLines = 1
                    }, LinearLayout.LayoutParams(0, dp(22), 1f))
                    meta.addView(TextView(this).apply {
                        text = if (registry.isFavorite(entry.id)) "★" else "☆"
                        textSize = 14f
                        setTextColor(if (registry.isFavorite(entry.id)) accentColor else Color.LTGRAY)
                        setPadding(dp(3), 0, dp(3), 0)
                        contentDescription = "Toggle favorite"
                        setOnClickListener {
                            registry.toggleFavorite(entry.id)
                            drawResults(search.text?.toString().orEmpty())
                        }
                    })
                    tile.addView(meta)
                    row.addView(tile, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f).apply {
                        setMargins(dp(2), dp(2), dp(2), dp(2))
                    })
                }
                repeat(4 - group.size) {
                    row.addView(View(this), LinearLayout.LayoutParams(0, 1, 1f))
                }
                symbolResults.addView(row)
            }
        }
        symbolSearchRenderer = { query -> drawResults(query) }
        search.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) = Unit
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) { drawResults(s?.toString().orEmpty()) }
            override fun afterTextChanged(s: Editable?) = Unit
        })
        drawResults("")

        if (registry.booleanSetting(SymbolRegistry.KEY_NUMBER_ROW, true)) {
            addKeyRow("1234567890", 1f)
        }
        addLetterRow("qwertyuiop", 1f)
        addLetterRow("asdfghjkl", 1f, inset = 10)
        val bottom = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        bottom.addView(keyButton("⇧", "Shift") { shift = !shift; updateLetterLabels() }, weightedParams(1.25f))
        "zxcvbnm".forEach { letter ->
            val key = keyButton(labelFor(letter), letter.toString()) {
                commitKey(letter.toString())
                if (shift) { shift = false; updateLetterLabels() }
            }
            letterKeys.add(key to letter)
            bottom.addView(key, weightedParams())
        }
        bottom.addView(keyButton("⌫", "Delete") {
            currentInputConnection?.deleteSurroundingTextInCodePoints(1, 0)
            vibrateKey()
        }, weightedParams(1.25f))
        keyboardPanel.addView(bottom)

        val actions = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        actions.addView(keyButton("!#1", "Symbols and punctuation") {
            selectedCategory = "All"; showSymbols(!symbolPanel.isShown); renderSymbols()
        }, weightedParams(1.25f))
        actions.addView(keyButton(",", "Comma") { commitKey(",") }, weightedParams())
        actions.addView(keyButton("English (US)", "Space") { commitKey(" ") }, weightedParams(4f))
        actions.addView(keyButton(".", "Period") { commitKey(".") }, weightedParams())
        actions.addView(keyButton("↵", "Enter") { sendEnter() }, weightedParams(1.25f))
        keyboardPanel.addView(actions)
        root.addView(keyboardPanel)
        return root
    }

    private fun buildFallbackInputView(error: Throwable): View {
        val panel = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(6), dp(6), dp(6), dp(6))
            setBackgroundColor(Color.rgb(22, 24, 29))
        }
        panel.addView(TextView(this).apply {
            text = "ORCHID safe keyboard · symbol layer paused"
            setTextColor(Color.WHITE)
            textSize = 12f
            setPadding(dp(6), dp(4), dp(6), dp(8))
            contentDescription = error.message ?: "Symbol browser unavailable"
        })
        listOf("qwertyuiop", "asdfghjkl", "⇧zxcvbnm⌫").forEach { letters ->
            val row = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
            letters.forEach { character ->
                row.addView(Button(this).apply {
                    text = character.toString()
                    isAllCaps = false
                    minWidth = 0
                    setPadding(dp(1), 0, dp(1), 0)
                    setOnClickListener {
                        when (character) {
                            '⌫' -> currentInputConnection?.deleteSurroundingText(1, 0)
                            '⇧' -> Unit
                            else -> currentInputConnection?.commitText(character.toString(), 1)
                        }
                    }
                }, LinearLayout.LayoutParams(0, dp(44), 1f).apply {
                    setMargins(dp(1), dp(1), dp(1), dp(1))
                })
            }
            panel.addView(row)
        }
        panel.addView(Button(this).apply {
            text = "Space"
            setOnClickListener { currentInputConnection?.commitText(" ", 1) }
        })
        return panel
    }

    private var symbolSearchRenderer: ((String) -> Unit)? = null

    private fun matchingEntries(query: String): List<Entry> {
        val databaseEntries = database.all().map {
            Entry(it.id, it.name, it.glyph, it.meaning, it.kind, "CANONICAL")
        }
        val privateEntries = registry.all()
            .filter { it.origin == "LOCAL_PRIVATE" || it.origin == "IMPORTED_PRIVATE" }
            .map { Entry(it.id, it.name, it.glyph, it.meaning, "private", it.origin) }
        val all = (databaseEntries + privateEntries).distinctBy { it.id }
        val recentIds = registry.recent()
        val favoriteIds = registry.favorites()
        val categoryEntries = when (selectedCategory) {
            "Core" -> all.filter { it.kind == "core-layer" }
            "Time" -> all.filter { it.kind == "time-layer" || it.kind == "chronoglyph" }
            "Recent" -> all.filter { it.id in recentIds }.sortedBy { recentIds.indexOf(it.id) }
            "Favorites" -> all.filter { it.id in favoriteIds }
            "Chrono" -> all.filter { it.kind.contains("chrono", true) || it.id.startsWith("ORC-CG") }
            "Words" -> all.filter { it.kind == "keyword" }
            "Operators" -> all.filter { it.kind == "operator" }
            "Living" -> all.filter { it.kind == "living-symbol" }
            "Concepts" -> all.filter { it.kind == "concept" }
            "Private" -> privateEntries
            else -> all
        }
        if (query.isBlank()) return categoryEntries
        val needle = query.lowercase()
        return categoryEntries.filter { entry ->
            sequenceOf(entry.name, entry.glyph, entry.meaning, entry.id, entry.origin)
                .any { it.lowercase().contains(needle) } ||
                database.search(query).any { it.id == entry.id }
        }
    }

    private fun renderSymbols() { symbolSearchRenderer?.invoke(search.text?.toString().orEmpty()) }
    private fun showSymbols(show: Boolean) {
        symbolPanel.visibility = if (show) View.VISIBLE else View.GONE
        keyboardPanel.visibility = if (show) View.GONE else View.VISIBLE
    }

    private fun launchStudio() {
        startActivity(Intent(this, OrchidSymbolManagerActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
    }

    private fun addKeyRow(value: String, weight: Float) {
        val row = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        value.forEach { key ->
            row.addView(keyButton(key.toString()) { commitKey(key.toString()) }, weightedParams(weight))
        }
        keyboardPanel.addView(row)
    }

    private fun addLetterRow(value: String, weight: Float, inset: Int = 0) {
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            if (inset > 0) setPadding(dp(inset), 0, dp(inset), 0)
        }
        value.forEach { letter ->
            val key = keyButton(labelFor(letter), letter.toString()) {
                commitKey(letter.toString())
                if (shift) { shift = false; updateLetterLabels() }
            }
            letterKeys.add(key to letter)
            row.addView(key, weightedParams(weight))
        }
        keyboardPanel.addView(row)
    }

    private fun updateLetterLabels() { letterKeys.forEach { (button, letter) -> button.text = labelFor(letter) } }
    private fun labelFor(letter: Char) = if (shift) letter.uppercaseChar().toString() else letter.toString()

    private fun commitKey(value: String) {
        currentInputConnection?.commitText(if (value.length == 1 && value[0].isLetter()) {
            if (shift) value.uppercase() else value.lowercase()
        } else value, 1)
        vibrateKey()
    }

    private fun sendEnter() {
        val action = currentInputEditorInfo?.imeOptions?.and(EditorInfo.IME_MASK_ACTION)
        if (action != null && action != EditorInfo.IME_ACTION_NONE && action != EditorInfo.IME_ACTION_UNSPECIFIED) {
            currentInputConnection?.performEditorAction(action)
        } else currentInputConnection?.commitText("\n", 1)
        vibrateKey()
    }

    private fun applyPreferences() {
        keyHeight = when (registry.setting(SymbolRegistry.KEY_HEIGHT, "standard")) {
            "compact" -> 42
            "tall" -> 54
            else -> 48
        }
        when (registry.setting(SymbolRegistry.KEY_THEME, "midnight")) {
            "light" -> { panelColor = Color.rgb(235, 237, 242); keyColor = Color.rgb(255, 255, 255); accentColor = Color.rgb(88, 75, 168) }
            "orchid" -> { panelColor = Color.rgb(31, 22, 42); keyColor = Color.rgb(64, 48, 78); accentColor = Color.rgb(199, 151, 226) }
            else -> { panelColor = Color.rgb(18, 20, 25); keyColor = Color.rgb(47, 50, 57); accentColor = Color.rgb(128, 111, 210) }
        }
    }

    private fun vibrateKey() {
        if (!registry.booleanSetting(SymbolRegistry.KEY_VIBRATION, false)) return
        val vibrator = getSystemService(VIBRATOR_SERVICE) as? Vibrator ?: return
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createOneShot(12, VibrationEffect.DEFAULT_AMPLITUDE))
        } else {
            vibrateLegacy(vibrator)
        }
    }

    @Suppress("DEPRECATION")
    private fun vibrateLegacy(vibrator: Vibrator) {
        vibrator.vibrate(12)
    }

    private fun categoryButton(label: String, action: () -> Unit) = Button(this).apply {
        text = label
        isAllCaps = false
        textSize = 11f
        minWidth = 0; minimumWidth = 0
        minHeight = dp(34); minimumHeight = dp(34)
        setPadding(dp(8), 0, dp(8), 0)
        setTextColor(Color.WHITE)
        background = rounded(if (selectedCategory == label) accentColor else Color.rgb(48, 50, 58), 18)
        setOnClickListener { action(); background = rounded(accentColor, 18) }
    }

    private fun toolButton(label: String, description: String, action: () -> Unit) =
        keyButton(label, description, action)

    private fun keyButton(label: String, description: String = label, action: () -> Unit): Button =
        Button(this).apply {
            text = label
            contentDescription = description
            isAllCaps = false
            textSize = if (label.length > 5) 10f else 16f
            minWidth = 0; minimumWidth = 0
            minHeight = dp(keyHeight); minimumHeight = dp(keyHeight)
            setPadding(dp(2), dp(1), dp(2), dp(1))
            setTextColor(if (registry.setting(SymbolRegistry.KEY_THEME, "midnight") == "light") Color.rgb(35, 36, 42) else Color.WHITE)
            background = rounded(if (label == "ORCHID") accentColor else keyColor, 8)
            setOnClickListener { action() }
        }

    private fun rounded(color: Int, radius: Int) = GradientDrawable().apply {
        setColor(color); cornerRadius = dp(radius).toFloat()
    }

    private fun weightedParams(weight: Float = 1f) =
        LinearLayout.LayoutParams(0, dp(keyHeight), weight).apply {
            setMargins(dp(2), dp(2), dp(2), dp(2))
        }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
}
