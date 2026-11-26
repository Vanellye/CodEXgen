package com.vanellye.eria.orchid

import android.inputmethodservice.InputMethodService
import android.graphics.Color
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

/** Offline symbol keyboard. Text is inserted only after an explicit key tap. */
class OrchidSymbolImeService : InputMethodService() {
    private lateinit var registry: SymbolRegistry
    override fun onCreate() { super.onCreate(); registry = SymbolRegistry(applicationContext) }

    override fun onCreateInputView(): View {
        val scroll = ScrollView(this)
        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(8,8,8,8)
            setBackgroundColor(Color.rgb(24,27,34))
        }
        column.addView(TextView(this).apply {
            text = "ORCHID  •  PRIVATE SYMBOL KEYBOARD"
            setTextColor(Color.WHITE); textSize = 14f; setPadding(8,8,8,12)
        })
        registry.all().chunked(3).forEach { group ->
            val row = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
            group.forEach { item ->
                row.addView(Button(this).apply {
                    text = item.glyph + "\n" + item.name
                    isAllCaps = false; textSize = 16f
                    setOnClickListener { currentInputConnection?.commitText(item.glyph,1) }
                    layoutParams = LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1f)
                })
            }
            column.addView(row)
        }
        column.addView(Button(this).apply { text = "Space"; setOnClickListener { currentInputConnection?.commitText(" ",1) } })
        column.addView(Button(this).apply { text = "⌫"; setOnClickListener { currentInputConnection?.deleteSurroundingTextInCodePoints(1,0) } })
        scroll.addView(column)
        return scroll
    }
}
