import sys
import os
import json
import logging
import threading
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from binance.client import Client
from utils.env_loader import BINANCE_API_KEY, BINANCE_SECRET_KEY
from utils.telegram_notifier import TelegramNotifier
from utils.recovery import RecoverySystem
from utils.rate_limiter import RateLimiter
from database.db_manager import DatabaseManager
from trading.trading_filter import TradingFilters
from trading.strategy import TradingStrategy
from trading.risk_manager import RiskManager
from trading.order_manager import OrderManager
from monitoring.balance_monitor import BalanceMonitor
from monitoring.health_monitor import HealthMonitor
from websocket.websocket_manager import WebSocketManager

# Configure advanced logging
script_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(script_dir, "logs"), exist_ok=True)
logger = logging.getLogger(__name__)
logger.handlers.clear()
logger.setLevel(logging.INFO)

# Handler for log file
file_handler = RotatingFileHandler(
    os.path.join(script_dir, "logs", "trade_log.txt"),
    maxBytes=10000,
    backupCount=5
)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Handler for console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Load configuration
config_path = os.path.join(script_dir, "config.json")
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

db_lock = threading.Lock()

# Initialize Binance client
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

# Get rate limits from exchangeInfo
exchange_info = client.get_exchange_info()
rate_limits = exchange_info['rateLimits']

rate_limiter = RateLimiter(rate_limits)
db_manager = DatabaseManager()

