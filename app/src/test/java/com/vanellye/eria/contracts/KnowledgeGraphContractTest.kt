package com.vanellye.eria.contracts

import org.junit.Assert.assertTrue
import org.junit.Assert.assertFalse
import org.junit.Test
import org.json.JSONObject
import java.io.File

class KnowledgeGraphContractTest {
    private val source = GraphSource("repo:Vanellye/CodEXgen@main", "a".repeat(64))
    private fun document(events: List<KnowledgeGraphEvent>) = KnowledgeGraphDocument(KnowledgeGraphContract.SCHEMA_VERSION, "eria.main-knowledge", events)

    @Test fun acceptsAppendOnlyGraphAndStableNodeIdentity() {
        val node = GraphNode("node.origin", "concept", "Origin", "2026-11-15T12:00:00Z", source)
        val result = KnowledgeGraphContract.validate(document(listOf(NodeCreatedEvent("evt.1", 1, "2026-11-15T12:00:00Z", "human.operator", node))))
        assertTrue(result.toString(), result.isEmpty())
    }

    @Test fun rejectsDuplicateIdentityAndNonContiguousSequence() {
        val node = GraphNode("node.origin", "concept", "Origin", "2026-11-15T12:00:00Z", source)
        val result = KnowledgeGraphContract.validate(document(listOf(
            NodeCreatedEvent("evt.1", 1, "2026-11-15T12:00:00Z", "human.operator", node),
            NodeCreatedEvent("evt.2", 3, "2026-11-15T12:00:00Z", "human.operator", node)
        )))
        assertFalse(result.isEmpty())
        assertTrue(result.any { it.contains("unique") })
        assertTrue(result.any { it.contains("contiguous") })
    }

    @Test fun rejectsEdgesToUnknownNodesAndMissingProvenance() {
        val edge = GraphEdge("edge.1", "node.missing", "node.missing", "supports", "2026-11-15T12:00:00Z", GraphSource("source", "bad"))
        val result = KnowledgeGraphContract.validate(document(listOf(EdgeCreatedEvent("evt.1", 1, "2026-11-15T12:00:00Z", "human.operator", edge))))
        assertTrue(result.any { it.contains("previously created nodes") })
        assertTrue(result.any { it.contains("SHA-256") })
    }

    @Test fun modelsCorrectionsAsNewEventsWithoutChangingOriginalValues() {
        val original = GraphNode("node.old", "concept", "Original", "2026-11-15T12:00:00Z", source)
        val replacement = GraphNode("node.new", "concept", "Corrected", "2026-11-15T12:01:00Z", source)
        val events = listOf(
            NodeCreatedEvent("evt.1", 1, "2026-11-15T12:00:00Z", "human.operator", original),
            NodeCreatedEvent("evt.2", 2, "2026-11-15T12:01:00Z", "human.operator", replacement),
            RecordSupersededEvent("evt.3", 3, "2026-11-15T12:02:00Z", "human.operator", "node.old", "node.new", "Correction appended")
        )
        val result = KnowledgeGraphContract.validate(document(events))
        assertTrue(result.toString(), result.isEmpty())
        assertTrue(original.label == "Original")
    }

    @Test fun canonicalSharedFixtureValidatesOnAndroid() {
        val candidates = listOf(File("contracts/fixtures/knowledge-graph.valid.json"), File("../contracts/fixtures/knowledge-graph.valid.json"))
        val fixtureFile = candidates.firstOrNull { it.isFile }
        assertTrue("canonical shared fixture must be present", fixtureFile != null)
        val root = JSONObject(fixtureFile!!.readText())
        val eventsJson = root.getJSONArray("events")
        val events = (0 until eventsJson.length()).map { index ->
            val item = eventsJson.getJSONObject(index)
            val base = arrayOf(item.getString("eventId"), item.getLong("sequence"), item.getString("recordedAt"), item.getString("actor"))
            when (item.getString("type")) {
                "node.created" -> {
                    val n = item.getJSONObject("node")
                    val s = n.getJSONObject("source")
                    NodeCreatedEvent(base[0] as String, base[1] as Long, base[2] as String, base[3] as String,
                        GraphNode(n.getString("id"), n.getString("kind"), n.getString("label"), n.getString("createdAt"),
                            GraphSource(s.getString("ref"), s.getString("digest"))))
                }
                "edge.created" -> {
                    val e = item.getJSONObject("edge")
                    val s = e.getJSONObject("source")
                    EdgeCreatedEvent(base[0] as String, base[1] as Long, base[2] as String, base[3] as String,
                        GraphEdge(e.getString("id"), e.getString("fromNodeId"), e.getString("toNodeId"), e.getString("relation"),
                            e.getString("createdAt"), GraphSource(s.getString("ref"), s.getString("digest"))))
                }
                "node.superseded", "edge.superseded" -> RecordSupersededEvent(base[0] as String, base[1] as Long, base[2] as String, base[3] as String,
                    item.getString("subjectId"), item.getString("replacementId"), item.getString("reason"))
                else -> error("Unsupported fixture event type")
            }
        }
        val document = KnowledgeGraphDocument(root.getString("schemaVersion"), root.getString("graphId"), events)
        assertTrue(KnowledgeGraphContract.validate(document).toString(), KnowledgeGraphContract.validate(document).isEmpty())
    }

}
