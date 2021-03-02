from requests.auth import HTTPBasicAuth
import requests
from .structs import Currency
from typing import Optional, Any
VIRTUALCRYPTO_ENDPOINT = "http://localhost"
VIRTUALCRYPTO_API = VIRTUALCRYPTO_ENDPOINT + "/api/v1"
VIRTUALCRYPTO_TOKEN_ENDPOINT = VIRTUALCRYPTO_ENDPOINT + "/oauth2/token"


class VirtualCryptoClientBase:
    def __init__(self, client_id, client_secret, scopes):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.token = None

    def get(self, path: str, params: dict, expect):
        pass

    def get_currency_by_unit(self, unit: str):
        pass

    def get_currency_by_guild(self, guild_id: int):
        pass

    def get_currency_by_name(self, name: str):
        pass


class VirtualCryptoClient(VirtualCryptoClientBase):
    def __init__(self, client_id, client_secret, scopes):
        super().__init__(client_id, client_secret, scopes)
        body = {
            'scope': ' '.join(scopes),
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

    def get(self, path, params, expect) -> Any:
        headers = {
            "Authorization": "Bearer " + self.token
        }
        result = requests.get(
            VIRTUALCRYPTO_API + path,
            params=params,
            headers=headers
        )
        expect(result.json())

    def get_currency_by_unit(self, unit: str) -> Optional[Currency]:
        return self.get("/currencies", {"unit": unit}, Currency.by_json)

    def get_currency_by_guild(self, guild_id: int) -> Optional[Currency]:
        return self.get("/currencies", {"guild": str(guild_id)}, Currency.by_json)

    def get_currency_by_name(self, name: str) -> Optional[Currency]:
        return self.get("/currencies", {"name": name}, Currency.by_json)
