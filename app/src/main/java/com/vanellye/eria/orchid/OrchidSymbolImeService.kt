package com.vanellye.eria.orchid

import android.inputmethodservice.InputMethodService
import android.graphics.Color
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Path
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.text.Editable
import android.text.TextWatcher
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

/** Offline ORCHID keyboard. Keys commit text only after an explicit user tap. */
class OrchidSymbolImeService : InputMethodService() {
    private lateinit var registry: SymbolRegistry
    private lateinit var database: OrchidSymbolDatabase

    override fun onCreate() {
        super.onCreate()
        registry = SymbolRegistry(applicationContext)
        database = OrchidSymbolDatabase(applicationContext)
    }

    override fun onCreateInputView(): View {
        val scroll = ScrollView(this)
        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(8, 8, 8, 8)
            setBackgroundColor(Color.rgb(24, 27, 34))
        }

        column.addView(TextView(this).apply {
            text = "ORCHID  •  PRIVATE SYMBOL KEYBOARD"
            setTextColor(Color.WHITE)
            textSize = 14f
            setPadding(8, 8, 8, 12)
        })

        addSectionTitle(column, "TRYNITI / SOURCE")
        val trynitiKey = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(8, 8, 8, 8)
            background = GradientDrawable().apply {
                setColor(Color.rgb(39, 46, 59))
                cornerRadius = dp(14).toFloat()
                setStroke(dp(1), Color.rgb(145, 125, 220))
            }
            isClickable = true
            isFocusable = true
            contentDescription = "Insert TRYNITI source symbol"
            addView(TrynitiGlyphView(this@OrchidSymbolImeService), LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(112)
            ))
            addView(TextView(this@OrchidSymbolImeService).apply {
                text = "TRYNITI  •  3-ON-INFINITY"
                setTextColor(Color.WHITE)
                textSize = 12f
                typeface = Typeface.DEFAULT_BOLD
                gravity = Gravity.CENTER
            })
            setOnClickListener {
                currentInputConnection?.commitText("4♧", 1)
                announceForAccessibility("TRYNITI inserted")
            }
        }
        column.addView(trynitiKey, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(dp(3), dp(3), dp(3), dp(8)) })

        addSectionTitle(column, "KEYWORD / SYMBOL DATABASE")
        val databaseSearch = EditText(this).apply {
            hint = "Search meaning, keyword, or symbol name"
            singleLine = true
            textSize = 14f
            setTextColor(Color.WHITE)
            setHintTextColor(Color.LTGRAY)
            setPadding(dp(12), dp(8), dp(12), dp(8))
        }
        column.addView(databaseSearch, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ))
        val databaseResults = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
        }
        column.addView(databaseResults, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ))

        fun showDatabaseResults(query: String) {
            databaseResults.removeAllViews()
            val matches = if (query.isBlank()) {
                database.all().filter { it.kind in setOf("living-symbol", "operator", "concept") }
            } else {
                database.search(query)
            }.take(12)
            if (matches.isEmpty()) {
                databaseResults.addView(TextView(this).apply {
                    text = "No matching ORCHID records"
                    setTextColor(Color.LTGRAY)
                    setPadding(dp(8), dp(8), dp(8), dp(8))
                })
                return
            }
            matches.chunked(3).forEach { group ->
                val resultRow = keyRow()
                group.forEach { record ->
                    resultRow.addView(Button(this).apply {
                        text = record.glyph + "\n" + record.name
                        isAllCaps = false
                        textSize = 13f
                        contentDescription = "Insert ${record.name}: ${record.meaning}"
                        setOnClickListener {
                            currentInputConnection?.commitText(database.insertText(record.id), 1)
                            announceForAccessibility("${record.name} inserted")
                        }
                    }, weightedKeyParams())
                }
                databaseResults.addView(resultRow)
            }
        }
        showDatabaseResults("")
        databaseSearch.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) = Unit
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                showDatabaseResults(s?.toString().orEmpty())
            }
            override fun afterTextChanged(s: Editable?) = Unit
        })

        addSectionTitle(column, "CHRONOGLYPH")
        registry.all().chunked(3).forEach { group ->
            val row = keyRow()
            group.forEach { item ->
                val key = Button(this).apply {
                    text = item.glyph + "\n" + item.name
                    isAllCaps = false
                    textSize = 16f
                    setOnClickListener { currentInputConnection?.commitText(item.glyph, 1) }
                    layoutParams = weightedKeyParams()
                }
                row.addView(key)
            }
            column.addView(row)
        }

        addSectionTitle(column, "WORD KEYS  •  DEPTH / MOTION / FORM")
        registry.wordKeys().chunked(3).forEach { group ->
            val row = keyRow()
            group.forEach { item ->
                row.addView(createDimensionalWordKey(item), weightedKeyParams())
            }
            column.addView(row)
        }

        val controls = keyRow()
        controls.addView(Button(this).apply {
            text = "Space"
            setOnClickListener { currentInputConnection?.commitText(" ", 1) }
            layoutParams = weightedKeyParams()
        })
        controls.addView(Button(this).apply {
            text = "⌫"
            setOnClickListener { currentInputConnection?.deleteSurroundingTextInCodePoints(1, 0) }
            layoutParams = weightedKeyParams()
        })
        column.addView(controls)

        scroll.addView(column)
        return scroll
    }

    private fun addSectionTitle(parent: LinearLayout, title: String) {
        parent.addView(TextView(this).apply {
            text = title
            setTextColor(Color.rgb(190, 205, 230))
            textSize = 12f
            typeface = Typeface.DEFAULT_BOLD
            setPadding(8, 14, 8, 6)
        })
    }

    private fun keyRow() = LinearLayout(this).apply {
        orientation = LinearLayout.HORIZONTAL
        gravity = Gravity.CENTER
    }

    private fun weightedKeyParams() =
        LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f).apply {
            setMargins(3, 3, 3, 3)
        }

    /**
     * A four-plane, 4D-inspired emoji silhouette: three offset depth echoes,
     * a crisp foreground form, and a small temporal orbit cue. It is a visual
     * metaphor rendered with native text, not a literal 4D projection.
     */
    private fun createDimensionalWordKey(item: OrchidWordKey): View {
        val key = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(3, 5, 3, 6)
            background = GradientDrawable().apply {
                setColor(Color.rgb(39, 46, 59))
                cornerRadius = dp(12).toFloat()
                setStroke(dp(1), Color.rgb(75, 91, 116))
            }
            isClickable = true
            isFocusable = true
            elevation = dp(3).toFloat()
        }

        val silhouette = FrameLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(54)
            )
        }
        val echoes = listOf(
            Triple(0.16f, dp(-4), dp(3)),
            Triple(0.25f, dp(3), dp(-2)),
            Triple(0.34f, dp(5), dp(3))
        )
        echoes.forEach { (alpha, x, y) ->
            silhouette.addView(TextView(this).apply {
                text = item.silhouette
                textSize = 29f
                this.alpha = alpha
                gravity = Gravity.CENTER
                translationX = x.toFloat()
                translationY = y.toFloat()
                layoutParams = FrameLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.MATCH_PARENT
                )
            })
        }
        silhouette.addView(TextView(this).apply {
            text = item.silhouette
            textSize = 31f
            gravity = Gravity.CENTER
            setShadowLayer(dp(5).toFloat(), dp(1).toFloat(), dp(2).toFloat(), Color.BLACK)
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        })
        silhouette.addView(TextView(this).apply {
            text = "↻"
            textSize = 12f
            setTextColor(Color.rgb(153, 190, 230))
            gravity = Gravity.TOP or Gravity.END
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            ).apply { setMargins(0, dp(1), dp(5), 0) }
        })
        key.addView(silhouette)

        key.addView(TextView(this).apply {
            text = item.name
            textSize = 11f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            maxLines = 1
        })
        key.addView(TextView(this).apply {
            text = item.glyph
            textSize = 13f
            setTextColor(Color.rgb(190, 205, 230))
            gravity = Gravity.CENTER
            maxLines = 1
        })

        key.setOnClickListener {
            // Insert the readable word and its ORCHID expression as one user action.
            currentInputConnection?.commitText(item.name + " " + item.glyph, 1)
            key.animate().scaleX(0.96f).scaleY(0.96f).setDuration(65)
                .withEndAction { key.animate().scaleX(1f).scaleY(1f).setDuration(90).start() }
                .start()
        }
        return key
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
}


