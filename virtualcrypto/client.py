from requests.auth import HTTPBasicAuth
import requests
from .structs import Currency, Scope
from .errors import MissingScope, BadRequest
from typing import Optional, Any, List
VIRTUALCRYPTO_ENDPOINT = "https://vcrypto.sumidora.com"
VIRTUALCRYPTO_API = VIRTUALCRYPTO_ENDPOINT + "/api/v1"
VIRTUALCRYPTO_TOKEN_ENDPOINT = VIRTUALCRYPTO_ENDPOINT + "/oauth2/token"


class VirtualCryptoClientBase:
    def __init__(self, client_id: str, client_secret: str, scopes: List[Scope]):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.token = None

    def get(self, path: str, params: dict, expect=None):
        pass

    def post(self, path, data, expect=None):
        pass

    def get_currency_by_unit(self, unit: str):
        pass

    def get_currency_by_guild(self, guild_id: int):
        pass

    def get_currency_by_name(self, name: str):
        pass

    def get_currency_by_id(self, currency_id: int):
        pass

    def create_user_transactions(self, unit: str, receiver_discord_id: int, amount: int):
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

    def get(self, path, params, expect=None) -> Any:
        headers = {
            "Authorization": "Bearer " + self.token
        }
        result = requests.get(
            VIRTUALCRYPTO_API + path,
            params=params,
            headers=headers
        )
        if expect is not None:
            return expect(result)
        return result

    def post(self, path, data, expect=None) -> Any:
        headers = {
            "Authorization": "Bearer " + self.token
        }
        result = requests.post(
            VIRTUALCRYPTO_API + path,
            data=data,
            headers=headers
        )
        if expect is not None:
            return expect(result)
        return result

    def get_currency_by_unit(self, unit: str) -> Optional[Currency]:
        return self.get("/currencies", {"unit": unit}, Currency.by_response)

    def get_currency_by_guild(self, guild_id: int) -> Optional[Currency]:
        return self.get("/currencies", {"guild": str(guild_id)}, Currency.by_response)

    def get_currency_by_name(self, name: str) -> Optional[Currency]:
        return self.get("/currencies", {"name": name}, Currency.by_response)

    def get_currency_by_id(self, currency_id: int):
        return self.get("/currencies/" + str(currency_id), {}, Currency.by_response)

    def create_user_transactions(self, unit: str, receiver_discord_id: int, amount: int):
        if Scope.Pay not in self.scopes:
            raise MissingScope("vc.pay")
        result: requests.Response = self.post(
            "/users/@me/transactions",
            {
                "unit": unit,
                "receiver_discord_id": str(receiver_discord_id),
                "amount": str(amount)
            }
        )
        if result.status_code == 400:
            raise BadRequest(result.json()["error_info"])

    pay = create_user_transactions
