import talib
import numpy as np

# Exemplu simplu de utilizare a TA-Lib
close = np.random.random(100)
output = talib.SMA(close)
print(output)
