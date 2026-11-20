# ERIA FILLER

FILLER is the repository structure-completion layer. It compares an explicit manifest
of required destinations with reviewed templates, reports missing structures, and can
create only absent targets after branch-bound human approval.

- Governance: [AÐð Fïl·lĕŕ — Rightous Companioxn Protocol](RIGHTOUS-COMPANION-PROTOCOL.md)
- Utility: [tools/filler/filler.sh](../../tools/filler/filler.sh)
- Mapping manifest: [tools/filler/filler.manifest](../../tools/filler/filler.manifest)

## Operating modes

- **Plan:** read-only; default mode.
- **Apply:** requires `--approve feature/ashes-to-angels-pheonix` and that exact
  checked-out branch.
- **Existing source:** always preserved.
- **Unmapped structure:** reported as unknown; never guessed into existence.

FILLER currently supports reviewed template mappings only. Recursive discovery,
dependency inference, UP/DOWN messaging, and runtime integration are future work and
must not be treated as implemented.
