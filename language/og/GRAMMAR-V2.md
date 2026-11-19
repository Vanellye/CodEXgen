# Ɣơ grammar prototype v2

Status: experimental parser contract. The JavaScript parser builds an AST only and does not evaluate, compile, or execute input.

## Glyph semantics

| Glyph | Prototype meaning |
|---|---|
| `☆` | explicit zero / absence literal |
| `k` | explicit one / presence literal |
| `∞` | unbounded or open-ended *symbolic* value; runtime resource limits remain finite |
| `△` | exactly three ordered related expressions (triad) |
| `§` | named scope boundary |
| `&` | composition |
| `→` | transformation relation |
| `∴` | derived-expression marker |

These are language-level values and operators. They do not alter binary hardware storage or imply infinite physical computation.

## EBNF (prototype)

```ebnf
program      = expression, { ";", expression }, [ ";" ] ;
expression   = primary, { ("&" | "→"), primary } ;
primary      = "☆" | "k" | "∞" | string
             | identifier
             | "△", "(", expression, ",", expression, ",", expression, ")"
             | "∴", expression
             | "§", identifier, "{", [ expression, { ";", expression }, [ ";" ] ], "}" ;
string       = JSON-compatible quoted string ;
identifier   = letter, { letter | digit | "_" } ;
```

The prototype intentionally omits functions, loops, imports, mutation, I/O, and arbitrary JavaScript syntax. It is a small syntax/AST experiment, not a JavaScript replacement yet.
