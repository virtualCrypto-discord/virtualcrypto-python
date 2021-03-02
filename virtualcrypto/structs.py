from dataclasses import dataclass
from enum import Enum
from requests import Response


class ClaimStatus(Enum):
    Pending = "pending"
    Approved = "approved"
    Canceled = "canceled"
    Denied = "denied"


class Scope(Enum):
    Pay = "vc.pay"
    Claim = "vc.claim"


@dataclass
class User:
    id: int
    discord_id: int


@dataclass
class Currency:
    unit: str
    guild: int
    name: str
    pool_amount: int
    total_amount: int

    @classmethod
    def by_response(cls, response: Response):
        data = response.json()
        if 'error' in data.keys():
            return None

        return cls(
            unit=data['unit'],
            guild=int(data['guild']),
            name=data['name'],
            pool_amount=int(data['pool_amount']),
            total_amount=int(data['total_amount'])
        )


@dataclass
class Claim:
    id: int
    amount: int
    claimant: User
    payer: User
    currency: Currency
    status: ClaimStatus
    created_at: str