/** Native 2D TRYNITI mark: three braided upper strands over a horizontal infinity. */
private class TrynitiGlyphView(context: android.content.Context) : View(context) {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 4.2f * resources.displayMetrics.density
        strokeCap = Paint.Cap.ROUND
        strokeJoin = Paint.Join.ROUND
        color = Color.rgb(221, 211, 255)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val sx = width / 240f
        val sy = height / 220f
        val scale = minOf(sx, sy)
        val save = canvas.save()
        canvas.translate((width - 240f * scale) / 2f, (height - 220f * scale) / 2f)
        canvas.scale(scale, scale)

        val upper = listOf(
            Path().apply {
                moveTo(120f, 12f)
                cubicTo(42f, 12f, 64f, 67f, 120f, 91f)
                cubicTo(176f, 115f, 198f, 145f, 120f, 174f)
            },
            Path().apply {
                moveTo(120f, 12f)
                cubicTo(198f, 12f, 176f, 67f, 120f, 91f)
                cubicTo(64f, 115f, 42f, 145f, 120f, 174f)
            },
            Path().apply {
                moveTo(120f, 12f)
                cubicTo(91f, 39f, 91f, 67f, 120f, 91f)
                cubicTo(149f, 115f, 149f, 146f, 120f, 174f)
            }
        )
        upper.forEach { canvas.drawPath(it, paint) }

        val infinity = Path().apply {
            moveTo(120f, 174f)
            cubicTo(91f, 128f, 12f, 132f, 12f, 174f)
            cubicTo(12f, 216f, 83f, 216f, 120f, 174f)
            cubicTo(157f, 132f, 228f, 132f, 228f, 174f)
            cubicTo(228f, 216f, 149f, 216f, 120f, 174f)
        }
        canvas.drawPath(infinity, paint)

        paint.style = Paint.Style.FILL
        canvas.drawCircle(120f, 12f, 7f, paint)
        canvas.drawCircle(12f, 174f, 6f, paint)
        canvas.drawCircle(228f, 174f, 6f, paint)
        paint.style = Paint.Style.STROKE
        canvas.drawCircle(120f, 174f, 16f, paint)
        canvas.drawLine(120f, 165f, 120f, 183f, paint)
        canvas.drawLine(111f, 174f, 129f, 174f, paint)

        canvas.restoreToCount(save)
    }
}
