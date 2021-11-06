class BybitResponse:
    def __init__(self, response) -> None:
        self.response = response
        self.__getValues()
        self.__isSuccessful()

    def __getValues(self):
        self.body = self.response[0]
        self.ret_code = self.body['ret_code']
        self.ext_code = self.body['ext_code']
        self.ret_msg = self.body['ret_msg']
        self.result = self.body['result']
    
    def __isSuccessful(self):
        if self.ret_code == 0 and self.ext_code == '':
            pass
        else:
            raise Exception("Invalid Response", self.ret_code, self.ext_code, self.ret_msg)

class Symbols(BybitResponse):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.__parse()

    def __parse(self):
        pass

class Positions(BybitResponse):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.__parse()

    def __parse(self):
        self.longPosition = self.result[0]
        self.shortPosition = self.result[1]
        if self.longPosition['side'] != 'Buy' or self.shortPosition['side'] != 'Sell':
            raise Exception()

class Candles(BybitResponse):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.__parse()

    def __parse(self):
        pass

class TradingRecord(BybitResponse):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.__parse()

    def __parse(self):
        self.last = self.result[0]

class ServerTime(BybitResponse):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.__parse()
    
    def __parse(self):
        self.time = self.body['time_now']

class TradingStop(BybitResponse):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.__parse()

    def __parse(self):
        pass

class Order(BybitResponse):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.__parse()

    def __parse(self):
        self.order_id = self.result['order_id']

class OrderWithStatus(Order):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.__parse()

    def __parse(self):
        self.order_status = self.result['order_status']

class OrderList(BybitResponse):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.__parse()

    def __parse(self):
        pass