from derivativesTrader import DerivativesTrader
import Responses
from typing import NamedTuple

class Account(NamedTuple):
    buyOrder: Responses.OrderWithStatus = None
    sellOrder: Responses.OrderWithStatus = None

class Params(NamedTuple):
    openTH: float
    closeTH: float
    qty: float
    orderCount: int
    qtyWeight: float
    THWeight: float

class Spread(NamedTuple):
    open_buyPrice: float = 0
    open_sellPrice: float = 0
    close_buyPrice: float = 0
    close_sellPrice: float = 0

class DerivativesStrategy:

    def __init__(self, api_key, api_secret, symbol, openTH, closeTH, qtyWeight, THWeight) -> None:
        self.trader: DerivativesTrader = DerivativesStrategy.__createTrader(api_key, api_secret, symbol)
        self.params = Params(openTH=openTH, closeTH=closeTH, 
                             qty=self.trader.symbol.QTYSTEP, 
                             qtyWeight=qtyWeight, THWeight=THWeight, 
                             orderCount=0)
        self.account = Account()
        self.spread = Spread()

    def __createTrader(api_key, api_secret, symbol) -> DerivativesTrader:
        return DerivativesTrader(api_key, api_secret, symbol)

    def updateSpread(self):
        average_price = self.trader.getAvgPrice()

        upper_spread = (lambda avg, threshold, count: avg * (1 + threshold) ** count)
        lower_spread = (lambda avg, threshold, count: avg * (1 - threshold) ** count)

        self.spread.open_buyPrice = upper_spread(average_price, self.params.openTH, self.params.orderCount)
        self.spread.open_sellPrice = lower_spread(average_price, self.params.openTH, self.params.orderCount)

        self.spread.close_buyPrice = lower_spread(average_price, self.params.openTH, self.params.orderCount)
        self.spread.close_sellPrice = upper_spread(average_price, self.params.openTH, self.params.orderCount)

    def buy(self):
        self.updateSpread()
        self.account.buyOrder = self.trader.placeOrder(side='Buy', qty=self.params.qty, price=self.spread.open_buyPrice)

    def sell(self):
        self.updateSpread()
        self.account.sellOrder = self.trader.placeOrder(side='Sell', qty=self.params.qty, price=self.spread.open_sellPrice)

    def close_buy(self):
        self.updateSpread()
        self.trader.setTradingStop(side='Buy', price=self.spread.close_buyPrice)

    def close_sell(self):
        self.updateSpread()
        self.trader.setTradingStop(side='Sell', price=self.spread.close_sellPrice)
    
    def cancelBuy(self):
        self.trader.cancelOrder(self.account.buyOrder)

    def cancelSell(self):
        self.trader.cancelOrder(self.account.sellOrder)

    def onBuyOrderFilled(self):
        self.params.orderCount += 1
        self.close_buy()
        self.cancelSell()
        self.buy()

        while True:
            if self.buyOrderFilled():
                self.onBuyOrderFilled()
                break
            elif self.trader.hasPosition == False:
                print('Closed')
                break
            else:
                self.refreshBuyOrder()
                self.close_buy()
        print('Trading Completed')

    def onSellOrderFilled(self):
        self.params.orderCount += 1
        self.close_sell()
        self.cancelBuy()
        self.sell()

        while True:
            if self.sellOrderFilled():
                self.onSellOrderFilled()
                break
            elif self.trader.hasPosition == False:
                print('Closed')
                break
            else:
                self.refreshSellOrder()
                self.close_sell()
        print('Trading Completed')

    def buyOrderFilled(self):
        if self.trader.queryOrder(self.account.buyOrder).order_status == 'Filled':
            return True
        else:
            return False

    def sellOrderFilled(self):
        if self.trader.queryOrder(self.account.sellOrder).order_status == 'Filled':
            return True
        else:
            return False

    def refreshBuyOrder(self):
        pass

    def refreshSellOrder(self):
        pass

class MyStrategy(DerivativesStrategy):
    
    def __init__(self, api_key, api_secret, symbol, openTH, closeTH, qtyWeight, THWeight) -> None:
        super().__init__(api_key, api_secret, symbol, openTH, closeTH, qtyWeight, THWeight)

    def startTrade(self) -> int:
        if self.trader.hasPosition():
            return -1
        
        self.buy()
        self.sell()

        #어느 한 쪽의 주문이 체결될 때까지 대기
        while True:
            if self.buyOrderFilled():
                self.onBuyOrderFilled()
                break

            elif self.sellOrderFilled():
                self.onSellOrderFilled()
                break

            else:
                self.refreshBuyOrder()
                self.refreshSellOrder()