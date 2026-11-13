import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
from water_equipment import WaterEquipment, build_equipment_inventory


class WaterEquipmentTests(unittest.TestCase):
    def test_reported_connections_never_enable_control_or_potability(self):
        inventory = build_equipment_inventory((
            WaterEquipment("pump-1", "pump", "inventory/source", "reported_connected"),
            WaterEquipment("sensor-1", "sensor", "inventory/source", "reported_connected"),
            WaterEquipment("valve-1", "valve", "inventory/source", "unknown"),
            WaterEquipment("filter-1", "treatment", "inventory/source", "not_connected"),
        ))
        self.assertEqual(len(inventory), 4)
        for item in inventory:
            self.assertTrue(item["observation_only"])
            self.assertFalse(item["control_enabled"])
            self.assertFalse(item["potability_claim_allowed"])
            self.assertFalse(item["external_io_performed"])

    def test_rejects_duplicate_equipment_ids(self):
        item = WaterEquipment("pump-1", "pump", "inventory/source")
        with self.assertRaises(ValueError):
            build_equipment_inventory((item, item))

    def test_rejects_unknown_equipment_kind(self):
        with self.assertRaises(ValueError):
            WaterEquipment("device-1", "robot", "inventory/source").to_record()


if __name__ == "__main__":
    unittest.main()
