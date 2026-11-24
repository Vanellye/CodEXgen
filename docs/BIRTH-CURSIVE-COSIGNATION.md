# Birth-Cursive Co-signation

The yaero.birth-cursive/1 engine derives constructive alternatives for allowlisted nested UI text while preserving each exact source string.

## Meaning

Birth-cursive is the origin-linked creation of a derived expression. Co-signation records the declared co-signers and a reference to an external co-signature event. The module does not create or verify cryptographic signatures; a trusted host must validate any attached signature.

## Processing contract

1. Preserve the original UI tree and exact source text.
2. Visit nested mappings and lists with cycle detection and a maximum depth.
3. Transform only strings under allowlisted presentation fields.
4. Keep code, commands, routes, URLs, identifiers, status codes, and security warnings unchanged.
5. Apply exact, versioned opposition rules. Unknown or ambiguous text remains unchanged and is marked REVIEW_REQUIRED.
6. Emit a separate derived tree and per-field lineage records containing origin and derived SHA-256 digests, reasoning, possibility, rule ID, and co-signation metadata.
7. Never treat a digest as proof of authorship, truth, approval, or cryptographic signature validity.

## Financial transaction boundary

The transfer policy no longer depends on PONS transaction authorization. It still requires authenticated account-holder confirmation bound to the exact transaction, configured limits, beneficiary verification, idempotency, audit evidence, and independent settlement verification. Live transfers remain disabled.

## Validation

Run:

    python -m unittest discover -s tests -p 'test_eria_birth_cursive.py' -v

Android Compose, the Termux conversation browser, the repository browser, and terminal output display the origin unchanged with a separate constructive possibility when an exact rule matches. Nested native data validation and birth-cursive tree traversal use explicit work stacks rather than call-stack descent.\n\nThe module is a deterministic exact-rule engine, not an unrestricted sentiment rewrite or a factual-outcome generator.
