/**
 * Ŷæṛö currency decoder and English renderer.
 * Exact minor-unit arithmetic only; never invent FX rates or coerce UNKNOWN to zero.
 */

export const CURRENCY_META = Object.freeze({
  USD: { name: "US dollar", major: "dollar", minor: "cent", exponent: 2 },
  EUR: { name: "euro", major: "euro", minor: "cent", exponent: 2 },
  RUB: { name: "Russian ruble", major: "ruble", minor: "kopek", exponent: 2 },
  KRW: { name: "South Korean won", major: "won", minor: "jeon", exponent: 0 }
});

const NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"];
const TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"];

function underThousand(value) {
  if (value < 20) return NUMBER_WORDS[value];
  if (value < 100) return TENS[Math.floor(value / 10)] + (value % 10 ? "-" + NUMBER_WORDS[value % 10] : "");
  return NUMBER_WORDS[Math.floor(value / 100)] + " hundred" + (value % 100 ? " " + underThousand(value % 100) : "");
}

export function integerToEnglish(input) {
  let value = BigInt(input);
  if (value < 0n) return "minus " + integerToEnglish(-value);
  if (value < 1000n) return underThousand(Number(value));
  const scales = [[1000000000000000000n, "quintillion"], [1000000000000000n, "quadrillion"], [1000000000000n, "trillion"], [1000000000n, "billion"], [1000000n, "million"], [1000n, "thousand"]];
  for (const [size, label] of scales) {
    if (value >= size) {
      const quotient = value / size;
      const remainder = value % size;
      return integerToEnglish(quotient) + " " + label + (remainder ? " " + integerToEnglish(remainder) : "");
    }
  }
  return underThousand(Number(value));
}

/** Parse a versioned, canonical JSON currency record without changing its source bytes. */
export function decodeCurrencyRecord(input) {
  const sourceSnapshot = typeof input === "string" ? input : JSON.stringify(input);
  let record;
  try {
    record = typeof input === "string" ? JSON.parse(input) : input;
  } catch {
    return { status: "INVALID", sourceSnapshot, diagnostics: ["Input is not valid JSON."] };
  }
  if (!record || typeof record !== "object" || Array.isArray(record)) {
    return { status: "INVALID", sourceSnapshot, diagnostics: ["Currency record must be an object."] };
  }
  if (record.schema !== "yaero.currency/1") {
    return { status: "UNSUPPORTED", sourceSnapshot, diagnostics: ["Expected schema yaero.currency/1."] };
  }
  const code = typeof record.currency === "string" ? record.currency.toUpperCase() : "";
  const meta = CURRENCY_META[code];
  if (!/^[A-Z]{3}$/.test(code)) {
    return { status: "INVALID", sourceSnapshot, diagnostics: ["currency must be a three-letter code."] };
  }
  if (typeof record.minorUnits !== "string" || !/^-?(0|[1-9]\d*)$/.test(record.minorUnits)) {
    return { status: "INVALID", sourceSnapshot, diagnostics: ["minorUnits must be a canonical integer string."] };
  }
  if (!meta) {
    return {
      status: "UNKNOWN_CURRENCY", currency: code, minorUnits: record.minorUnits,
      exponent: Number.isInteger(record.exponent) ? record.exponent : null,
      sourceSnapshot, diagnostics: ["Currency code is syntactically valid but not in the decoder's verified metadata table."]
    };
  }
  if (record.exponent !== meta.exponent) {
    return { status: "INVALID", sourceSnapshot, diagnostics: ["Exponent does not match the decoder's currency metadata."] };
  }
  return {
    status: "DECODED", currency: code, currencyName: meta.name,
    minorUnits: record.minorUnits, exponent: meta.exponent,
    sourceSnapshot, sourceRef: record.sourceRef ?? null,
    asOf: record.asOf ?? null,
    diagnostics: []
  };
}

export function renderCurrencyEnglish(decoded) {
  if (decoded.status !== "DECODED") {
    return { literal: decoded.status, english: "The currency amount cannot be fully decoded: " + decoded.diagnostics.join(" "), intent: "UNKNOWN" };
  }
  const meta = CURRENCY_META[decoded.currency];
  const minor = BigInt(decoded.minorUnits);
  const negative = minor < 0n;
  const absolute = negative ? -minor : minor;
  const scale = 10n ** BigInt(decoded.exponent);
  const major = decoded.exponent === 0 ? absolute : absolute / scale;
  const fraction = decoded.exponent === 0 ? 0n : absolute % scale;
  const majorLabel = meta.major + (major === 1n ? "" : "s");
  let amount = (negative ? "minus " : "") + integerToEnglish(major) + " " + majorLabel;
  if (decoded.exponent > 0 && fraction > 0n) {
    const minorLabel = meta.minor + (fraction === 1n ? "" : "s");
    amount += " and " + integerToEnglish(fraction) + " " + minorLabel;
  }
  return {
    literal: { currency: decoded.currency, minorUnits: decoded.minorUnits, exponent: decoded.exponent },
    english: amount,
    intent: "A monetary amount is represented; purpose or transaction direction is not established by the amount alone."
  };
}

/** Optional intent evidence is explicit metadata, not a guess from the amount. */
export function interpretCurrencyIntent(decoded, evidence = {}) {
  const action = typeof evidence.action === "string" ? evidence.action.toLowerCase() : null;
  const allowed = new Set(["payment", "receipt", "refund", "transfer", "quote", "balance"]);
  if (decoded.status !== "DECODED" || !action || !allowed.has(action)) {
    return { label: "UNKNOWN", confidence: "none", evidence: [], explanation: "The amount alone does not reveal why it exists." };
  }
  return {
    label: action.toUpperCase(), confidence: "explicit",
    evidence: [{ field: "action", value: action, sourceRef: evidence.sourceRef ?? null }],
    explanation: "Intent is taken from explicit action metadata, not inferred from the numeric amount."
  };
}
