from derivativesTrader import DerivativesTrader
import Responses

class Account:
    def __init__(self, buyOrder=None, sellOrder=None) -> None:
        self.buyOrder: Responses.Order = buyOrder
        self.sellOrder: Responses.Order = sellOrder

class Params:
    def __init__(self, openTH, closeTH, qtyStep, qtyWeight, THWeight, orderCount) -> None:
        self.openTH = openTH
        self.closeTH = closeTH
        self.qtyStep = qtyStep
        self.qtyWeight = qtyWeight
        self.THWeight = THWeight
        self.orderCount = orderCount

class Spread:
    def __init__(self, open_buyPrice=None, open_sellPrice=None, close_buyPrice=None, close_sellPrice=None, qty=None) -> None:
        self.open_buyPrice: float = open_buyPrice
        self.open_sellPrice: float = open_sellPrice
        self.close_buyPrice: float = close_buyPrice
        self.close_sellPrice: float = close_sellPrice
        self.qty: float = qty

class DerivativesStrategy:

    def __init__(self, api_key, api_secret, symbol, openTH, closeTH, qtyWeight, THWeight, limit, interval) -> None:
        self.trader: DerivativesTrader = DerivativesStrategy.__createTrader(api_key=api_key, api_secret=api_secret, symbol=symbol, limit=limit, interval=interval)
        self.params = Params(openTH=openTH, closeTH=closeTH, 
                             qtyStep=self.trader.symbol.QTYSTEP,
                             qtyWeight=qtyWeight, THWeight=THWeight, 
                             orderCount=0)
        self.account = Account()
        self.spread = Spread()

    def __createTrader(api_key, api_secret, symbol, limit, interval) -> DerivativesTrader:
        return DerivativesTrader(api_key, api_secret, symbol, limit, interval)

    def updateSpread(self):
        self.spread.qty = self.params.qtyStep * 2 ** self.params.orderCount

        average_price = self.trader.getAvgPrice()

        upper_spread = (lambda avg, threshold, count: round(avg * (1 + threshold) ** count), 3)
        lower_spread = (lambda avg, threshold, count: round(avg * (1 - threshold) ** count), 3)

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
        old_open_buyPrice = self.spread.open_buyPrice
        self.updateSpread()
        if self.spread.open_buyPrice == old_open_buyPrice:
            return
        else:
            self.trader.replaceOrder(self.account.buyOrder, self.spread.open_buyPrice)

    def refreshSellOrder(self):
        old_open_sellPrice = self.spread.open_sellPrice
        self.updateSpread()
        if self.spread.open_sellPrice == old_open_sellPrice:
            return
        else:
            self.trader.replaceOrder(self.account.buyOrder, self.spread.open_buyPrice)

class MyStrategy(DerivativesStrategy):
    
    def __init__(self, api_key, api_secret, symbol, openTH, closeTH, qtyWeight, THWeight, limit, interval) -> None:
        super().__init__(api_key, api_secret, symbol, openTH, closeTH, qtyWeight, THWeight, limit, interval)

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