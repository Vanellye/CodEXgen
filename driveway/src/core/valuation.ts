export interface ValuationRule {
  unit: string;
  currency: string;
  minorUnitsPerUnit: number;
  valuationOnly: boolean;
}
export function valueUnits(units: number, rule: ValuationRule): number {
  if (!Number.isFinite(units) || units < 0) throw new Error("Units must be a finite non-negative number");
  if (!Number.isSafeInteger(rule.minorUnitsPerUnit) || rule.minorUnitsPerUnit < 0) throw new Error("Invalid valuation rate");
  return Math.round(units * rule.minorUnitsPerUnit);
}
// Example policy: 1 POINT = 1 USD. This is a valuation only, not a redemption promise.
export const onePointOneDollar: ValuationRule = Object.freeze({
  unit: "POINT", currency: "USD", minorUnitsPerUnit: 100, valuationOnly: true
});
