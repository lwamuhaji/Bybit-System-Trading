from bravado.client import SwaggerClient
import Responses
import bybit
from coinsymbol import Symbol

class Trader:

    def __init__(self, api_key: str, api_secret: str, symbol: str) -> None:
        self.client: SwaggerClient = Trader.__createClient(api_key, api_secret)
        self.symbol: Symbol = Symbol(symbol, self.client)

    def __createClient(key, secret) -> SwaggerClient:
        client = bybit.bybit(test=False, api_key=key, api_secret=secret)
        Responses.BybitResponse(client.APIkey.APIkey_info().result())
        return client

    def __str__(self) -> str:
        return str(self.symbol)