    def _getServerTime(self) -> float:
        response = Responses.ServerTime(self._client.Common.Common_getTime().result())
        return float(response.time)