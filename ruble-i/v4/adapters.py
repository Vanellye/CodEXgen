"""Provider adapter stubs. They deliberately perform no network I/O."""
from dataclasses import dataclass

from coordinator import LiveExecutionDisabled


@dataclass(frozen=True)
class PreparedProviderRequest:
    provider: str
    rail: str
    beneficiary_ref: str
    asset: str
    amount_minor: int
    intent_sha256: str
    mode: str = "PREPARE_ONLY"


class BasePrepareOnlyAdapter:
    provider = "abstract"
    supported_rails: frozenset[str] = frozenset()

    def prepare(self, *, beneficiary_ref: str, rail: str, asset: str,
                amount_minor: int, intent_sha256: str) -> PreparedProviderRequest:
        if rail not in self.supported_rails:
            raise ValueError("unsupported rail for provider adapter")
        if not beneficiary_ref or amount_minor <= 0 or len(intent_sha256) != 64:
            raise ValueError("invalid provider preparation input")
        return PreparedProviderRequest(self.provider, rail, beneficiary_ref,
                                       asset, amount_minor, intent_sha256)

    def submit(self, *_args, **_kwargs):
        raise LiveExecutionDisabled("provider adapter is prepare-only; live submission disabled")


class WisePlatformAdapter(BasePrepareOnlyAdapter):
    provider = "wise_platform"
    supported_rails = frozenset({"IBAN_SEPA", "INTERNATIONAL_PAYOUT"})


class PlaidTransferAdapter(BasePrepareOnlyAdapter):
    provider = "plaid_transfer"
    supported_rails = frozenset({"ACH", "US_WIRE", "RTP", "FEDNOW"})
