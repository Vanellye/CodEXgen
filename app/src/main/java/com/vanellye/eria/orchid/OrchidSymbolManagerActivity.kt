package com.vanellye.eria.orchid

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.view.ViewGroup
import android.view.inputmethod.InputMethodManager
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.ScrollView
import android.widget.Toast

class OrchidSymbolManagerActivity : Activity() {
    private lateinit var api: OrchidKeyboardApi
    private lateinit var listing: LinearLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        api = OrchidKeyboardApi(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(20,20,20,20)
        }
        root.addView(TextView(this).apply { text = "ORCHID • PRIVATE SYMBOLS"; textSize = 20f })
        root.addView(Button(this).apply {
            text = "Enable ORCHID keyboard in Android settings"
            setOnClickListener {
                startActivity(Intent(Settings.ACTION_INPUT_METHOD_SETTINGS))
            }
        })
        root.addView(Button(this).apply {
            text = "Select ORCHID as current keyboard"
            setOnClickListener {
                (getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager).showInputMethodPicker()
            }
        })
        val name = EditText(this).apply { hint = "Symbol name" }
        val glyph = EditText(this).apply { hint = "Glyph or short sequence" }
        val meaning = EditText(this).apply { hint = "Meaning (optional)" }
        root.addView(name); root.addView(glyph); root.addView(meaning)
        root.addView(Button(this).apply {
            text = "Add to my private keyboard"
            setOnClickListener {
                runCatching { api.addPrivateSymbol(name.text.toString(),glyph.text.toString(),meaning.text.toString()) }
                    .onSuccess { name.text.clear(); glyph.text.clear(); meaning.text.clear(); refresh() }
                    .onFailure { Toast.makeText(this@OrchidSymbolManagerActivity,it.message,Toast.LENGTH_LONG).show() }
            }
        })
        root.addView(Button(this).apply {
            text = "Share private symbol pack"
            setOnClickListener { startActivity(Intent.createChooser(api.createShareIntent(),"Share ORCHID symbols")) }
        })
        root.addView(Button(this).apply {
            text = "Import symbol pack text"
            setOnClickListener {
                val input = EditText(this@OrchidSymbolManagerActivity).apply { hint = "Paste ORCHID_SYMBOL_PACK_V1 JSON" }
                android.app.AlertDialog.Builder(this@OrchidSymbolManagerActivity)
                    .setTitle("Import private symbols").setView(input)
                    .setPositiveButton("Import") { _, _ ->
                        runCatching { api.importPrivatePack(input.text.toString()) }
                            .onSuccess { Toast.makeText(this@OrchidSymbolManagerActivity,"Imported $it symbols",Toast.LENGTH_LONG).show(); refresh() }
                            .onFailure { Toast.makeText(this@OrchidSymbolManagerActivity,it.message,Toast.LENGTH_LONG).show() }
                    }.setNegativeButton("Cancel",null).show()
            }
        })
        root.addView(TextView(this).apply { text = "Available symbols"; textSize = 18f })
        listing = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        root.addView(listing,LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT))
        setContentView(ScrollView(this).apply { addView(root) })
        refresh()
        if (intent?.action == Intent.ACTION_SEND) {
            val payload = intent.getStringExtra(Intent.EXTRA_TEXT)
            if (!payload.isNullOrBlank()) runCatching { api.importPrivatePack(payload) }.onSuccess { refresh() }
        }
    }

    private fun refresh() {
        listing.removeAllViews()
        api.symbols().forEach { item ->
            listing.addView(TextView(this).apply {
                text = item.glyph + "   " + item.name + "   [" + item.origin + "]"
                textSize = 17f; setPadding(4,8,4,8)
            })
        }
    }
}
