import logging
import pandas as pd
import numpy as np
import talib
from binance.client import Client
from utils.env_loader import BINANCE_API_KEY, BINANCE_SECRET_KEY
from utils.rate_limiter import RateLimiter
from database.db_manager import DatabaseManager
import time

logger = logging.getLogger(__name__)
db = DatabaseManager()

class OHLCVInitializer:
    def __init__(self, client, params, stablecoins):
        self.client = client
        self.params = params
        self.stablecoins = stablecoins
        self.logger = logger

    def initialize_ohlcv_data(self):
        """Inițializează tabela ohlcv cu date REST."""
        try:
            self.logger.info("Starting OHLCV data initialization...")
            start_time = time.time()
            with db.conn:
                cursor = db.conn.execute("SELECT COUNT(*) FROM ohlcv")
                count = cursor.fetchone()[0]
                self.logger.info(f"Current OHLCV row count: {count}")

            markets = self.client.get_exchange_info()["symbols"]
            pairs = []
            for m in markets:
                if m["status"] == "TRADING" and m["quoteAsset"] in self.stablecoins:
                    pairs.append(m["symbol"])

            self.logger.info(f"Found {len(pairs)} valid trading pairs")

            for pair in pairs:
                try:
                    klines = self.client.get_klines(symbol=pair, interval="5m", limit=100)
                    if len(klines) >= 50:
                        for k in klines:
                            timestamp = k[0]
                            o, h, l, c, v = map(float, k[1:6])
                            if all(x > 0 for x in [o, h, l, c, v]):
                                db.save_ohlcv(pair, timestamp, o, h, l, c, v)
                        self.logger.info(f"Updated OHLCV data for {pair}")
                except Exception as e:
                    self.logger.error(f"Error fetching data for {pair}: {str(e)}")
                    continue

            end_time = time.time()
            self.logger.info(f"OHLCV data initialization completed in {end_time - start_time:.2f} seconds")

        except Exception as e:
            self.logger.error(f"Failed to initialize OHLCV data: {str(e)}")
            raise

class IndicatorCalculator:
    def __init__(self, params):
        self.params = params
        self.logger = logger

    def calculate_indicators(self, df):
        """Calculează indicatorii tehnici pentru un DataFrame de date OHLCV."""
        try:
            df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
            df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
            df['EMA_fast'] = talib.EMA(df['close'], timeperiod=self.params['ema_fast'])
            df['EMA_slow'] = talib.EMA(df['close'], timeperiod=self.params['ema_slow'])
            df['RSI'] = talib.RSI(df['close'], timeperiod=14)
            macd, signal, _ = talib.MACD(
                df['close'],
                fastperiod=self.params['macd_fast'],
                slowperiod=self.params['macd_slow'],
                signalperiod=self.params['macd_signal']
            )
            df['MACD'] = macd
            return df
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {str(e)}")
            return df

    def should_trade(self, df):
        """Verifică dacă o tranzacție este validă pe baza indicatorilor."""
        if df is None or df.empty:
            return False, "No data available"
        last_row = df.iloc[-1]
        if pd.isna(last_row['ATR']) or last_row['ATR'] < self.params['volatility_threshold_low']:
            return False, "Volatilitate prea scăzută (ATR)"
        if pd.isna(last_row['ADX']) or last_row['ADX'] < 20:
            return False, "Trend prea slab (ADX)"
        if last_row['volume'] < self.params['min_volume']:
            return False, "Volum insuficient"
        return True, "Tranzacție validă"

