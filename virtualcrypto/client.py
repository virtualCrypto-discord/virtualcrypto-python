from requests.auth import HTTPBasicAuth
import requests
from .structs import Currency, Scope, Claim, ClaimStatus
from .errors import MissingScope, BadRequest, NotFound
from typing import Optional, Any, List
VIRTUALCRYPTO_ENDPOINT = "http://localhost"
VIRTUALCRYPTO_API = VIRTUALCRYPTO_ENDPOINT + "/api/v1"
VIRTUALCRYPTO_TOKEN_ENDPOINT = VIRTUALCRYPTO_ENDPOINT + "/oauth2/token"


class VirtualCryptoClientBase:
    def __init__(self, client_id: str, client_secret: str, scopes: List[Scope]):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.token = None

    def get(self, path: str, params: dict):
        pass

    def post(self, path, data):
        pass

    def patch(self, path, data):
        pass

    def get_currency_by_unit(self, unit: str):
        pass

    def get_currency_by_guild(self, guild_id: int):
        pass

    def get_currency_by_name(self, name: str):
        pass

    def get_currency_by_id(self, currency_id: int):
        pass

    def create_user_transaction(self, unit: str, receiver_discord_id: int, amount: int):
        pass

    def get_claims(self):
        pass

    def get_claim(self, claim_id: int):
        pass

    def update_claim(self, claim_id: int, status: ClaimStatus):
        pass


class VirtualCryptoClient(VirtualCryptoClientBase):
    def __init__(self, client_id, client_secret, scopes):
        super().__init__(client_id, client_secret, scopes)
        body = {
            'scope': ' '.join(map(lambda x: x.value, scopes)),
            'grant_type': 'client_credentials'
        }
        data = requests.post(
            VIRTUALCRYPTO_TOKEN_ENDPOINT,
            data=body,
            auth=HTTPBasicAuth(client_id, client_secret)
        ).json()
        self.token = data['access_token']
        self.expires_in = data['expires_in']
        self.token_type = data['token_type']

    def get(self, path, params) -> Any:
        headers = {
            "Authorization": "Bearer " + self.token
        }
        result = requests.get(
            VIRTUALCRYPTO_API + path,
            params=params,
            headers=headers
        )
        return result

    def post(self, path, data) -> requests.Response:
        headers = {
            "Authorization": "Bearer " + self.token
        }
        result = requests.post(
            VIRTUALCRYPTO_API + path,
            data=data,
            headers=headers
        )
        return result

    def patch(self, path, data) -> requests.Response:
        headers = {
            "Authorization": "Bearer " + self.token
        }
        result = requests.patch(
            VIRTUALCRYPTO_API + path,
            data=data,
            headers=headers
        )
        return result

    def get_currency_by_unit(self, unit: str) -> Optional[Currency]:
        return Currency.by_json(self.get("/currencies", {"unit": unit}).json())

    def get_currency_by_guild(self, guild_id: int) -> Optional[Currency]:
        return Currency.by_json(self.get("/currencies", {"guild": str(guild_id)}).json())

    def get_currency_by_name(self, name: str) -> Optional[Currency]:
        return Currency.by_json(self.get("/currencies", {"name": name}).json())

    def get_currency(self, currency_id: int):
        return Currency.by_json(self.get("/currencies/" + str(currency_id), {}).json())

    def create_user_transaction(self, unit: str, receiver_discord_id: int, amount: int) -> None:
        if Scope.Pay not in self.scopes:
            raise MissingScope("vc.pay")
        result = self.post(
            "/users/@me/transactions",
            {
                "unit": unit,
                "receiver_discord_id": str(receiver_discord_id),
                "amount": str(amount)
            }
        )
        if result.status_code == 400:
            raise BadRequest(result.json()["error_info"])

    pay = create_user_transaction

    def get_claims(self):
        if Scope.Claim not in self.scopes:
            raise MissingScope("vc.claim")
        result = self.get(
            "/users/@me/claims",
            {}
        )
        return list(map(Claim.by_json, result.json()))

    def get_claim(self, claim_id: int):
        return Claim.by_json(self.get("/users/@me/claims/" + str(claim_id), {}).json())

    def update_claim(self, claim_id: int, status: ClaimStatus):
        if status == ClaimStatus.Pending:
            raise ValueError("can't update to pending")

        result = self.patch(
            "/users/@me/claims/" + str(claim_id),
            {"status": status.value}
        )

        if result.status_code == 404:
            raise NotFound(result.json()["error_description"])
        elif result.status_code == 400:
            raise BadRequest(result.json()["error_info"])

        return result
