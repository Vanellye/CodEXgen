# Ɣơ Fixtures

`byte-vectors.json` lists canonical hexadecimal byte inputs for future cross-implementation tests.

A fixture's hexadecimal string is exact: preserve empty strings, leading zero byte pairs, case-normalized hex, and order. Test reports should identify the vector and profile version.

Fixtures are immutable inputs during normal test execution. Any change needs a reviewed explanation and corresponding test update.
