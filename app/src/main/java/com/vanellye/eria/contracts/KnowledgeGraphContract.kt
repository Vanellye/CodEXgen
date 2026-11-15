package com.vanellye.eria.contracts

/** Android projection of contracts/knowledge-graph.schema.json. Corrections append events. */
data class KnowledgeGraphDocument(val schemaVersion: String, val graphId: String, val events: List<KnowledgeGraphEvent>)
sealed interface KnowledgeGraphEvent {
    val eventId: String
    val sequence: Long
    val recordedAt: String
    val actor: String
}
data class GraphSource(val ref: String, val digest: String)
data class GraphNode(val id: String, val kind: String, val label: String, val createdAt: String, val source: GraphSource, val attributes: Map<String, String> = emptyMap())
data class GraphEdge(val id: String, val fromNodeId: String, val toNodeId: String, val relation: String, val createdAt: String, val source: GraphSource, val attributes: Map<String, String> = emptyMap())
data class NodeCreatedEvent(override val eventId: String, override val sequence: Long, override val recordedAt: String, override val actor: String, val node: GraphNode) : KnowledgeGraphEvent
data class EdgeCreatedEvent(override val eventId: String, override val sequence: Long, override val recordedAt: String, override val actor: String, val edge: GraphEdge) : KnowledgeGraphEvent
data class RecordSupersededEvent(override val eventId: String, override val sequence: Long, override val recordedAt: String, override val actor: String, val subjectId: String, val replacementId: String, val reason: String, val subjectType: String) : KnowledgeGraphEvent

object KnowledgeGraphContract {
    const val SCHEMA_VERSION = "1.0.0"
    private val identifier = Regex("^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
    private val sha256 = Regex("^[a-f0-9]{64}$")

    fun validate(document: KnowledgeGraphDocument): List<String> {
        val errors = mutableListOf<String>()
        if (document.schemaVersion != SCHEMA_VERSION) errors += "schemaVersion must equal $SCHEMA_VERSION"
        if (!identifier.matches(document.graphId)) errors += "graphId must be a stable identifier"
        val eventIds = mutableSetOf<String>()
        val nodeIds = mutableSetOf<String>()
        val edgeIds = mutableSetOf<String>()
        document.events.forEachIndexed { index, event ->
            if (!identifier.matches(event.eventId) || !eventIds.add(event.eventId)) errors += "events[$index].eventId must be unique and stable"
            if (event.sequence != index + 1L) errors += "events[$index].sequence must be contiguous and append ordered"
            if (!identifier.matches(event.actor)) errors += "events[$index].actor must be a stable identifier"
            if (!hasOffsetTimestamp(event.recordedAt)) errors += "events[$index].recordedAt must include timezone"
            when (event) {
                is NodeCreatedEvent -> {
                    val node = event.node
                    if (!identifier.matches(node.id) || !nodeIds.add(node.id)) errors += "node id must be unique and stable"
                    if (!identifier.matches(node.kind)) errors += "node kind must be a stable identifier"
                    if (node.label.isBlank() || node.label.length > 512) errors += "node label is invalid"
                    if (!hasOffsetTimestamp(node.createdAt)) errors += "node createdAt must include timezone"
                    validateSource(node.source, "events[$index].node", errors)
                }
                is EdgeCreatedEvent -> {
                    val edge = event.edge
                    if (!identifier.matches(edge.id) || !edgeIds.add(edge.id)) errors += "edge id must be unique and stable"
                    if (edge.fromNodeId !in nodeIds || edge.toNodeId !in nodeIds) errors += "edge endpoints must reference previously created nodes"
                    if (!identifier.matches(edge.relation)) errors += "edge relation must be a stable identifier"
                    if (!hasOffsetTimestamp(edge.createdAt)) errors += "edge createdAt must include timezone"
                    validateSource(edge.source, "events[$index].edge", errors)
                }
                is RecordSupersededEvent -> if (event.subjectId.isBlank() || event.replacementId.isBlank() || event.subjectId == event.replacementId || event.reason.isBlank()) {
                    errors += "supersession must identify distinct records and explain the correction"
                }
            }
        }
        return errors
    }

    private fun validateSource(source: GraphSource, path: String, errors: MutableList<String>) {
        if (source.ref.isBlank()) errors += "$path.source.ref is required"
        if (!sha256.matches(source.digest)) errors += "$path.source.digest must be lowercase SHA-256"
    }

    private fun hasOffsetTimestamp(value: String): Boolean =
        Regex("^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+-]\\d{2}:\\d{2})$").matches(value)
}
