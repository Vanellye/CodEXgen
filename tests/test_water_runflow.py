import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
from codexgen_contracts.envelope import validate_record
from water_runflow import WaterFlowStep, build_water_runflow


class WaterRunflowTests(unittest.TestCase):
    def step(self, record_id, stage, parent=None):
        return WaterFlowStep(
            record_id=record_id,
            stage=stage,
            parent_record_id=parent,
            source_ref="hypotheticals/water-runflow",
            observed_at="2026-11-13T12:00:00+00:00",
            volume_value=10.0,
            volume_unit="L",
            quality_observation="example observation only",
        )

    def test_full_runflow_is_parent_linked_and_non_authorizing(self):
        steps = (
            self.step("water-collect", "collection"),
            self.step("water-treat", "treatment", "water-collect"),
            self.step("water-store", "storage", "water-treat"),
            self.step("water-distribute", "distribution", "water-store"),
            self.step("water-reuse", "reuse", "water-distribute"),
        )
        records = build_water_runflow(steps)
        self.assertEqual(len(records), 5)
        for record in records:
            validate_record(record)
            self.assertEqual(record["quality"], "UNKNOWN")
            self.assertEqual(record["authorization"]["status"], "not_authorized")
            self.assertFalse(record["payload"]["physical_actuation_allowed"])
            self.assertFalse(record["payload"]["potability_determined"])

    def test_rejects_out_of_order_stages(self):
        with self.assertRaises(ValueError):
            build_water_runflow((
                self.step("water-store", "storage"),
                self.step("water-collect", "collection", "water-store"),
            ))

    def test_rejects_broken_parent_chain(self):
        with self.assertRaises(ValueError):
            build_water_runflow((
                self.step("water-collect", "collection"),
                self.step("water-treat", "treatment", "wrong-parent"),
            ))

    def test_allows_partial_runflow(self):
        records = build_water_runflow((self.step("water-collect", "collection"),))
        self.assertEqual(records[0]["payload"]["stage"], "collection")


if __name__ == "__main__":
    unittest.main()
