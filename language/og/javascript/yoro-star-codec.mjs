import fs from "node:fs";

const PREFIX = "Ɣơ/2:";
export function encodeBytes(input) {
  const bytes = input instanceof Uint8Array ? input : Uint8Array.from(input);
  return PREFIX + Array.from(bytes, byte =>
    Array.from({ length: 8 }, (_, i) => (byte >> (7 - i)) & 1 ? "k" : "☆").join("")
  ).join(".");
}
export function decodeBytes(text) {
  if (!text.startsWith(PREFIX)) throw new Error("Unsupported Ɣơ profile");
  const body = text.slice(PREFIX.length);
  if (body === "") return new Uint8Array();
  const groups = body.split(".");
  if (groups.some(g => g.length !== 8 || /[^☆k]/u.test(g)))
    throw new Error("Each byte must contain exactly eight ☆/k symbols");
  return Uint8Array.from(groups, g => [...g].reduce((n, c) => (n << 1) | (c === "k" ? 1 : 0), 0));
}
export function validateVectors(path) {
  const lines = fs.readFileSync(path, "utf8").split(/\r?\n/u)
    .filter(line => line.trim() && !line.startsWith("#"));
  for (const line of lines) {
    const [name, hex, expected] = line.split("|");
    if (hex === undefined || expected === undefined) throw new Error("Malformed vector: " + line);
    const bytes = Uint8Array.from(hex.match(/../gu) ?? [], pair => parseInt(pair, 16));
    if (encodeBytes(bytes) !== expected) throw new Error("Encode mismatch: " + name);
    const decoded = decodeBytes(expected);
    if (decoded.length !== bytes.length || decoded.some((v, i) => v !== bytes[i]))
      throw new Error("Decode mismatch: " + name);
  }
  return lines.length;
}
if (process.argv[1] && import.meta.url === new URL("file://" + process.argv[1]).href) {
  console.log("JavaScript Ɣơ/2 vectors passed:", validateVectors(process.argv[2]));
}
