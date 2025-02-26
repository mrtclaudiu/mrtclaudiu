import pandas as pd
import talib
import logging
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)
db = DatabaseManager()

class TradingStrategy:
    def __init__(self, params):
        self.short_period = params.get("short_period", 10)
        self.long_period = params.get("long_period", 50)
        self.logger = logger

    def sma_crossover(self, pair):
        try:
            with db.conn:
                cursor = db.conn.execute(
                    "SELECT close FROM ohlcv WHERE pair = ? ORDER BY timestamp DESC LIMIT ?",
                    (pair, self.long_period)
                )
                prices = [float(row[0]) for row in cursor.fetchall()]
            if len(prices) < self.long_period:
                return None
            df = pd.DataFrame(prices, columns=["close"])
            short_sma = talib.SMA(df["close"], timeperiod=self.short_period).iloc[-1]
            long_sma = talib.SMA(df["close"], timeperiod=self.long_period).iloc[-1]
            prev_short_sma = talib.SMA(df["close"], timeperiod=self.short_period).iloc[-2]
            prev_long_sma = talib.SMA(df["close"], timeperiod=self.long_period).iloc[-2]

            if short_sma > long_sma and prev_short_sma <= prev_long_sma:
                self.logger.info(f"Buy signal for {pair}")
                return "buy"
            elif short_sma < long_sma and prev_short_sma >= prev_long_sma:
                self.logger.info(f"Sell signal for {pair}")
                return "sell"
            return None
        except Exception as e:
            self.logger.error(f"Error in sma_crossover for {pair}: {str(e)}")
            return None