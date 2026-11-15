package com.vanellye.eria

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.Button
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Slider
import androidx.compose.material.Surface
import androidx.compose.material.Switch
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

private data class KnowledgeNode(
    val label: String,
    val orbit: Float,
    val phase: Float,
    val inclination: Float,
    val mass: Float
)

private data class Point4(val x: Float, val y: Float, val z: Float, val w: Float)

private val wellNodes = listOf(
    KnowledgeNode("ERIA Core", 0.24f, 0.2f, 0.1f, 2.4f),
    KnowledgeNode("Physics", 0.38f, 1.1f, 0.6f, 1.5f),
    KnowledgeNode("Geometry", 0.49f, 2.0f, -0.4f, 1.2f),
    KnowledgeNode("Robotics", 0.61f, 2.8f, 0.9f, 1.1f),
    KnowledgeNode("Telemetry", 0.73f, 3.7f, -0.7f, 0.9f),
    KnowledgeNode("Research", 0.84f, 4.6f, 0.3f, 0.8f),
    KnowledgeNode("Governance", 0.94f, 5.4f, -0.2f, 0.7f)
)

/** 3 projected spatial axes plus an evolving fourth knowledge/time coordinate. */
@Composable
fun KnowledgeWellScreen() {
    var running by remember { mutableStateOf(true) }
    var gravityEnabled by remember { mutableStateOf(true) }
    var gravityStrength by remember { mutableStateOf(0.72f) }
    var phase by remember { mutableStateOf(0f) }
    var rotationXW by remember { mutableStateOf(0.35f) }
    var rotationYW by remember { mutableStateOf(-0.25f) }

    LaunchedEffect(running) {
        while (running) {
            delay(16)
            phase += 0.016f
        }
    }

    Surface(modifier = Modifier.fillMaxSize(), color = Color(0xFF070A18)) {
        Column(
            modifier = Modifier.fillMaxSize().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text("ERIA · KNOWLEDGE WELL", color = Color(0xFFE9E8FF), style = MaterialTheme.typography.h6)
            Text("A living map of connected knowledge", color = Color(0xFF9CA6D8), fontSize = 13.sp)

            Canvas(
                modifier = Modifier.fillMaxWidth().weight(1f)
                    .clip(RoundedCornerShape(24.dp))
                    .background(Color(0xFF0B1026))
                    .pointerInput(Unit) {
                        detectDragGestures { change, drag ->
                            change.consume()
                            rotationXW += drag.y * 0.006f
                            rotationYW += drag.x * 0.006f
                        }
                    }
            ) {
                val center = Offset(size.width / 2f, size.height / 2f)
                val scale = size.minDimension * 0.39f
                val mass = if (gravityEnabled) gravityStrength * 2.8f else 0f

                for (i in 1..10) {
                    val base = i / 10f
                    val radius = scale * (base * (1f + mass * 0.10f))
                    drawCircle(
                        color = Color(0xFF6958C8).copy(alpha = 0.025f + (1f - base) * 0.025f),
                        radius = radius,
                        center = center,
                        style = Stroke(width = 1.dp.toPx())
                    )
                }

                val vertices = (-1..1 step 2).flatMap { x ->
                    (-1..1 step 2).flatMap { y ->
                        (-1..1 step 2).flatMap { z ->
                            (-1..1 step 2).map { w -> Point4(x.toFloat(), y.toFloat(), z.toFloat(), w.toFloat()) }
                        }
                    }
                }

                fun project(p: Point4): Offset {
                    val c1 = cos(rotationXW + phase * 0.12f)
                    val s1 = sin(rotationXW + phase * 0.12f)
                    val c2 = cos(rotationYW + phase * 0.09f)
                    val s2 = sin(rotationYW + phase * 0.09f)
                    val x1 = p.x * c1 - p.w * s1
                    val w1 = p.x * s1 + p.w * c1
                    val y1 = p.y * c2 - w1 * s2
                    val w2 = p.y * s2 + w1 * c2
                    val perspective4 = 2.8f / (2.8f - w2 * 0.32f)
                    val zPerspective = 2.4f / (2.4f - p.z * 0.18f)
                    return Offset(
                        center.x + x1 * perspective4 * zPerspective * scale,
                        center.y + y1 * perspective4 * zPerspective * scale
                    )
                }

                vertices.forEachIndexed { i, a ->
                    for (j in i + 1 until vertices.size) {
                        val b = vertices[j]
                        val differences = listOf(a.x != b.x, a.y != b.y, a.z != b.z, a.w != b.w).count { it }
                        if (differences == 1) {
                            drawLine(Color(0xFF7B77D8).copy(alpha = 0.24f), project(a), project(b), 1.1.dp.toPx())
                        }
                    }
                }

                drawCircle(Color(0xFF8B5CF6).copy(alpha = 0.12f), scale * 0.16f, center)
                drawCircle(Color(0xFFB9A5FF), scale * 0.035f, center)
                drawCircle(Color(0xFFE7DEFF).copy(alpha = 0.7f), scale * 0.012f, center)

                val points = wellNodes.mapIndexed { index, node ->
                    val orbitalSpeed = sqrt((mass + 0.08f) / (node.orbit * node.orbit * node.orbit + 0.08f))
                    val angle = node.phase + phase * orbitalSpeed * 0.16f
                    val x = node.orbit * cos(angle)
                    val y = node.orbit * sin(angle) * cos(node.inclination)
                    val z = node.orbit * sin(angle) * sin(node.inclination)
                    val w = sin(angle * 0.5f + index) * 0.45f
                    project(Point4(x * 2f, y * 2f, z * 2f, w)) to node
                }

                points.forEachIndexed { i, (p, node) ->
                    points.drop(i + 1).forEach { (q, _) ->
                        val dx = p.x - q.x
                        val dy = p.y - q.y
                        val d = sqrt(dx * dx + dy * dy)
                        if (d < scale * 0.72f) {
                            drawLine(
                                Color(0xFF51C7D8).copy(alpha = (0.22f * (1f - d / (scale * 0.9f))).coerceIn(0.025f, 0.22f)),
                                p, q, 1.dp.toPx()
                            )
                        }
                    }
                    val glow = (node.mass * 2.1f).coerceIn(2f, 7f)
                    drawCircle(Color(0xFF4DD9E8).copy(alpha = 0.13f), glow * 3.2f, p)
                    drawCircle(Color(0xFFB6F5FF), glow, p)
                }
            }

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Gravity field", color = Color(0xFFE3E2FF))
                Switch(checked = gravityEnabled, onCheckedChange = { gravityEnabled = it })
            }
            Text("Gravity strength · ${(gravityStrength * 100).toInt()}%", color = Color(0xFFB8BCE0), fontSize = 12.sp)
            Slider(value = gravityStrength, onValueChange = { gravityStrength = it }, enabled = gravityEnabled)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { running = !running }) { Text(if (running) "Pause time" else "Resume time") }
                Button(onClick = {
                    phase = 0f
                    rotationXW = 0.35f
                    rotationYW = -0.25f
                }) { Text("Reset view") }
            }
            Text("DRAG TO ROTATE · 4D PROJECTION: X/Y/Z + W (evolving knowledge-time)", color = Color(0xFF828CB9), fontSize = 10.sp)
            Text("Newtonian-inspired gravity visualization · not a literal 4D spacetime solver", color = Color(0xFF697398), fontSize = 10.sp)
        }
    }
}
