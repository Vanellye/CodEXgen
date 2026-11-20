package io.driveway.app

import android.app.Activity
import android.os.Bundle
import android.graphics.Color
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(28, 32, 28, 32)
            setBackgroundColor(Color.rgb(11, 18, 32))
        }
        fun label(text: String, size: Float, color: Int, bold: Boolean = false) =
            TextView(this).apply {
                this.text = text
                textSize = size
                setTextColor(color)
                if (bold) setTypeface(typeface, android.graphics.Typeface.BOLD)
                setPadding(0, 10, 0, 10)
            }
        root.addView(label("DRIVEWAY.IO", 14f, Color.rgb(167, 239, 192), true))
        root.addView(label("Build the ledger.\nDrive the workflow.", 32f, Color.WHITE, true))
        root.addView(label("Android starter · Kotlin", 16f, Color.LTGRAY))
        root.addView(label("Read-only demo. No wallet keys, transfers, withdrawals, or financial posting are enabled.", 14f, Color.LTGRAY))
        root.addView(label("Connectors and ledger sync are not configured yet.", 12f, Color.rgb(167, 239, 192)))
        setContentView(root)
    }
}
