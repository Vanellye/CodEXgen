#!/usr/bin/env python3
"""Deterministic fixture checks for the bundled ORCHID symbol database."""
import json
import pathlib
import sys

DATABASE = pathlib.Path("app/src/main/assets/orchid/orchid-symbol-database.v1.json")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    data = json.loads(DATABASE.read_text(encoding="utf-8"))
    require(data.get("format") == "ORCHID_SYMBOL_DATABASE", "database format mismatch")
    require(str(data.get("schemaVersion", "")).startswith("1."), "unsupported schema version")

    records = data.get("records")
    keywords = data.get("keywordRecords")
    require(isinstance(records, list) and isinstance(keywords, list), "record collections missing")
    all_records = records + keywords
    ids = [record.get("id") for record in all_records]
    require(all(isinstance(value, str) and value.strip() for value in ids), "record ID missing")
    require(len(ids) == len(set(ids)), "duplicate record IDs across collections")

    for record in all_records:
        require(isinstance(record.get("glyph"), str) and record["glyph"], f"empty glyph: {record.get('id')}")
        require(isinstance(record.get("name"), str) and record["name"].strip(), f"empty name: {record.get('id')}")
        require(isinstance(record.get("kind"), str) and record["kind"].strip(), f"empty kind: {record.get('id')}")

    profiles = data.get("encodingProfiles")
    require(isinstance(profiles, list) and profiles, "encoding profiles missing")
    n8 = next((profile for profile in profiles if profile.get("id") == "N8-A1-A8-V1"), None)
    require(n8 is not None, "N8-A1-A8-V1 profile missing")
    require(n8.get("unitWidth") == 8 and n8.get("unitCount") == 8, "N8 dimensions changed")
    require(n8.get("totalBits") == 64, "N8 total bit width must remain 64")

    payload = n8.get("bytes")
    expected = ["10100001", "10100010", "10100011", "10100100",
                "10100101", "10100110", "10100111", "10101000"]
    require(isinstance(payload, list) and len(payload) == 8, "N8 must contain exactly eight bytes")
    actual = [item.get("bits") for item in payload]
    require(actual == expected, "N8 bytes/order/leading zeros changed")
    require(all(isinstance(bits, str) and len(bits) == 8 and set(bits) <= {"0", "1"} for bits in actual),
            "N8 contains a non-binary or non-eight-bit value")
    zeros = sum(bits.count("0") for bits in actual)
    ones = sum(bits.count("1") for bits in actual)
    counts = n8.get("counts", {})
    require((zeros, ones) == (35, 29), "N8 bit population changed")
    require(counts.get("zero") == zeros and counts.get("one") == ones and counts.get("total") == 64,
            "N8 declared bit counts do not match payload")

    everweave = next((r for r in all_records if r.get("id") == "ORC-EVERWEAVE-001"), None)
    require(everweave is not None, "EVERWEAVE record missing")
    require(everweave.get("glyph") == "⟲⋈⟲⋈⟲⤻", "EVERWEAVE glyph changed")
    layer_ids = {
        "ORC-LAYER-CORE-001", "ORC-LAYER-CORE-002", "ORC-LAYER-CORE-003",
        "ORC-LAYER-STAR-001", "ORC-LAYER-STAR-002", "ORC-LAYER-TIME-001",
        "ORC-LAYER-TIME-007", "ORC-LAYER-TIME-008", "ORC-LAYER-TIME-009",
    }
    layer_records = {record["id"]: record for record in all_records}
    require(layer_ids.issubset(layer_records), "Core, star, or clock-time fixture records missing")
    require(all(layer_records[item].get("origin") == "ORCHID_LAYER_FIXTURE_V1" for item in layer_ids),
            "Layer fixture provenance missing or changed")
    require(sum(record.get("kind") == "core-layer" for record in all_records) >= 12,
            "Far-left Core layer is not populated")
    require(sum(record.get("kind") == "favorite-layer" for record in all_records) >= 8,
            "Star/Favorites layer is not populated")
    require(sum(record.get("kind") == "time-layer" for record in all_records) >= 12,
            "Clock/Time layer is not populated")

    print(f"ORCHID fixture PASS: {len(records)} records + {len(keywords)} keywords; "
          f"N8=64 bits (35 zero, 29 one); IDs unique; glyphs present; Core/Star/Time layers populated.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"ORCHID fixture FAIL: {error}", file=sys.stderr)
        sys.exit(1)
