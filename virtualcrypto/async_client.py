from .structs import Currency, Scope, Claim, ClaimStatus, Balance
from .errors import MissingScope, BadRequest, NotFound
from .client import VirtualCryptoClientBase, VIRTUALCRYPTO_TOKEN_ENDPOINT, VIRTUALCRYPTO_API
from typing import Optional, List
import datetime
import aiohttp
import asyncio


class AsyncVirtualCryptoClient(VirtualCryptoClientBase):
    def __init__(self, client_id: str, client_secret: str, scopes: List[Scope], loop=asyncio.get_event_loop()):
        super().__init__(client_id, client_secret, scopes)
        self.loop = loop
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.wait_ready = asyncio.Event(loop=self.loop)

    async def wait_for_ready(self):
        await self.wait_ready.wait()

    async def start(self):
        await self.set_token()
        self.wait_ready.set()

    async def close(self):
        await self.session.close()

    async def set_token(self):
        body = {
            'scope': ' '.join(map(lambda x: x.value, self.scopes)),
            'grant_type': 'client_credentials'
        }
        async with self.session.post(
                VIRTUALCRYPTO_TOKEN_ENDPOINT,
                data=body,
                auth=aiohttp.BasicAuth(self.client_id, self.client_secret)) as response:
            data = await response.json()

        self.token = data['access_token']
        self.expires_in = data['expires_in']
        self.token_type = data['token_type']
        self.when_set_token = datetime.datetime.utcnow()

    async def get_headers(self):
        if (datetime.datetime.utcnow() - self.when_set_token).seconds >= self.expires_in:
            await self.set_token()
        return {
            "Authorization": "Bearer " + self.token
        }

    async def get(self, path, params) -> aiohttp.ClientResponse:
        headers = await self.get_headers()

        return await self.session.get(VIRTUALCRYPTO_API + path, params=params, headers=headers)

    async def post(self, path, data) -> aiohttp.ClientResponse:
        headers = await self.get_headers()
        return await self.session.post(VIRTUALCRYPTO_API + path, data=data, headers=headers)

    async def patch(self, path, data) -> aiohttp.ClientResponse:
        headers = await self.get_headers()
        return await self.session.patch(VIRTUALCRYPTO_API + path, data=data, headers=headers)

    async def get_currency_by_unit(self, unit: str) -> Optional[Currency]:
        response = await self.get("/currencies", {"unit": unit})

        return Currency.by_json(await response.json())

    async def get_currency_by_guild(self, guild_id: int) -> Optional[Currency]:
        response = await self.get("/currencies", {"guild": str(guild_id)})

        return Currency.by_json(await response.json())

    async def get_currency_by_name(self, name: str) -> Optional[Currency]:
        response = await self.get("/currencies", {"name": name})
        return Currency.by_json(await response.json())

    async def get_currency(self, currency_id: int):
        response = await self.get("/currencies/" + str(currency_id), {})

        return Currency.by_json(await response.json())

    async def create_user_transaction(self, unit: str, receiver_discord_id: int, amount: int) -> None:
        if Scope.Pay not in self.scopes:
            raise MissingScope("vc.pay")

        response = await self.post(
            "/users/@me/transactions",
            {
                "unit": unit,
                "receiver_discord_id": str(receiver_discord_id),
                "amount": str(amount)
            }
        )
        if response.status == 400:
            raise BadRequest((await response.json())["error_info"])

    pay = create_user_transaction

    async def get_claims(self):
        if Scope.Claim not in self.scopes:
            raise MissingScope("vc.claim")

        response = await self.get(
            "/users/@me/claims",
            {}
        )
        return list(map(Claim.by_json, await response.json()))

    async def get_claim(self, claim_id: int):
        response = await self.get("/users/@me/claims/" + str(claim_id), {})
        return Claim.by_json(await response.json())

    async def update_claim(self, claim_id: int, status: ClaimStatus):
        if status == ClaimStatus.Pending:
            raise ValueError("can't update to pending")

        response = await self.patch(
            "/users/@me/claims/" + str(claim_id),
            {"status": status.value}
        )

        if response.status == 404:
            raise NotFound((await response.json())["error_description"])
        elif response.status == 400:
            raise BadRequest((await response.json())["error_info"])

        return response

    async def get_balances(self):
        response = await self.get(
            "/users/@me/balances",
            {}
        )
        return list(map(Balance.by_json, await response.json()))
