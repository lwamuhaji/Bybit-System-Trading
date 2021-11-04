from typing import NamedTuple
import Responses
from trader import Trader

class DerivativesTrader(Trader):

    class Spread(NamedTuple):
        openTop: float
        openBottom: float
        closeTop: float
        closeBottom: float

    class Account(NamedTuple):
        buyOrder: Responses.OrderWithStatus
        sellOrder: Responses.OrderWithStatus

    def __init__(self, api_key, api_secret, symbol, openTH, closeTH, interval, limit, openWeight, closeWeight) -> None:
        super().__init__(api_key=api_key, api_secret=api_secret, symbol=symbol, openTH=openTH, closeTH=closeTH, interval=interval, limit=limit, openWeight=openWeight, closeWeight=closeWeight)
        super()._initValues()

    def __getTradingRecord(self) -> Responses.TradingRecord:
        return Responses.TradingRecord(self._client.LinearMarket.LinearMarket_trading(symbol=self._symbol).result())

    def __getPPO(self) -> tuple:
        average_price = self.__getAvgPrice()
        current_price = self.__getTradingRecord().last['price']
        return (average_price - current_price) / average_price

    def __getCandles(self) -> list:
        time: float = self._getServerTime() - int(self._interval) * (self._limit + 1) * 60
        response = Responses.Candles(self._client.LinearKline.LinearKline_get(symbol=self._symbol, interval=self._interval, limit=self._limit, **{'from':time}).result())

        if len(response.result) == self._limit + 1:
            return response.result[:self._limit]
        elif len(response.result) == self._limit:
            return response.result
        else:
            raise Exception('Error on amount of candles', len(response.result))

    def __getAvgPrice(self) -> float:
        total = 0.0
        for candle in self.__getCandles():
            total += candle['close']
        return total / self._limit

    def getOrders(self, status='All') -> Responses.OrderList:
        if status == 'All':
            return Responses.OrderList(self._client.LinearOrder.LinearOrder_getOrders(symbol=self._symbol).result())
        return Responses.OrderList(self._client.LinearOrder.LinearOrder_getOrders(symbol=self._symbol, order_status=status).result())

    def queryOrder(self, order: Responses.BybitResponse) -> Responses.OrderWithStatus:
        return Responses.OrderWithStatus(self._client.LinearOrder.LinearOrder_query(symbol=self._symbol, order_id=order.order_id).result())

    def getPositions(self) -> Responses.Positions:
        return Responses.Positions(self._client.LinearPositions.LinearPositions_myPosition(symbol=self._symbol).result())

    def setTradingStop(self, side, price) -> Responses.TradingStop:
        return Responses.TradingStop(self._client.LinearPositions.LinearPositions_tradingStop(symbol=self._symbol, side=side, take_profit=price).result())

    def placeOrder(self, side, qty, price) -> Responses.OrderWithStatus:
        return Responses.OrderWithStatus(
        self._client.LinearOrder.LinearOrder_new(
        side=side,
        symbol=self._symbol,
        order_type="Limit",
        qty=qty,
        price=price,
        time_in_force="GoodTillCancel",
        reduce_only=False,
        close_on_trigger=False)
        .result())

    def getOpenSpread(self):
        average_price = self.__getAvgPrice()
        return average_price + average_price * self.openTH, average_price - average_price * self.openTH

    def getCloseSpread(self):
        average_price = self.__getAvgPrice()
        return average_price + average_price * self.closeTH, average_price - average_price * self.closeTH

    def cancelOrder(self, order_id) -> Responses.Order:
        return Responses.Order(self._client.LinearOrder.LinearOrder_cancel(symbol=self._symbol, order_id=order_id).result())

    def replaceOrder(self, order_id, price) -> Responses.Order:
        return Responses.Order(self._client.LinearOrder.LinearOrder_replace(symbol=self._symbol, order_id=order_id, p_r_price=price).result())