from dataclasses import dataclass
from enum import Enum
from requests import Response
from typing import Optional


class ClaimStatus(Enum):
    Pending = "pending"
    Approved = "approved"
    Canceled = "canceled"
    Denied = "denied"


class Scope(Enum):
    Pay = "vc.pay"
    Claim = "vc.claim"


@dataclass
class DiscordUser:
    id: int
    username: str
    discriminator: str
    avatar: str
    public_flags: Optional[bool] = None
    bot: Optional[bool] = None
    system: Optional[bool] = None
    mfa_enabled: Optional[bool] = None
    premium_type: Optional[int] = None

    @classmethod
    def by_json(cls, data: dict):
        return cls(
            id=int(data["id"]),
            username=data["username"],
            discriminator=data["discriminator"],
            avatar=data["avatar"],
            public_flags=data.get("public_flags", None),
            bot=data.get("bot",  None),
            system=data.get("system", None),
            mfa_enabled=data.get("mfa_enabled", None),
            premium_type=data.get("premium_type", None)
        )


@dataclass
class User:
    id: int
    discord: DiscordUser

    @classmethod
    def by_json(cls, data: dict):
        return cls(id=int(data["id"]), discord=DiscordUser.by_json(data["discord"]))


@dataclass
class Currency:
    unit: str
    guild: int
    name: str
    pool_amount: int
    total_amount: Optional[int]

    @classmethod
    def by_json(cls, data: dict):
        if 'error' in data.keys():
            return None

        return cls(
            unit=data['unit'],
            guild=int(data['guild']),
            name=data['name'],
            pool_amount=int(data['pool_amount']),
            total_amount=int(data['total_amount']) if 'total_amount' in data.keys() else None
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
    updated_at: str

    @classmethod
    def by_json(cls, data):
        return cls(
            id=int(data["id"]),
            amount=int(data["amount"]),
            claimant=User.by_json(data["claimant"]),
            payer=User.by_json(data["payer"]),
            currency=Currency.by_json(data["currency"]),
            status=ClaimStatus(data["status"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )

    def approve(self, client):
        return client.update_claim(self.id, ClaimStatus.Approved)

    def deny(self, client):
        return client.update_claim(self.id, ClaimStatus.Denied)

    def cancel(self, client):
        return client.update_claim(self.id, ClaimStatus.Canceled)


@dataclass
class Balance:
    amount: int
    currency: Currency

    @classmethod
    def by_json(cls, data):
        return cls(
            amount=int(data['amount']),
            currency=Currency.by_json(data['currency'])
        )
