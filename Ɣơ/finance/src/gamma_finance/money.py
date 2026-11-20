"""Integer minor-unit money and dated rational FX quotes."""
from dataclasses import dataclass
from datetime import date
from fractions import Fraction

CURRENCY_EXPONENT = {"USD": 2, "EUR": 2, "RUB": 2, "KRW": 0}

@dataclass(frozen=True)
class Money:
    currency: str
    minor: int
    def __post_init__(self):
        if self.currency not in CURRENCY_EXPONENT:
            raise ValueError("unsupported currency")
        if not isinstance(self.minor, int) or isinstance(self.minor, bool):
            raise TypeError("minor amount must be an integer")
    def add(self, other):
        if self.currency != other.currency:
            raise ValueError("currency mismatch; use a dated FX quote")
        return Money(self.currency, self.minor + other.minor)

@dataclass(frozen=True)
class FxQuote:
    base: str
    quote: str
    rate: Fraction
    observed_on: date
    source: str
    def __post_init__(self):
        if self.base not in CURRENCY_EXPONENT or self.quote not in CURRENCY_EXPONENT:
            raise ValueError("unsupported FX currency")
        if self.base == self.quote or self.rate <= 0 or not self.source.strip():
            raise ValueError("FX requires distinct currencies, positive rate, and source")
    def convert_minor(self, amount: Money) -> Money:
        if amount.currency != self.base:
            raise ValueError("FX base currency mismatch")
        base_scale = 10 ** CURRENCY_EXPONENT[self.base]
        quote_scale = 10 ** CURRENCY_EXPONENT[self.quote]
        exact = Fraction(amount.minor, base_scale) * self.rate * quote_scale
        q, r = divmod(abs(exact.numerator), exact.denominator)
        if 2 * r > exact.denominator or (2 * r == exact.denominator and q % 2):
            q += 1
        return Money(self.quote, q if exact >= 0 else -q)
