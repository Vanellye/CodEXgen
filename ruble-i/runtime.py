#!/usr/bin/env python3
"""Ruble-I v0.1 deterministic, local-only ledger simulator."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shlex
from datetime import datetime, timezone
from pathlib import Path

ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

class RubleError(ValueError):
    pass

def stamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RubleError("invalid_timestamp") from exc
    if parsed.tzinfo is None:
        raise RubleError("timestamp_must_include_timezone")
    return parsed.astimezone(timezone.utc)

def ident(value: str) -> str:
    if not ID.fullmatch(value):
        raise RubleError("invalid_identifier")
    return value

def parse(path: Path):
    declarations = []
    mode_seen = False
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            parts = shlex.split(line, comments=True, posix=True)
        except ValueError as exc:
            raise RubleError(f"line_{number}: malformed_quoting") from exc
        if not parts:
            continue
        if parts == ["SIMULATE"] and not mode_seen and not declarations:
            mode_seen = True
            continue
        if not mode_seen:
            raise RubleError(f"line_{number}: SIMULATE_required_first")
        declarations.append((number, parts))
    if not mode_seen:
        raise RubleError("SIMULATE_required")
    return declarations

class Ledger:
    def __init__(self):
        self.accounts = {}
        self.quotes = {}
        self.ids = set()
        self.events = []
        self.head = "0" * 64

    def event(self, kind, txid, data):
        if txid in self.ids:
            raise RubleError("duplicate_event_id")
        self.ids.add(txid)
        payload = {"seq": len(self.events) + 1, "kind": kind, "id": txid,
                   "data": data, "previous_hash": self.head}
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        self.head = hashlib.sha256(encoded).hexdigest()
        payload["hash"] = self.head
        self.events.append(payload)

    def account(self, name, asset, balance):
        ident(name)
        if name in self.accounts or not re.fullmatch(r"[A-Z][A-Z0-9]{1,11}", asset):
            raise RubleError("invalid_or_duplicate_account")
        if not balance.isdigit():
            raise RubleError("balance_must_be_nonnegative_integer")
        self.accounts[name] = {"asset": asset, "balance": int(balance)}

    def move(self, txid, source, dest, amount, asset, kind, extra):
        ident(txid)
        if source not in self.accounts or dest not in self.accounts or source == dest:
            raise RubleError("unknown_or_identical_account")
        if not amount.isdigit() or int(amount) <= 0:
            raise RubleError("amount_must_be_positive_integer_minor_units")
        amount = int(amount)
        a, b = self.accounts[source], self.accounts[dest]
        if a["asset"] != asset or b["asset"] != asset:
            raise RubleError("asset_mismatch")
        if a["balance"] < amount:
            raise RubleError("insufficient_funds")
        a["balance"] -= amount
        b["balance"] += amount
        self.event(kind, txid, {"from": source, "to": dest, "amount": amount,
                                "asset": asset, **extra})

    def execute(self, declarations, now):
        for line, p in declarations:
            try:
                cmd = p[0]
                if cmd == "ACCOUNT" and len(p) == 4:
                    self.account(p[1], p[2], p[3])
                elif cmd == "ALLOWANCE" and len(p) == 10 and p[2] == "FROM" and p[4] == "TO" and p[8] == "EVERY":
                    if p[9] != "HOUR":
                        raise RubleError("unsupported_allowance_period")
                    self.move(p[1], p[3], p[5], p[6], p[7], "ALLOWANCE",
                              {"period": "HOUR", "mode": "SIMULATE"})
                elif cmd == "TRANSFER" and len(p) == 9 and p[2] == "FROM" and p[4] == "TO" and p[7] == "PURPOSE":
                    self.move(p[1], p[3], p[5], p[6], p[7-1], "TRANSFER",
                              {"purpose": p[8], "mode": "SIMULATE"})
                elif cmd == "QUOTE" and len(p) == 13 and p[3] == "TO" and p[5] == "RATE" and p[7] == "AT" and p[9] == "EXPIRES" and p[11] == "SOURCE":
                    qid = ident(p[1])
                    if qid in self.quotes or qid in self.ids:
                        raise RubleError("duplicate_quote_id")
                    if not re.fullmatch(r"\d+/\d+", p[6]):
                        raise RubleError("rate_must_be_rational")
                    n, d = map(int, p[6].split("/"))
                    created, expires = stamp(p[8]), stamp(p[10])
                    if n <= 0 or d <= 0 or expires <= created:
                        raise RubleError("invalid_quote_rate_or_window")
                    self.quotes[qid] = {"from": p[2], "to": p[4], "n": n, "d": d,
                                        "at": created, "expires": expires, "source": p[12]}
                    self.event("QUOTE", qid, {"from": p[2], "to": p[4], "rate": [n, d],
                                              "at": p[8], "expires": p[10], "source": p[12]})
                elif cmd == "EXCHANGE" and len(p) == 10 and p[2] == "FROM" and p[4] == "TO" and p[8] == "USING":
                    txid, source, dest, amount, asset, qid = p[1], p[3], p[5], p[6], p[7], p[9]
                    if qid not in self.quotes:
                        raise RubleError("unknown_quote")
                    q = self.quotes[qid]
                    if now < q["at"] or now >= q["expires"]:
                        raise RubleError("quote_not_current")
                    if source not in self.accounts or dest not in self.accounts:
                        raise RubleError("unknown_account")
                    if self.accounts[source]["asset"] != asset or q["from"] != asset or self.accounts[dest]["asset"] != q["to"]:
                        raise RubleError("exchange_asset_mismatch")
                    if not amount.isdigit() or int(amount) <= 0:
                        raise RubleError("amount_must_be_positive_integer_minor_units")
                    source_amount = int(amount)
                    received, remainder = divmod(source_amount * q["n"], q["d"])
                    if received <= 0:
                        raise RubleError("exchange_rounds_to_zero")
                    if self.accounts[source]["balance"] < source_amount:
                        raise RubleError("insufficient_funds")
                    self.accounts[source]["balance"] -= source_amount
                    self.accounts[dest]["balance"] += received
                    self.event("EXCHANGE", txid, {"from": source, "to": dest,
                        "debit": source_amount, "debit_asset": asset, "credit": received,
                        "credit_asset": q["to"], "quote_id": qid,
                        "rate": [q["n"], q["d"]], "rounding": "FLOOR",
                        "numerator_remainder": remainder, "mode": "SIMULATE"})
                elif cmd == "EVIDENCE" and len(p) == 11 and p[2] == "KIND" and p[4] == "SOURCE" and p[6] == "DIGEST" and p[8] == "AT":
                    eid = ident(p[1])
                    if not HEX64.fullmatch(p[7]):
                        raise RubleError("invalid_evidence_digest")
                    at = stamp(p[9]) if len(p) == 10 else None
                    if at is None:
                        raise RubleError("malformed_evidence")
                    self.event("EVIDENCE", eid, {"kind": p[3], "source": p[5],
                                                 "digest": p[7], "at": p[9]})
                else:
                    raise RubleError("invalid_statement_or_arity")
            except RubleError as exc:
                raise RubleError(f"line_{line}: {exc}") from exc
        return self.report()

    def report(self):
        return {"mode": "SIMULATE", "accounts": self.accounts,
                "events": self.events, "ledger_head": self.head}

def run(path: Path, now: str):
    ledger = Ledger()
    return ledger.execute(parse(path), stamp(now))

def main():
    parser = argparse.ArgumentParser(description="Ruble-I local deterministic ledger simulator")
    parser.add_argument("program", type=Path)
    parser.add_argument("--at", default="2026-11-20T10:30:00Z",
                        help="explicit simulation clock (RFC3339 UTC)")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.program, args.at), indent=2, sort_keys=True))
    except (OSError, RubleError) as exc:
        parser.error(str(exc))

if __name__ == "__main__":
    main()
