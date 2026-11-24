"""Birth-cursive derivation for nested UI text.

The source value is never mutated. Only allowlisted presentation fields are
eligible for exact, reviewed phrase rules. Unknown text remains unchanged and
is marked for review rather than being rewritten by guesswork.

Traversal is iterative: nested objects are processed with an explicit stack.
Co-signation metadata links the origin and derivative; references are not
cryptographic signatures and must be verified by a trusted host.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple


TEXT_FIELDS = frozenset({
    "text", "content", "label", "title", "description", "message", "tooltip",
    "placeholder", "accessibility_label", "accessibilityLabel",
    "aria_label", "ariaLabel", "alt", "notification", "dialog_text",
    "button_text", "helper_text", "caption", "summary",
})

NEVER_TRANSFORM_FIELDS = frozenset({
    "code", "command", "route", "url", "uri", "id", "key", "status",
    "error_code", "errorCode", "security_warning", "securityWarning",
    "warning_code", "warningCode", "shortcut", "hotkey", "escape_sequence",
})


@dataclass(frozen=True)
class OppositionRule:
    rule_id: str
    origin_phrase: str
    meaning: str
    possibility: str
    blessing: str


DEFAULT_RULES: Tuple[OppositionRule, ...] = (
    OppositionRule("oppositio.failure.v1", "May you fail",
                   "A wish for an unsuccessful outcome",
                   "Learning, adaptation, and achievement remain possible",
                   "May your efforts open paths to learning, growth, and success."),
    OppositionRule("oppositio.suffering.v1", "May you suffer",
                   "A wish for another person's suffering",
                   "Relief, care, peace, and healing are constructive possibilities",
                   "May you find relief, peace, care, and healing."),
    OppositionRule("oppositio.worth.v1", "You are worthless",
                   "A statement denying a person's worth",
                   "Human dignity and belonging can be affirmed",
                   "Your life has inherent worth and dignity."),
    OppositionRule("oppositio.trapped.v1", "You are trapped",
                   "A statement that presents a person as having no way forward",
                   "Safe choices and paths toward freedom may be discovered",
                   "May you discover a safe path toward freedom."),
    OppositionRule("oppositio.darkness.v1", "Darkness surrounds you",
                   "A statement expressing obscurity or disorientation",
                   "Clarity, understanding, and guidance are possible",
                   "May clarity and understanding illuminate your path."),
)


class CursiveCycleError(ValueError):
    """Raised when a nested UI structure contains a reference cycle."""


class CursiveDepthError(ValueError):
    """Raised when a nested UI structure exceeds the configured depth."""


@dataclass(frozen=True)
class BirthCursiveRecord:
    schema: str
    field_path: str
    origin_text: str
    origin_sha256: str
    meaning: Optional[str]
    possibility: Optional[str]
    derived_text: str
    derived_sha256: str
    rule_id: Optional[str]
    status: str
    co_signers: Tuple[str, ...]
    co_signature_ref: Optional[str]
    co_signature_status: str
    signature_verification: str = "NOT_PERFORMED_BY_THIS_MODULE"

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["co_signers"] = list(self.co_signers)
        return result


def _digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _match_key(text: str) -> str:
    return " ".join(text.strip().casefold().rstrip(" .!?").split())


class BirthCursiveEngine:
    """Derive constructive UI text while retaining exact origin and lineage."""

    def __init__(
        self,
        rules: Sequence[OppositionRule] = DEFAULT_RULES,
        max_depth: int = 32,
    ) -> None:
        if max_depth < 1:
            raise ValueError("max_depth must be at least 1")
        self._rules = {_match_key(rule.origin_phrase): rule for rule in rules}
        self.max_depth = max_depth

    def transform_text(
        self,
        source_text: str,
        field_path: str,
        co_signers: Sequence[str] = (),
        co_signature_ref: Optional[str] = None,
    ) -> BirthCursiveRecord:
        signers = tuple(dict.fromkeys(
            signer.strip() for signer in co_signers
            if isinstance(signer, str) and signer.strip()
        ))
        signature_ref = (
            co_signature_ref.strip()
            if isinstance(co_signature_ref, str) and co_signature_ref.strip()
            else None
        )
        rule = self._rules.get(_match_key(source_text))
        if rule is None:
            derived, meaning, possibility, rule_id, status = (
                source_text, None, None, None, "REVIEW_REQUIRED"
            )
        else:
            derived, meaning, possibility, rule_id, status = (
                rule.blessing, rule.meaning, rule.possibility,
                rule.rule_id, "DERIVED"
            )
        co_status = (
            "REFERENCE_ATTACHED_UNVERIFIED"
            if signature_ref is not None and signers else "PENDING"
        )
        return BirthCursiveRecord(
            schema="yaero.birth-cursive/1",
            field_path=field_path,
            origin_text=source_text,
            origin_sha256=_digest(source_text),
            meaning=meaning,
            possibility=possibility,
            derived_text=derived,
            derived_sha256=_digest(derived),
            rule_id=rule_id,
            status=status,
            co_signers=signers,
            co_signature_ref=signature_ref,
            co_signature_status=co_status,
        )

    def transform_tree(
        self,
        source: Any,
        co_signers: Sequence[str] = (),
        co_signature_ref: Optional[str] = None,
    ) -> Tuple[Any, List[BirthCursiveRecord]]:
        """Return a derived copy and lineage records using an explicit work stack."""
        records: List[BirthCursiveRecord] = []
        active: Set[int] = set()
        root: List[Any] = [None]

        def assign_root(value: Any) -> None:
            root[0] = value

        # Tasks are tuples: visit, exit, or tuple_finalize. No Python call
        # recursively descends the input structure.
        stack = [("visit", source, "", 0, False, False, assign_root)]
        while stack:
            task = stack.pop()
            kind = task[0]

            if kind == "exit":
                active.remove(task[1])
                continue

            if kind == "tuple_finalize":
                _, identity, values, setter = task
                setter(tuple(values))
                active.remove(identity)
                continue

            _, value, path, depth, text_context, blocked, setter = task
            if depth > self.max_depth:
                raise CursiveDepthError(
                    "maximum nested UI depth exceeded at " + (path or "/")
                )

            if isinstance(value, str):
                if blocked or not text_context:
                    setter(value)
                else:
                    record = self.transform_text(
                        value, path or "/", co_signers, co_signature_ref
                    )
                    records.append(record)
                    setter(record.derived_text)
                continue

            if isinstance(value, Mapping):
                identity = id(value)
                if identity in active:
                    raise CursiveCycleError("cycle detected at " + (path or "/"))
                active.add(identity)
                derived: Dict[Any, Any] = {}
                setter(derived)
                stack.append(("exit", identity))
                entries = list(value.items())
                for key, child in reversed(entries):
                    key_text = key if isinstance(key, str) else str(key)
                    child_path = path + "/" + key_text.replace("~", "~0").replace("/", "~1")
                    child_blocked = blocked or key_text in NEVER_TRANSFORM_FIELDS
                    child_text = (not child_blocked and key_text in TEXT_FIELDS)
                    stack.append((
                        "visit", child, child_path, depth + 1,
                        child_text, child_blocked,
                        lambda result, target=derived, target_key=key: target.__setitem__(target_key, result),
                    ))
                continue

            if isinstance(value, list):
                identity = id(value)
                if identity in active:
                    raise CursiveCycleError("cycle detected at " + (path or "/"))
                active.add(identity)
                derived_list: List[Any] = [None] * len(value)
                setter(derived_list)
                stack.append(("exit", identity))
                for index in range(len(value) - 1, -1, -1):
                    stack.append((
                        "visit", value[index], path + "/" + str(index),
                        depth + 1, text_context, blocked,
                        lambda result, target=derived_list, target_index=index: target.__setitem__(target_index, result),
                    ))
                continue

            if isinstance(value, tuple):
                identity = id(value)
                if identity in active:
                    raise CursiveCycleError("cycle detected at " + (path or "/"))
                active.add(identity)
                values: List[Any] = [None] * len(value)
                stack.append(("tuple_finalize", identity, values, setter))
                for index in range(len(value) - 1, -1, -1):
                    stack.append((
                        "visit", value[index], path + "/" + str(index),
                        depth + 1, text_context, blocked,
                        lambda result, target=values, target_index=index: target.__setitem__(target_index, result),
                    ))
                continue

            setter(value)

        return root[0], records
