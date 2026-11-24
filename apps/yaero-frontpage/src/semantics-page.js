import { decodeCurrencyRecord, renderCurrencyEnglish, interpretCurrencyIntent } from "./semantics/currency.js";
import { splitIn2, translateDimensionsToEnglish } from "./semantics/dimensional-in2.js";

const readJson = (id) => {
  const raw = document.querySelector(id).value;
  return { raw, value: JSON.parse(raw) };
};
const show = (id, value) => { document.querySelector(id).textContent = JSON.stringify(value, null, 2); };

document.querySelector("#decode-currency").addEventListener("click", () => {
  try {
    const { raw } = readJson("#currency-input");
    const decoded = decodeCurrencyRecord(raw);
    let evidence = {};
    const evidenceText = document.querySelector("#intent-input").value.trim();
    if (evidenceText) evidence = JSON.parse(evidenceText);
    show("#currency-output", {
      decoded,
      english: renderCurrencyEnglish(decoded),
      intent: interpretCurrencyIntent(decoded, evidence),
      sourcePreserved: decoded.sourceSnapshot === raw
    });
  } catch (error) {
    show("#currency-output", { status: "INVALID", reason: error.message, sourcePreserved: true });
  }
});

document.querySelector("#split-in2").addEventListener("click", () => {
  try {
    const { raw, value } = readJson("#in2-input");
    const split = splitIn2({ ...value, sourceSnapshot: raw });
    show("#in2-output", { split, english: translateDimensionsToEnglish(split) });
  } catch (error) {
    show("#in2-output", { status: "INVALID", reason: error.message, sourcePreserved: true });
  }
});
