import bybit
import math
from datetime import datetime
import time
import os
from IPython.display import clear_output

from DerivativesTrader import DerivativesTrader
import Responses

trader = DerivativesTrader(api_key="MdojZrGYvNXsXf8sxp", api_secret="jLNEDFu2CGJip7h8UlheZVDX1yMI20V8L6LW", symbol='ETHUSDT')
trader.start()