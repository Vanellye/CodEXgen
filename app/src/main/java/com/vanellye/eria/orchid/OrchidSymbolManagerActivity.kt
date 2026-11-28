package com.vanellye.eria.orchid

import android.app.Activity
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.provider.Settings
import android.view.ViewGroup
import android.view.inputmethod.InputMethodManager
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast

/** ORCHID tools, keyboard preferences, and the persistent private-symbol studio. */
class OrchidSymbolManagerActivity : Activity() {
    private lateinit var api: OrchidKeyboardApi
    private lateinit var registry: SymbolRegistry
    private lateinit var listing: LinearLayout
    private lateinit var settingsPanel: LinearLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        api = OrchidKeyboardApi(this)
        registry = SymbolRegistry(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(18), dp(18), dp(18), dp(24))
            setBackgroundColor(Color.rgb(18, 20, 25))
        }
        root.addView(TextView(this).apply {
            text = "ORCHID tools"
            textSize = 26f
            setTextColor(Color.WHITE)
        })
        root.addView(TextView(this).apply {
            text = "Keyboard settings · symbol library · private studio"
            textSize = 13f
            setTextColor(Color.LTGRAY)
            setPadding(0, dp(4), 0, dp(16))
        })

        root.addView(sectionTitle("Keyboard setup"))
        root.addView(actionButton("Enable ORCHID keyboard") {
            startActivity(Intent(Settings.ACTION_INPUT_METHOD_SETTINGS))
        })
        root.addView(actionButton("Choose active keyboard") {
            (getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager).showInputMethodPicker()
        })
        root.addView(TextView(this).apply {
            text = "Samsung Keyboard remains installed and available. Use the Android keyboard picker to switch back at any time."
            textSize = 12f
            setTextColor(Color.LTGRAY)
            setPadding(dp(4), dp(8), dp(4), dp(14))
        })

        root.addView(sectionTitle("Keyboard appearance"))
        settingsPanel = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        settingsPanel.addView(optionLabel("Key size"))
        settingsPanel.addView(choiceRow(
            listOf("Compact" to "compact", "Standard" to "standard", "Tall" to "tall"),
            SymbolRegistry.KEY_HEIGHT,
            "standard"
        ))
        settingsPanel.addView(optionLabel("Color theme"))
        settingsPanel.addView(choiceRow(
            listOf("Midnight" to "midnight", "Orchid" to "orchid", "Light" to "light"),
            SymbolRegistry.KEY_THEME,
            "midnight"
        ))
        settingsPanel.addView(toggleOption("Key vibration", SymbolRegistry.KEY_VIBRATION, false))
        settingsPanel.addView(toggleOption("Number row", SymbolRegistry.KEY_NUMBER_ROW, true))
        root.addView(settingsPanel)

        root.addView(sectionTitle("Private symbol studio"))
        root.addView(TextView(this).apply {
            text = "Create personal glyphs that stay on this device until you explicitly export a private pack. Canonical records and their provenance are not edited."
            textSize = 12f
            setTextColor(Color.LTGRAY)
            setPadding(dp(4), 0, dp(4), dp(10))
        })
        val name = field("Symbol name")
        val glyph = field("Glyph or short sequence")
        val meaning = field("Meaning (optional)")
        root.addView(name); root.addView(glyph); root.addView(meaning)
        root.addView(actionButton("Save to private studio") {
            runCatching { api.addPrivateSymbol(name.text.toString(), glyph.text.toString(), meaning.text.toString()) }
                .onSuccess {
                    name.text.clear(); glyph.text.clear(); meaning.text.clear()
                    refresh()
                    Toast.makeText(this, "Saved privately on this device", Toast.LENGTH_SHORT).show()
                }
                .onFailure { Toast.makeText(this, it.message ?: "Could not save symbol", Toast.LENGTH_LONG).show() }
        })
        root.addView(actionButton("Export private symbol pack") {
            startActivity(Intent.createChooser(api.createShareIntent(), "Export ORCHID private symbols"))
        })
        root.addView(actionButton("Import private symbol pack") {
            val input = EditText(this).apply {
                hint = "Paste ORCHID_SYMBOL_PACK_V1 JSON"
                setTextColor(Color.WHITE)
                setHintTextColor(Color.LTGRAY)
                setPadding(dp(12), dp(10), dp(12), dp(10))
            }
            android.app.AlertDialog.Builder(this)
                .setTitle("Import private symbols").setView(input)
                .setPositiveButton("Import") { _, _ ->
                    runCatching { api.importPrivatePack(input.text.toString()) }
                        .onSuccess { Toast.makeText(this, "Imported $it symbols", Toast.LENGTH_LONG).show(); refresh() }
                        .onFailure { Toast.makeText(this, it.message ?: "Import failed", Toast.LENGTH_LONG).show() }
                }.setNegativeButton("Cancel", null).show()
        })
        root.addView(sectionTitle("Your private symbols"))
        listing = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        root.addView(listing, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        setContentView(ScrollView(this).apply { addView(root) })
        refresh()

        if (intent?.action == Intent.ACTION_SEND) {
            val payload = intent.getStringExtra(Intent.EXTRA_TEXT)
            if (!payload.isNullOrBlank()) runCatching { api.importPrivatePack(payload) }.onSuccess { refresh() }
        }
    }

    private fun choiceRow(options: List<Pair<String, String>>, key: String, default: String): LinearLayout {
        val row = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        options.forEach { (label, value) ->
            val selected = registry.setting(key, default) == value
            row.addView(Button(this).apply {
                text = label
                isAllCaps = false
                textSize = 11f
                setTextColor(Color.WHITE)
                background = rounded(if (selected) Color.rgb(112, 92, 180) else Color.rgb(48, 50, 58))
                setOnClickListener { registry.setSetting(key, value); recreate() }
            }, LinearLayout.LayoutParams(0, dp(44), 1f).apply { setMargins(dp(2), dp(3), dp(2), dp(8)) })
        }
        return row
    }

    private fun toggleOption(label: String, key: String, default: Boolean): Switch =
        Switch(this).apply {
            text = label
            textSize = 14f
            setTextColor(Color.WHITE)
            isChecked = registry.booleanSetting(key, default)
            setPadding(dp(4), dp(6), dp(4), dp(6))
            setOnCheckedChangeListener { _, checked -> registry.setBooleanSetting(key, checked) }
        }

    private fun field(hintText: String) = EditText(this).apply {
        hint = hintText
        setSingleLine(hintText != "Meaning (optional)")
        textSize = 14f
        setTextColor(Color.WHITE)
        setHintTextColor(Color.LTGRAY)
        setPadding(dp(12), dp(8), dp(12), dp(8))
        background = rounded(Color.rgb(39, 41, 48))
    }

    private fun sectionTitle(value: String) = TextView(this).apply {
        text = value
        textSize = 17f
        setTextColor(Color.rgb(213, 202, 255))
        setPadding(dp(2), dp(14), dp(2), dp(8))
    }

    private fun optionLabel(value: String) = TextView(this).apply {
        text = value
        textSize = 12f
        setTextColor(Color.LTGRAY)
        setPadding(dp(4), dp(8), dp(4), 0)
    }

    private fun actionButton(label: String, action: () -> Unit) = Button(this).apply {
        text = label
        isAllCaps = false
        textSize = 13f
        setTextColor(Color.WHITE)
        background = rounded(Color.rgb(48, 50, 58))
        setOnClickListener { action() }
    }

    private fun rounded(color: Int) = GradientDrawable().apply {
        setColor(color); cornerRadius = dp(10).toFloat()
    }

    private fun refresh() {
        listing.removeAllViews()
        val privateSymbols = api.symbols().filter { it.origin == "LOCAL_PRIVATE" || it.origin == "IMPORTED_PRIVATE" }
        if (privateSymbols.isEmpty()) {
            listing.addView(TextView(this).apply {
                text = "No private symbols yet."
                setTextColor(Color.LTGRAY)
                setPadding(dp(4), dp(8), dp(4), dp(8))
            })
        }
        privateSymbols.forEach { item ->
            listing.addView(TextView(this).apply {
                text = "${item.glyph}   ${item.name}\n${item.meaning}\n${item.origin} · ${item.id}"
                textSize = 13f
                setTextColor(Color.WHITE)
                setPadding(dp(8), dp(10), dp(8), dp(10))
                background = rounded(Color.rgb(35, 37, 44))
            }, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT).apply {
                setMargins(0, dp(3), 0, dp(3))
            })
        }
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
}
