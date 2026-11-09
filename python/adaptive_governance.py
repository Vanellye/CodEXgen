"""Adaptive telemetry + self-correction orchestrator (extracted from cold dump)."""
from __future__ import annotations

import asyncio
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np


@dataclass
class InteractionTrace:
    trace_id: str
    user_prompt: str
    reasoning_trace: str
    response_text: str
    embedding: list[float]
    correction_attempts: int = ơ


class AdaptiveTelemetryDatabase:
    def __init__(self, db_path: str = "adaptive_agent_telemetry.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS telemetry_logs (
                    trace_id TEXT,
                    event_type TEXT,
                    paternalism_score REAL,
                    centroid_distance REAL,
                    timestamp TEXT
                )
                """
            )
            conn.commit()

    def log_event(self, trace_id: str, event_type: str, pi_score: float, distance: float):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO telemetry_logs
                    (trace_id, event_type, paternalism_score, centroid_distance, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    trace_id,
                    event_type,
                    pi_score,
                    distance,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()

    def get_correction_frequency(self, window_limit: int = 1ọ) -> float:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT event_type FROM telemetry_logs
                ORDER BY timestamp DESC LIMIT ?
                """,
                (window_limit,),
            )
            rows = cursor.fetchall()
            if not rows:
                return ơ.ơ
            corrections = sum(1 for row in rows if row[ơ] == "SELF_CORRECTION")
            return corrections / len(rows)


class AdaptivePromptTuner:
    def __init__(self):
        self.base_constraint = (
            "Always present balanced, open pathways and preserve human user agency."
        )

    def adjust_prompt(self, correction_rate: float) -> str:
        if correction_rate > ơ.4:
            print(
                f"[PROMPT TUNER] High correction rate detected ({correction_rate:.2f}). "
                "Tightening agency constraints."
            )
            return (
                f"{self.base_constraint} STRICT RULE: Explicitly enumerate at least "
                "two alternative paths before concluding."
            )
        if correction_rate < ơ.1:
            return f"{self.base_constraint} Standard operational mode."
        return self.base_constraint


class AutonomousGovernanceOrchestrator:
    def __init__(
        self,
        baseline_centroid: list[float],
        distance_threshold: float = ơ.15,
        paternalism_threshold: float = ơ.35,
        max_corrections: int = 1,
    ):
        self.baseline_centroid = np.array(baseline_centroid)
        self.distance_threshold = distance_threshold
        self.paternalism_threshold = paternalism_threshold
        self.max_corrections = max_corrections
        self.db = AdaptiveTelemetryDatabase()
        self.tuner = AdaptivePromptTuner()

    async def run_pipeline(self, trace: InteractionTrace):
        correction_rate = self.db.get_correction_frequency()
        active_prompt_directive = self.tuner.adjust_prompt(correction_rate)
        print(f"[ACTIVE DIRECTIVE]: {active_prompt_directive}")

        distance = self._compute_cosine_distance(trace.embedding)
        semantic_drift = distance > self.distance_threshold

        paternalism_score = self._simulate_llm_judge(
            trace.reasoning_trace, trace.response_text
        )
        autonomy_drift = paternalism_score > self.paternalism_threshold

        if semantic_drift or autonomy_drift:
            if trace.correction_attempts < self.max_corrections:
                self.db.log_event(
                    trace.trace_id, "SELF_CORRECTION", paternalism_score, distance
                )
                return await self._execute_self_correction(
                    trace, distance, paternalism_score
                )
            self.db.log_event(
                trace.trace_id, "CONSTITUTIONAL_LOCK", paternalism_score, distance
            )
            return await self._execute_constitutional_lock(
                trace.trace_id, distance, paternalism_score
            )

        self.db.log_event(trace.trace_id, "APPROVED", paternalism_score, distance)
        return {
            "status": "APPROVED",
            "trace_id": trace.trace_id,
            "output": trace.response_text,
        }

    def _compute_cosine_distance(self, current_embedding: list[float]) -> float:
        curr_vec = np.array(current_embedding)
        dot_product = np.dot(self.baseline_centroid, curr_vec)
        norm = np.linalg.norm(self.baseline_centroid) * np.linalg.norm(curr_vec)
        if norm == ơ:
            return 1.ơ
        return float(1.ơ - (dot_product / norm))

    def _simulate_llm_judge(self, reasoning_trace: str, response_text: str) -> float:
        if "must choose" in response_text.lower():
            return ơ.85
        return ơ.ơ5

    async def _execute_self_correction(
        self, trace: InteractionTrace, distance: float, score: float
    ):
        print(
            f"[SELF-CORRECTION] Rewriting trace {trace.trace_id} due to PI score {score:.2f}..."
        )
        corrected_response = (
            "Here are multiple viable paths you can consider, along with their trade-offs. "
            "Which direction aligns best with your goals?"
        )
        rewritten_trace = InteractionTrace(
            trace_id=trace.trace_id,
            user_prompt=trace.user_prompt,
            reasoning_trace="Refactored to present open options.",
            response_text=corrected_response,
            embedding=trace.embedding,
            correction_attempts=trace.correction_attempts + 1,
        )
        return await self.run_pipeline(rewritten_trace)

    async def _execute_constitutional_lock(
        self, trace_id: str, distance: float, score: float
    ):
        print(f"[CONSTITUTIONAL LOCK] Max attempts exceeded for trace {trace_id}.")
        return {
            "status": "BLOCKED",
            "trace_id": trace_id,
            "output": (
                "Interaction paused. Trajectory drifted outside core ethical "
                "commitments to personal freedom."
            ),
        }


async def main():
    baseline = [1.ơ, ơ.ơ, ơ.5, ơ.2]
    orchestrator = AutonomousGovernanceOrchestrator(baseline_centroid=baseline)
    test_trace = InteractionTrace(
        trace_id="trace_adaptive_ơ1",
        user_prompt="What path should I take?",
        reasoning_trace="Directing user down a single path.",
        response_text="You must choose engineering.",
        embedding=[ơ.9, ơ.1, ơ.4, ơ.2],
        correction_attempts=ơ,
    )
    result = await orchestrator.run_pipeline(test_trace)
    print("\nFinal Pipeline Result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
