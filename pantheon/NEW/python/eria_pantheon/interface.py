"""ctypes adapter for the existing Pantheon NEW and FaCADE C interfaces.

This module does not collect data, access the network, or write to the ERIA
database. Callers must supply minimized records and explicit authorization
assertions to the underlying C contracts.
"""
from __future__ import annotations

import ctypes
import os
from pathlib import Path
from typing import Any, Mapping, Optional


class PantheonError(RuntimeError):
    """Raised when the native Pantheon library rejects an operation."""


class _NewRecord(ctypes.Structure):
    _fields_ = [
        ("source_id", ctypes.c_char_p),
        ("record_id", ctypes.c_char_p),
        ("permission_basis", ctypes.c_char_p),
        ("purpose", ctypes.c_char_p),
        ("captured_at", ctypes.c_char_p),
        ("provenance_digest", ctypes.c_char_p),
        ("content_summary", ctypes.c_char_p),
        ("proof_reference", ctypes.c_char_p),
        ("proof_method", ctypes.c_char_p),
        ("proof_checked_at", ctypes.c_char_p),
        ("data_class", ctypes.c_int),
        ("evidence_status", ctypes.c_int),
        ("authorization_confirmed", ctypes.c_int),
    ]


class _FaCADECorrection(ctypes.Structure):
    _fields_ = [
        ("notice_id", ctypes.c_char_p),
        ("source_record_id", ctypes.c_char_p),
        ("target_record_id", ctypes.c_char_p),
        ("evidence_reference", ctypes.c_char_p),
        ("reason", ctypes.c_char_p),
        ("recorded_at", ctypes.c_char_p),
        ("reviewer_id", ctypes.c_char_p),
        ("relation", ctypes.c_int),
        ("source_authorized", ctypes.c_int),
        ("link_verified", ctypes.c_int),
    ]


_NEW_STATUS = {
    0: "OK",
    1: "INVALID",
    2: "NOT_AUTHORIZED",
    3: "UNSUPPORTED_DATA",
    4: "PROVENANCE_MISSING",
    5: "OUTPUT_TOO_SMALL",
    6: "PROOF_REFERENCE_MISSING",
}
_FACADE_STATUS = {
    0: "OK",
    1: "INVALID",
    2: "NOT_AUTHORIZED",
    3: "PROVENANCE_MISSING",
    4: "LINK_UNVERIFIED",
    5: "OUTPUT_TOO_SMALL",
}


def _text(value: Any, field: str, *, optional: bool = False) -> Optional[bytes]:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.encode("utf-8")


def _required(record: Mapping[str, Any], key: str) -> Any:
    if key not in record:
        raise ValueError(f"Missing required field: {key}")
    return record[key]


class ERIAPantheonInterface:
    """Loads the native library and exposes NEW/FaCADE operations.

    Library selection order:
      1. Explicit library_path argument
      2. ERIA_PANTHEON_LIBRARY environment variable
      3. ../build/liberia_pantheon.so relative to this package
    """

    def __init__(self, library_path: Optional[str] = None,
                 output_capacity: int = 8192) -> None:
        if output_capacity < 256:
            raise ValueError("output_capacity must be at least 256")
        package_root = Path(__file__).resolve().parents[2]
        candidate = (
            library_path
            or os.environ.get("ERIA_PANTHEON_LIBRARY")
            or str(package_root / "build" / "liberia_pantheon.so")
        )
        path = Path(candidate).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(
                f"Pantheon shared library not found: {path}. "
                "Build it with pantheon/NEW/python/test_bridge.sh or set "
                "ERIA_PANTHEON_LIBRARY."
            )

        self.library_path = str(path)
        self.output_capacity = output_capacity
        self._lib = ctypes.CDLL(self.library_path)

        self._lib.new_build_narrative.argtypes = [
            ctypes.POINTER(_NewRecord), ctypes.c_char_p, ctypes.c_size_t
        ]
        self._lib.new_build_narrative.restype = ctypes.c_int

        self._lib.facade_build_correction.argtypes = [
            ctypes.POINTER(_FaCADECorrection), ctypes.c_char_p,
            ctypes.c_size_t
        ]
        self._lib.facade_build_correction.restype = ctypes.c_int

    def build_narrative(self, record: Mapping[str, Any]) -> str:
        """Build an unreviewed, evidence-labeled narrative from a NEW record.

        data_class: 1=PUBLIC, 2=CONSENTED_AGGREGATE
        evidence_status: 1=SOURCE_REPORTED, 2=INDEPENDENTLY_CORROBORATED,
                         3=HYPOTHESIS
        """
        keepalive = [
            _text(_required(record, key), key)
            for key in (
                "source_id", "record_id", "permission_basis", "purpose",
                "captured_at", "provenance_digest", "content_summary"
            )
        ]
        proof_reference = _text(
            record.get("proof_reference"), "proof_reference", optional=True
        )
        proof_method = _text(
            record.get("proof_method"), "proof_method", optional=True
        )
        proof_checked_at = _text(
            record.get("proof_checked_at"), "proof_checked_at", optional=True
        )
        keepalive.extend([proof_reference, proof_method, proof_checked_at])

        data_class = int(_required(record, "data_class"))
        evidence_status = int(_required(record, "evidence_status"))
        authorized = bool(_required(record, "authorization_confirmed"))

        native = _NewRecord(
            *keepalive,
            data_class,
            evidence_status,
            1 if authorized else 0,
        )
        output = ctypes.create_string_buffer(self.output_capacity)
        status = self._lib.new_build_narrative(
            ctypes.byref(native), output, self.output_capacity
        )
        label = _NEW_STATUS.get(status, f"UNKNOWN_STATUS_{status}")
        if status != 0:
            raise PantheonError(f"Pantheon NEW rejected record: {label}")
        return output.value.decode("utf-8")

    def build_correction(self, correction: Mapping[str, Any]) -> str:
        """Build an additive FaCADE correction proposal; never edits records.

        relation: 1=RESTORES, 2=CORRECTS, 3=SUPERSEDES,
                  4=CONTRADICTS, 5=DERIVED_FROM
        """
        fields = [
            "notice_id", "source_record_id", "target_record_id",
            "evidence_reference", "reason", "recorded_at", "reviewer_id"
        ]
        encoded = [
            _text(_required(correction, key), key) for key in fields
        ]
        keepalive = list(encoded)
        native = _FaCADECorrection(
            *encoded,
            int(_required(correction, "relation")),
            1 if bool(_required(correction, "source_authorized")) else 0,
            1 if bool(_required(correction, "link_verified")) else 0,
        )
        output = ctypes.create_string_buffer(self.output_capacity)
        status = self._lib.facade_build_correction(
            ctypes.byref(native), output, self.output_capacity
        )
        label = _FACADE_STATUS.get(status, f"UNKNOWN_STATUS_{status}")
        if status != 0:
            raise PantheonError(f"Pantheon FaCADE rejected correction: {label}")
        return output.value.decode("utf-8")
