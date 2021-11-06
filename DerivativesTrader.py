import Responses
from trader import Trader

class DerivativesTrader(Trader):

    def __init__(self, api_key, api_secret, symbol) -> None:
        super().__init__(api_key=api_key, api_secret=api_secret, symbol=symbol)

    def __getTradingRecord(self) -> Responses.TradingRecord:
        return Responses.TradingRecord(self.client.LinearMarket.LinearMarket_trading(symbol=self.symbol).result())

    def __getPPO(self) -> tuple:
        average_price = self.__getAvgPrice()
        current_price = self.__getTradingRecord().last['price']
        return (average_price - current_price) / average_price

    def __getCandles(self) -> list:
        time: float = self._getServerTime() - int(self.interval) * (self._limit + 1) * 60
        response = Responses.Candles(self.client.LinearKline.LinearKline_get(symbol=self.symbol, interval=self.interval, limit=self.limit, **{'from':time}).result())

        if len(response.result) == self.limit + 1:
            return response.result[:self.limit]
        elif len(response.result) == self.limit:
            return response.result
        else:
            raise Exception('Error on amount of candles', len(response.result))

    def getAvgPrice(self) -> float:
        total = 0.0
        for candle in self.__getCandles():
            total += candle['close']
        return total / self.limit

    def getOrders(self, status='All') -> Responses.OrderList:
        if status == 'All':
            return Responses.OrderList(self.client.LinearOrder.LinearOrder_getOrders(symbol=self.symbol).result())
        return Responses.OrderList(self.client.LinearOrder.LinearOrder_getOrders(symbol=self.symbol, order_status=status).result())

    def queryOrder(self, order: Responses.BybitResponse) -> Responses.OrderWithStatus:
        return Responses.OrderWithStatus(self.client.LinearOrder.LinearOrder_query(symbol=self.symbol, order_id=order.order_id).result())

    def getPositions(self) -> Responses.Positions:
        return Responses.Positions(self.client.LinearPositions.LinearPositions_myPosition(symbol=self.symbol).result())

    def hasPosition(self) -> bool:
        for position in self.getPositions().result:
            if position['size'] > 0:
                return True
        return False

    def setTradingStop(self, side, price) -> Responses.TradingStop:
        return Responses.TradingStop(self._client.LinearPositions.LinearPositions_tradingStop(symbol=self.symbol, side=side, take_profit=price).result())

    def placeOrder(self, side, qty, price) -> Responses.OrderWithStatus:
        response = Responses.OrderWithStatus(
        self._client.LinearOrder.LinearOrder_new(
        side=side,
        symbol=self.symbol,
        order_type="Limit",
        qty=qty,
        price=price,
        time_in_force="GoodTillCancel",
        reduce_only=False,
        close_on_trigger=False)
        .result())

        if response.order_status != 'New':
            raise Exception('Place order failed')
        else:
            return response

    def getOpenSpread(self):
        average_price = self.__getAvgPrice()
        return average_price + average_price * self.openTH, average_price - average_price * self.openTH

    def getCloseSpread(self):
        average_price = self.__getAvgPrice()
        return average_price + average_price * self.closeTH, average_price - average_price * self.closeTH

    def cancelOrder(self, order: Responses.Order) -> Responses.Order:
        return Responses.Order(self.client.LinearOrder.LinearOrder_cancel(symbol=self.symbol, order_id=order.order_id).result())

    def replaceOrder(self, order_id, price) -> Responses.Order:
        return Responses.Order(self.client.LinearOrder.LinearOrder_replace(symbol=self.symbol, order_id=order_id, p_r_price=price).result())