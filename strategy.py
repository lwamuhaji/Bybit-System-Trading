from DerivativesTrader import DerivativesTrader
import time

class Strategy:

    def __init__(self) -> None:
        self.__createTrader()
        self.__orderCount = 0
        self.__openTH = self.trader.openTH
        self.__closeTH = self.trader.closeTH

    def __createTrader(self) -> None:
        self.trader = DerivativesTrader(api_key="MdojZrGYvNXsXf8sxp", 
                                        api_secret="jLNEDFu2CGJip7h8UlheZVDX1yMI20V8L6LW", 
                                        symbol='EOSUSDT', 
                                        openTH=0.01, 
                                        closeTH=0.0003, 
                                        interval='1', 
                                        limit=99, 
                                        openWeight=1.5, 
                                        closeWeight=1.5)

    def checkBeforeStart(self) -> None:
        for position in self.trader.getPositions().result:
            if position['size'] > 0:
                raise Exception('You already have positions')

    def __initValues(self):
        self.qty = self.trader.getQtyStep()
        self.price = self.trader.getTickSize()

    def start(self):
        self.checkBeforeStart()
        self.__initValues()
        print('Start trading')
        self.__start()

    def onOrderExecuted(self, side):
        self.updateTH()
        if side=='Buy':
            self.onLongExecuted()
        elif side=='Sell':
            self.onShortExecuted()
    
    def updateTH(self):
        self.trader.openTH *= self.trader._openWeight
        if self.__orderCount != 0:
            self.trader.closeTH *= self.trader._closeWeight
        self.__orderCount += 1

    def onLongExecuted(self):
        self.longOrder = self.placeOrder('Buy')
        if self.shortOrder != None:
            self.trader.cancelOrder(self.shortOrder.order_id)
        self.shortOrder = None

    def onShortExecuted(self):
        self.shortOrder = self.placeOrder('Sell')
        if self.longOrder != None:
            self.trader.cancelOrder(self.longOrder.order_id)
        self.longOrder = None

    def updateQty(self):
        pass

    def updateOpenPrice(self):
        return self.trader.getOpenSpread()

    def placeOrder(self, side):
        top, bottom = self.updateOpenPrice()
        top, bottom = round(top,3), round(bottom, 3)
        price = bottom if side=='Buy' else top
        return self.trader.placeOrder(side=side, qty=self.qty, price=price)

    def replaceOrder(self, side):
        top, bottom = self.updateOpenPrice()
        top, bottom = round(top,3), round(bottom, 3)
        price = bottom if side=='Buy' else top
        order = self.longOrder if side=='Buy' else self.shortOrder
        return self.trader.replaceOrder(order_id=order.order_id, price=price)

    def isOrderExcuted(self):
        L, S = None, None
        if self.longOrder != None:
            L = self.trader.queryOrder(self.longOrder).order_status
        if self.shortOrder != None:
            S = self.trader.queryOrder(self.shortOrder).order_status
        if L == 'Filled':
            return 'Buy'
        if S == 'Filled':
            return 'Sell'
        return False

    def hasPosition(self):
        positions = self.trader.getPositions()
        if positions.longPosition['size'] > 0:
            return 'Buy'
        elif positions.shortPosition['size'] > 0:
            return 'Sell'
        else:
            return False

    def updateClosePrice(self):
        return self.trader.getCloseSpread()

    def closePosition(self, side):
        top, bottom = self.updateClosePrice()
        top, bottom = round(top,3), round(bottom, 3)
        price = bottom if side=='Buy' else top
        self.trader.setTradingStop(side, price)

    def resetAll(self):
        self.__orderCount = 0
        self.trader.openTH = self.__openTH
        self.trader.closeTH = self.__closeTH

    def updateOrders(self):
        L, S = None, None
        if self.longOrder != None:
            L = self.trader.queryOrder(self.longOrder).order_status
        if self.shortOrder != None:
            S = self.trader.queryOrder(self.shortOrder).order_status
        if L == 'New':
            self.replaceOrder('Buy')
        if S == 'New':
            self.replaceOrder('Sell')
            

    def __start(self):
        self.longOrder = self.placeOrder(side='Buy')
        self.shortOrder = self.placeOrder(side='Sell')

        while True:
            time.sleep(0.5)
            order_flag = self.isOrderExcuted()
            if order_flag:
                self.onOrderExecuted(order_flag)

            time.sleep(0.5)
            position_flag = self.hasPosition()
            if position_flag:
                self.closePosition(position_flag)
            elif position_flag == False and self.__orderCount > 0:
                raise Exception('end')

            time.sleep(0.5)
            self.updateOrders()