class TradingFilters:
    def __init__(self, config):
        self.params = config["params"]
        self.stablecoins = config["stablecoins"]
        self.logger = logger
        self.logger.info("TradingFilters initialized with params: %s", self.params)
        self.client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
        
        self.logger.info("Creating OHLCVInitializer...")
        self.ohlcv_initializer = OHLCVInitializer(self.client, self.params, self.stablecoins)
        
        self.logger.info("Creating IndicatorCalculator...")
        self.indicator_calculator = IndicatorCalculator(self.params)
        
        self.logger.info("Starting OHLCV data initialization...")
        start_time = time.time()
        self.ohlcv_initializer.initialize_ohlcv_data()
        end_time = time.time()
        self.logger.info(f"OHLCV data initialization completed in {end_time - start_time:.2f} seconds")

    def detect_breakout(self, symbol):
        """Detectează un breakout pentru un simbol."""
        try:
            with db.conn:
                cursor = db.conn.execute(
                    "SELECT close, volume FROM ohlcv WHERE pair = ? ORDER BY timestamp DESC LIMIT 3",
                    (symbol,)
                )
                data = cursor.fetchall()
            if len(data) < 3:
                return False, 0.0
            df = pd.DataFrame(data, columns=['close', 'volume'])
            recent_high = df['close'].max()
            recent_low = df['close'].min()
            if recent_low <= 0:
                self.logger.warning(f"Recent low is {recent_low} for {symbol}, cannot calculate breakout")
                return False, 0.0
            price_change = ((recent_high - recent_low) / recent_low) * 100
            mean_volume = df['volume'].mean()
            current_volume_surge = df['volume'].iloc[-1] / mean_volume if mean_volume > 0 else 1.0
            is_breakout = price_change > 2.5 and current_volume_surge > 1.2
            return is_breakout, price_change
        except Exception as e:
            self.logger.error(f"Error detecting breakout for {symbol}: {str(e)}")
            return False, 0.0

    def calculate_opportunity_score(self, symbol):
        """Calculează un scor de oportunitate pentru un simbol."""
        try:
            with db.conn:
                cursor = db.conn.execute(
                    "SELECT open, high, low, close, volume FROM ohlcv WHERE pair = ? ORDER BY timestamp DESC LIMIT 50",
                    (symbol,)
                )
                data = cursor.fetchall()
            if len(data) < 50:
                self.logger.debug(f"Insufficient OHLCV data for {symbol}: {len(data)} rows")
                return 0.0

            df = pd.DataFrame(data, columns=['open', 'high', 'low', 'close', 'volume'])

            # Validare și curățare a datelor
            df = df.replace([np.inf, -np.inf], np.nan)
            df = df.dropna()

            if len(df) < 50:
                self.logger.debug(f"Insufficient valid OHLCV data for {symbol} after cleaning")
                return 0.0

            if df[['open', 'high', 'low', 'close']].le(0).any().any():
                self.logger.debug(f"Skipping {symbol} due to invalid price data")
                return 0.0

            self.logger.debug(f"Valid OHLCV data for {symbol}: {df.tail(5).to_string()}")

            df = self.indicator_calculator.calculate_indicators(df)
            if df.isnull().any().any():
                self.logger.debug(f"NaN values detected for {symbol}")
                return 0.0

            closes = df['close'].values[-5:]
            volumes = df['volume'].values[-5:]

            if len(closes) < 5 or len(volumes) < 5:
                return 0.0

            if any(x <= 0 for x in closes) or any(x <= 0 for x in volumes):
                self.logger.debug(f"Invalid price/volume data for {symbol}")
                return 0.0

            short_momentum = (closes[-1] / closes[-3] - 1) if closes[-3] > 0 else 0
            mean_volume = np.mean(volumes)
            volume_spike = volumes[-1] / mean_volume if mean_volume > 0 else 1.0
            is_breakout, breakout_strength = self.detect_breakout(symbol)

            rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50.0
            macd = float(df['MACD'].iloc[-1]) if not pd.isna(df['MACD'].iloc[-1]) else 0.0
            adx = float(df['ADX'].iloc[-1]) if not pd.isna(df['ADX'].iloc[-1]) else 20.0
            regime = "trending" if adx > 25 else "mean-reverting" if adx < 20 else "neutral"

            self.logger.debug(f"{symbol} indicators: RSI={rsi}, MACD={macd}, ADX={adx}")

            volume_score = min(volume_spike, 4.0) / 4.0 * 0.2
            momentum_score = min(abs(short_momentum) * 100, 1.0) * 0.3
            breakout_score = float(is_breakout) * breakout_strength / 10 * 0.4 if not pd.isna(breakout_strength) else 0.0
            volatility_score = min(df['ATR'].iloc[-1] / closes[-1] * 100, 1.0) if not pd.isna(df['ATR'].iloc[-1]) else 0.1

            total_score = volume_score + momentum_score + breakout_score + volatility_score
            total_score = min(total_score, 1.0) if not pd.isna(total_score) else 0.0

            self.logger.debug(f"{symbol}: Total Score={total_score}")
            try:
                db.conn.execute(
                    "INSERT INTO technical_analysis (symbol, rsi, macd, volume, regime, opportunity_score) VALUES (?, ?, ?, ?, ?, ?)",
                    (symbol, rsi, macd, volumes[-1], regime, total_score)
                )
                db.conn.commit()
            except Exception as e:
                self.logger.error(f"Error saving technical analysis for {symbol}: {str(e)}")
            return total_score
        except Exception as e:
            self.logger.error(f"Error calculating opportunity score for {symbol}: {str(e)}")
            return 0.0

    def adaptive_strategy(self, symbol):
        """Aplică o strategie adaptivă pentru un simbol."""
        try:
            with db.conn:
                cursor = db.conn.execute(
                    "SELECT close FROM ohlcv WHERE pair = ? ORDER BY timestamp DESC LIMIT 50",
                    (symbol,)
                )
                data = [float(row[0]) for row in cursor.fetchall()]
            if len(data) < 50 or any(x <= 0 for x in data):
                return False
            ema_fast = talib.EMA(np.array(data), timeperiod=self.params["ema_fast"])[-1]
            ema_slow = talib.EMA(np.array(data), timeperiod=self.params["ema_slow"])[-1]
            rsi = talib.RSI(np.array(data))[-1]
            return ema_fast > ema_slow and rsi < 75
        except Exception as e:
            self.logger.error(f"Error in adaptive strategy for {symbol}: {str(e)}")
            return False

    def calculate_volatility(self, symbol):
        """Calculează volatilitatea pentru un simbol."""
        try:
            klines = self.client.get_klines(symbol=symbol.replace('/', ''), interval='1h', limit=24)
            if len(klines) < 2:
                logger.warning(f"Insufficient klines data for {symbol}")
                return 0.01
            closes = [float(k[4]) for k in klines]
            returns = np.diff(np.log(closes))
            volatility = np.std(returns, ddof=1) * np.sqrt(24)
            return max(volatility, 0.01)
        except Exception as e:
            logger.error(f"Error calculating volatility for {symbol}: {str(e)}")
            return 0.01

    def filter_pairs(self):
        """Filtrează perechile de tranzacționare pe baza indicatorilor."""
        self.logger.info("Starting filter_pairs process")
        try:
            ticker_data = self.client.get_all_tickers() if self.client else []
            if not ticker_data:
                self.logger.warning("No ticker data available")
                return []
            self.logger.info(f"Retrieved {len(ticker_data)} tickers from Binance")

            filtered_pairs = []
            for ticker in ticker_data:
                pair = ticker["symbol"]
                if not any(pair.endswith(sc) for sc in self.stablecoins):
                    self.logger.debug(f"Skipping {pair} - not a stablecoin pair")
                    continue

                with db.conn:
                    cursor = db.conn.execute(
                        "SELECT open, high, low, close, volume FROM ohlcv WHERE pair = ? ORDER BY timestamp DESC LIMIT 50",
                        (pair,)
                    )
                    data = cursor.fetchall()
                if len(data) < 50:
                    self.logger.debug(f"Skipping {pair} - insufficient OHLCV data ({len(data)} rows)")
                    continue

                df = pd.DataFrame(data, columns=['open', 'high', 'low', 'close', 'volume'])
                df = self.indicator_calculator.calculate_indicators(df)
                should_trade, reason = self.indicator_calculator.should_trade(df)
                opportunity_score = self.calculate_opportunity_score(pair)
                self.logger.debug(f"{pair}: should_trade={should_trade} ({reason}), opportunity_score={opportunity_score}")

                if opportunity_score > 0.1:  # Prag relaxat
                    filtered_pairs.append(pair)
                    self.logger.info(f"Added {pair} to filtered pairs")

            self.logger.info(f"Completed filter_pairs: {len(filtered_pairs)} pairs filtered")
            return filtered_pairs
        except Exception as e:
            self.logger.error(f"Error in filter_pairs: {str(e)}")
            return []