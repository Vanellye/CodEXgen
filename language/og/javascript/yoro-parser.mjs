/** Ɣơ parser prototype: syntax to AST only; never evaluates source. */
const tokenPattern = /\s+|"(?:\\.|[^"\\])*"|☆|k|∞|△|§|∴|&|→|[A-Za-z_][A-Za-z0-9_]*|[{}(),;=]/uy;
export function tokenize(source) {
  const tokens = [];
  let offset = 0;
  while (offset < source.length) {
    tokenPattern.lastIndex = offset;
    const match = tokenPattern.exec(source);
    if (!match) throw new SyntaxError(`Unexpected character at ${offset}`);
    offset = tokenPattern.lastIndex;
    if (!/^\s+$/u.test(match[0])) tokens.push(match[0]);
  }
  return tokens;
}
export function parse(source) {
  const tokens = tokenize(source);
  let i = 0;
  const peek = () => tokens[i];
  const take = expected => {
    const got = tokens[i++];
    if (expected !== undefined && got !== expected) throw new SyntaxError(`Expected ${expected}, got ${got}`);
    return got;
  };
  const expression = () => {
    let left = primary();
    while (peek() === "&" || peek() === "→") {
      const op = take();
      left = { type: op === "&" ? "Compose" : "Transform", left, right: primary() };
    }
    return left;
  };
  const primary = () => {
    const t = peek();
    if (t === "☆" || t === "k" || t === "∞") { take(); return { type: "Literal", value: t }; }
    if (t === "△") {
      take(); take("(");
      const items = [expression()]; take(",");
      items.push(expression()); take(",");
      items.push(expression()); take(")");
      return { type: "Triad", items };
    }
    if (t === "∴") { take(); return { type: "Derived", expression: expression() }; }
    if (t === "§") {
      take(); const name = take();
      take("{"); const body = [];
      while (peek() !== "}") {
        if (peek() === undefined) throw new SyntaxError("Unclosed scope");
        body.push(expression()); if (peek() === ";") take(";");
        else if (peek() !== "}") throw new SyntaxError("Expected ';' or '}'");
      }
      take("}");
      return { type: "Scope", name, body };
    }
    if (t?.startsWith('"')) { take(); return { type: "String", value: JSON.parse(t) }; }
    if (t && /^[A-Za-z_]/u.test(t)) { take(); return { type: "Identifier", name: t }; }
    throw new SyntaxError("Expected expression, got " + String(t));
  };
  const ast = [];
  while (i < tokens.length) {
    ast.push(expression());
    if (peek() === ";") take(";");
    else if (i < tokens.length) throw new SyntaxError("Expected ';' between expressions");
  }
  return { type: "Program", body: ast };
}
