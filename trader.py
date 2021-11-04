from bravado.client import SwaggerClient
import Responses
import bybit

class Trader:

    def __init__(self, api_key, api_secret, symbol, openTH, closeTH, interval, limit, openWeight, closeWeight) -> None:
        self._client = Trader._makeClient(api_key, api_secret)
        self._symbol = symbol
        self._interval = interval
        self._limit = limit
        self.openTH = openTH
        self.closeTH = closeTH
        self._openWeight = openWeight
        self._closeWeight = closeWeight
        
    def getQtyStep(self):
        return self._qty_step

    def getTickSize(self):
        return self._tick_size

    def _makeClient(key, secret) -> SwaggerClient:
        client = bybit.bybit(test=False, api_key=key, api_secret=secret)
        Responses.BybitResponse(client.APIkey.APIkey_info().result())
        print('Successfully Created Client')
        return client
        
    def _getServerTime(self) -> float:
        response = Responses.ServerTime(self._client.Common.Common_getTime().result())
        return float(response.time)

    def _querySymbol(self, symbol) -> dict:
        response = Responses.Symbols(self._client.Symbol.Symbol_get().result())
        for coin in response.result:
            if coin['name'] == symbol:
                return coin
        raise Exception('Invalid Symbol', symbol)

    def _initValues(self) -> None:
        coin = self._querySymbol(self._symbol)
        self._qty_step = coin['lot_size_filter']['qty_step']
        self._tick_size = coin['price_filter']['tick_size']

        print('Initialized Values',
              '\n - Interval:', self._interval,
              '\n - Limit:', self._limit,
              '\n - Symbol:', self._symbol, 
              '\n - openTH:', self.openTH, 
              '\n - closeTH:', self.closeTH,
              '\n - openWeight:', self._openWeight,
              '\n - closeWeight:', self._closeWeight,
              '\n - qty_step:', self._qty_step,
              '\n - tick_size:', self._tick_size)