class BotLauncher:
    def __init__(self, config):
        try:
            logger.info("Starting BotLauncher initialization...")
            if not config:
                raise ValueError("Config is empty or invalid")
            self.config = config
            logger.info("Loading configuration parameters...")
            self.params = config.get("params", {})
            if not self.params:
                raise ValueError("No parameters found in config")
            self.stablecoins = config.get("stablecoins", ["USDT"])
            logger.info(f"Configured stablecoins: {self.stablecoins}")

            self.lock = threading.Lock()
            self.open_positions = []
            self.market_cache = {}
            self.last_market_update = None

            # Initialize components
            logger.info("Initializing TradingFilters...")
            start_time = time.time()
            self.filters = TradingFilters(config)
            end_time = time.time()
            logger.info(f"TradingFilters initialized in {end_time - start_time:.2f} seconds")

            logger.info("Getting trading pairs...")
            self.pairs = self.filters.filter_pairs()
            logger.info(f"Successfully filtered {len(self.pairs)} trading pairs")
            if not self.pairs:
                logger.error("No pairs filtered. Check OHLCV database and filter criteria.")
                with db_lock:
                    with db_manager.conn:
                        cursor = db_manager.conn.execute("SELECT COUNT(*) FROM ohlcv")
                        count = cursor.fetchone()[0]
                        logger.error(f"OHLCV database contains {count} rows")

            # Initialize HealthMonitor and BalanceMonitor
            self.health_monitor = HealthMonitor()
            self.balance_monitor = BalanceMonitor()
            logger.info("HealthMonitor and BalanceMonitor initialized")

            # Initialize other components
            self.strategy = TradingStrategy(self.params)
            logger.info("TradingStrategy initialized")
            self.risk_manager = RiskManager(self.params)
            logger.info("RiskManager initialized")
            self.order_manager = OrderManager(self.risk_manager)
            logger.info("OrderManager initialized")
            self.recovery = RecoverySystem()
            logger.info("RecoverySystem initialized")
            self.telegram = TelegramNotifier()
            logger.info("TelegramNotifier initialized")
            self.websocket_manager = WebSocketManager(self.pairs)
            logger.info("WebSocketManager initialized")

            # Load open positions
            self.load_open_positions()
            logger.info("BotLauncher initialization completed")

        except Exception as e:
            logger.exception(f"An error occurred during BotLauncher initialization: {e}")
            raise

    def load_open_positions(self):
        """Load open positions from the database."""
        with db_lock:
            self.open_positions = db_manager.load_positions()
        logger.info(f"Loaded {len(self.open_positions)} open positions")

    def monitor_balance(self):
        """Monitor the Binance account balance."""
        while True:
            try:
                rate_limiter.execute_with_rate_limit(lambda: client.get_asset_balance(asset="USDT"), weight=1)
                balance = float(client.get_asset_balance(asset="USDT")["free"])
                logger.info(f"Current balance: {balance} USDT")
                self.telegram.notify_balance_update(balance)
            except Exception as e:
                logger.error(f"Error monitoring balance: {str(e)}")
            time.sleep(300)  # Check every 5 minutes

    def trade_loop(self):
        """Scan trading pairs for opportunities."""
        while True:
            try:
                logger.info(f"Scanning {len(self.pairs)} pairs for opportunities")
                for pair in self.pairs:
                    signal = self.strategy.sma_crossover(pair)
                    if signal:
                        rate_limiter.execute_with_rate_limit(lambda: client.get_asset_balance(asset="USDT"), weight=1)
                        balance = float(client.get_asset_balance(asset="USDT")["free"])
                        profit = self.order_manager.execute_trade(pair, signal, balance)
                        if profit:
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                            with db_lock:
                                positions = db_manager.load_positions()
                            entry_price = next((pos["entry_price"] for pos in positions if pos["symbol"] == pair), 0)
                            exit_price = profit / next((pos["amount"] for pos in positions if pos["symbol"] == pair), 1) + entry_price
                            with db_lock:
                                db_manager.save_trade(pair, entry_price, exit_price, profit, timestamp)
                                db_manager.update_performance(pair, profit, profit > 0)
            except Exception as e:
                logger.error(f"Error in trade loop: {str(e)}")
            time.sleep(60)

    def adjust_volatility_threshold(self):
        """Adjust the volatility threshold based on BTC volatility."""
        try:
            btc_volatility = self.filters.calculate_volatility("BTC/USDT")
            current_threshold = self.params.get("volatility_threshold", 0.02)
            if btc_volatility > self.params["volatility_high"]:
                target_threshold = self.params["volatility_threshold_high"]
            elif btc_volatility < self.params["volatility_low"]:
                target_threshold = self.params["volatility_threshold_low"]
            else:
                target_threshold = (self.params["volatility_threshold_high"] + self.params["volatility_threshold_low"]) / 2
            self.params["volatility_threshold"] = current_threshold + (target_threshold - current_threshold) * 0.2
            logger.info(f"Adjusted volatility threshold to {self.params['volatility_threshold']:.4f}")
        except Exception as e:
            logger.error(f"Error adjusting volatility threshold: {str(e)}")

    def run(self):
        """Start the bot and all components."""
        try:
            # Notify bot start
            self.telegram.notify_bot_start()

            # Validate and recover positions
            self.recovery.validate_and_recover_positions()

            # Check if trading pairs exist
            if not self.pairs:
                logger.error("No pairs available to start WebSocket. Check filter_pairs output and database.")
                self.stop()
                return

            # Start WebSocketManager
            self.websocket_manager.start(self.pairs)

            # Start monitoring threads
            health_thread = threading.Thread(target=self.health_monitor.check_health, daemon=True)
            balance_thread = threading.Thread(target=self.balance_monitor.monitor_balance, daemon=True)
            health_thread.start()
            balance_thread.start()
            logger.info("Started HealthMonitor and BalanceMonitor threads")

            # Check if threads are running
            if health_thread.is_alive():
                logger.info("HealthMonitor thread is running")
            else:
                logger.error("HealthMonitor thread failed to start")

            if balance_thread.is_alive():
                logger.info("BalanceMonitor thread is running")
            else:
                logger.error("BalanceMonitor thread failed to start")

            # Main bot loop
            while True:
                try:
                    logger.info(f"Starting new iteration at {datetime.now(timezone.utc).isoformat()}")

                    # Adjust volatility threshold
                    self.adjust_volatility_threshold()

                    # Update market cache
                    self.cache_markets()

                    # Check portfolio risk
                    self.risk_management_check()

                    # Manage underperforming positions
                    self.manage_underperforming_positions()

                    # Get current balance
                    rate_limiter.execute_with_rate_limit(lambda: client.get_asset_balance(asset="USDT"), weight=1)
                    balance = float(client.get_asset_balance(asset="USDT")["free"])
                    portfolio_value = balance
                    logger.info(f"Current portfolio value: {portfolio_value} USDT")

                    # Check if there are sufficient funds
                    if portfolio_value < 15:
                        logger.warning("Insufficient funds. Waiting...")
                        time.sleep(self.params.get("refresh_interval", 10))
                        continue

                    # Scan pairs for opportunities
                    opportunities = self.scan_opportunities()
                    if not opportunities:
                        logger.info("No opportunities found this iteration")
                        time.sleep(self.params.get("refresh_interval", 10))
                        continue

                    # Process opportunities
                    self.process_opportunities(opportunities)

                    # Wait before next iteration
                    time.sleep(self.params.get("refresh_interval", 10))

                except KeyboardInterrupt:
                    logger.info("Session terminated by user")
                    self.stop()
                    break
                except Exception as e:
                    logger.exception(f"Non-critical error in run loop: {str(e)}")
                    time.sleep(10)

        except Exception as e:
            logger.exception(f"Fatal error in run method: {e}")
            self.stop()

    def stop(self):
        """Stop the bot and all components."""
        try:
            logger.info("Stopping HealthMonitor...")
            if hasattr(self.health_monitor, 'stop'):
                self.health_monitor.stop()
            else:
                logger.error("HealthMonitor does not have a stop method")
        except Exception as e:
            logger.error(f"Error stopping HealthMonitor: {e}")

        try:
            logger.info("Stopping BalanceMonitor...")
            if hasattr(self.balance_monitor, 'stop'):
                self.balance_monitor.stop()
            else:
                logger.error("BalanceMonitor does not have a stop method")
        except Exception as e:
            logger.error(f"Error stopping BalanceMonitor: {e}")

        try:
            logger.info("Stopping WebSocketManager...")
            self.websocket_manager.stop()
        except Exception as e:
            logger.error(f"Error stopping WebSocketManager: {e}")

        try:
            logger.info("Notifying bot stop...")
            self.telegram.notify_bot_stop()
        except Exception as e:
            logger.error(f"Error notifying bot stop: {e}")

        logger.info("Bot stopped")

    def cache_markets(self):
        """Update market cache."""
        try:
            if not self.last_market_update or (datetime.now(timezone.utc) - self.last_market_update).seconds > self.params.get("min_cache_update_interval", 60):
                markets = client.get_exchange_info()["symbols"]
                self.market_cache = {
                    m["symbol"]: m for m in markets 
                    if m["status"] == "TRADING" and m["quoteAsset"] in self.stablecoins
                }
                self.last_market_update = datetime.now(timezone.utc)
                logger.info(f"Market cache updated: {len(self.market_cache)} symbols")
        except Exception as e:
            logger.error(f"Error updating market cache: {str(e)}")

    def dynamic_position_sizing(self, symbol, portfolio_value):
        """Calculate position size based on volatility and risk."""
        try:
            volatility = self.filters.calculate_volatility(symbol)
            risk_factor = min(0.05 / volatility, 0.1) if volatility else 0.05
            position_size = portfolio_value * risk_factor
            return max(position_size, self.params.get("default_trade_amount", 15))
        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {str(e)}")
            return self.params.get("default_trade_amount", 15)

    def risk_management_check(self):
        """Check portfolio risk and close positions if necessary."""
        try:
            with db_lock:
                portfolio_value = float(client.get_asset_balance(asset="USDT")["free"])
            total_risk = 0
            for pos in self.open_positions:
                current_price = self.order_manager.get_current_price(pos["symbol"])
                if current_price:
                    position_value = pos["amount"] * current_price
                    price_risk = abs(current_price - pos["entry_price"]) / pos["entry_price"]
                    total_risk += position_value * price_risk

            risk_percentage = (total_risk / portfolio_value) * 100 if portfolio_value > 0 else 0
            if risk_percentage > self.params.get("max_portfolio_risk", 0.1) * 100:
                logger.warning(f"Risk exceeded: {risk_percentage:.2f}%")
                self.close_all_positions()
        except Exception as e:
            logger.error(f"Error in risk management check: {str(e)}")

    def manage_underperforming_positions(self):
        """Close underperforming positions."""
        try:
            for pos in self.open_positions[:]:
                current_price = self.order_manager.get_current_price(pos["symbol"])
                if current_price and (current_price - pos["entry_price"]) / pos["entry_price"] < -0.05:
                    self.order_manager.close_position(pos)
        except Exception as e:
            logger.error(f"Error managing underperforming positions: {str(e)}")

    def close_all_positions(self):
        """Close all open positions."""
        try:
            with self.lock:
                for pos in self.open_positions[:]:
                    self.order_manager.close_position(pos)
        except Exception as e:
            logger.error(f"Error closing all positions: {str(e)}")

    def scan_opportunities(self):
        """Scan for trading opportunities."""
        opportunities = []
        for pair in self.pairs:
            signal = self.strategy.sma_crossover(pair)
            if signal:
                opportunities.append((pair, signal))
        return opportunities

    def process_opportunities(self, opportunities):
        """Process trading opportunities."""
        for pair, signal in opportunities:
            rate_limiter.execute_with_rate_limit(lambda: client.get_asset_balance(asset="USDT"), weight=1)
            balance = float(client.get_asset_balance(asset="USDT")["free"])
            position_size = self.dynamic_position_sizing(pair, balance)
            profit = self.order_manager.execute_trade(pair, signal, position_size)
            if profit:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                with db_lock:
                    positions = db_manager.load_positions()
                entry_price = next((pos["entry_price"] for pos in positions if pos["symbol"] == pair), 0)
                exit_price = profit / next((pos["amount"] for pos in positions if pos["symbol"] == pair), 1) + entry_price
                with db_lock:
                    db_manager.save_trade(pair, entry_price, exit_price, profit, timestamp)
                    db_manager.update_performance(pair, profit, profit > 0)

def main():
    bot = None
    try:
        logger.info("Starting Advanced Trading Bot...")
        logger.info("Initializing BotLauncher...")
        bot = BotLauncher(config)
        logger.info("BotLauncher initialized successfully")
        logger.info("Starting bot.run()...")
        bot.run()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        if bot:
            bot.stop()
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}")
        logger.exception("Full error traceback:")
        if bot:
            try:
                bot.stop()
            except:
                pass
        sys.exit(1)

if __name__ == "__main__":
    main()