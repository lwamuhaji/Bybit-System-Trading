import Responses
from bravado.client import SwaggerClient

class Symbol:
    def __init__(self, symbol: str, client: SwaggerClient) -> None:
        self.symbol_name = symbol
        self.__checkSymbol(client)

    def __checkSymbol(self, client: SwaggerClient):
        response = Responses.Symbols(client.Symbol.Symbol_get().result())
        for symbol_info in response.result:
            if symbol_info['name'] == self.symbol_name:
                self.TICKSIZE = symbol_info['price_filter']['tick_size']
                self.QTYSTEP = symbol_info['lot_size_filter']['qty_step']
                return
        raise Exception('Invalid Symbol:', self.symbol_name)

    def __str__(self) -> str:
        return ' - Symbol: {0}\n - qty_step: {1}\n - tick_size: {2}'.format(self.symbol_name, self.QTYSTEP, self.TICKSIZE)
