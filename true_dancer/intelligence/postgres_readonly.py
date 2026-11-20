"""PostgreSQL read-only query adapter with fixed, reviewed query templates.

No DDL/DML, arbitrary SQL, provider writes, transfers, or financial execution exist here.
psycopg 3 is imported only when the adapter is instantiated without a test factory.
"""
from typing import Any, Callable, Mapping, Optional

from .avs import AvsValidator
from .contracts import EvidenceRecord, IntelligenceSnapshot, ReadGrant
from .pons import PonsAuthorizer


QUERY_TEMPLATES = {
    "shop_daily_sales": (
        "SELECT business_date, gross_sales, order_count "
        "FROM intelligence_shop_daily_sales WHERE business_date >= %s "
        "ORDER BY business_date LIMIT %s"
    ),
    "shop_inventory_summary": (
        "SELECT item_ref, quantity_on_hand, observed_at "
        "FROM intelligence_inventory_summary ORDER BY item_ref LIMIT %s"
    ),
}
QUERY_SCOPES = {
    "shop_daily_sales": "intelligence:shop_daily_sales:read",
    "shop_inventory_summary": "intelligence:shop_inventory_summary:read",
}


class ReadOnlyQueryDenied(PermissionError):
    pass


class PostgresReadOnlyStore:
    def __init__(self, dsn: str, pons: PonsAuthorizer, avs: AvsValidator,
                 connection_factory: Optional[Callable[..., Any]] = None):
        if not dsn:
            raise ValueError("PostgreSQL DSN must be supplied by the host environment")
        self._dsn, self._pons, self._avs = dsn, pons, avs
        if connection_factory is None:
            try:
                import psycopg
            except ImportError as exc:
                raise RuntimeError("install psycopg[binary] to use PostgreSQL adapter") from exc
            connection_factory = psycopg.connect
        self._connect = connection_factory

    def read(self, query_id: str, params: tuple[Any, ...], *, grant: ReadGrant,
             source_revision: str, now: int) -> IntelligenceSnapshot:
        template = QUERY_TEMPLATES.get(query_id)
        scope = QUERY_SCOPES.get(query_id)
        if template is None or scope is None:
            raise ReadOnlyQueryDenied("query_not_allowlisted")
        decision = self._pons.authorize(grant, scope=scope,
                                        source_revision=source_revision, now=now)
        if not decision.allowed:
            raise ReadOnlyQueryDenied(decision.reason)
        conn = self._connect(self._dsn)
        try:
            # The transaction-level read-only flag is set before any data query.
            conn.execute("SET TRANSACTION READ ONLY")
            cursor = conn.execute(template, params)
            rows = tuple(dict(row) for row in cursor.fetchall())
            captured = now
            import json, hashlib
            payload = json.dumps(rows, sort_keys=True, separators=(",", ":"), default=str).encode()
            evidence = EvidenceRecord(
                evidence_id=f"{query_id}:{now}", source="postgresql",
                source_revision=source_revision, captured_at=captured,
                payload_sha256=hashlib.sha256(payload).hexdigest(),
                provenance_ref=f"postgresql:{query_id}:{source_revision}:{now}",
                payload=payload,
            )
            result = self._avs.validate(evidence, expected_revision=source_revision, now=now)
            if not result.valid:
                raise ReadOnlyQueryDenied(f"avs_{result.status}")
            return IntelligenceSnapshot(query_id, source_revision, captured, rows, evidence)
        finally:
            try:
                conn.rollback()
            finally:
                conn.close()
