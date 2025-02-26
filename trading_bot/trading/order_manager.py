from binance.client import Client
from utils.env_loader import BINANCE_API_KEY, BINANCE_SECRET_KEY
from utils.rate_limiter import RateLimiter
from utils.telegram_notifier import TelegramNotifier
from database.db_manager import DatabaseManager
import logging
import time

logger = logging.getLogger(__name__)
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

# Obține limitele de rată din exchangeInfo
exchange_info = client.get_exchange_info()
rate_limits = exchange_info['rateLimits']

limiter = RateLimiter(rate_limits)
db = DatabaseManager()

class OrderManager:
    def __init__(self, risk_manager):
        self.risk_manager = risk_manager
        self.telegram = TelegramNotifier()

    def place_market_order(self, pair, side, quantity):
        """Plasează un ordin de tip market."""
        try:
            order_func = lambda: client.create_order(
                symbol=pair,
                side=side.upper(),
                type="MARKET",
                quantity=quantity
            )
            order = limiter.execute_with_rate_limit(order_func, weight=1)
            logger.info(f"Placed {side} market order for {pair}: {quantity}")
            self._check_rate_limits(order)
            return order
        except Exception as e:
            logger.error(f"Error placing market order for {pair}: {str(e)}")
            raise

    def place_oco_order(self, pair, quantity, price, stop_price):
        """Plasează un ordin OCO (One Cancels the Other)."""
        try:
            order_func = lambda: client.create_oco_order(
                symbol=pair,
                side="SELL",
                quantity=quantity,
                price=str(price),
                stopPrice=str(stop_price),
                stopLimitPrice=str(stop_price * 0.99),
                stopLimitTimeInForce="GTC"
            )
            order = limiter.execute_with_rate_limit(order_func, weight=1)
            logger.info(f"OCO order placed for {pair}: TP {price}, SL {stop_price}")
            self.telegram.sync_send_message(f"OCO order for {pair}: TP {price}, SL {stop_price}")
            self._check_rate_limits(order)
            return order
        except Exception as e:
            logger.error(f"Error placing OCO order for {pair}: {str(e)}")
            raise

    def execute_trade(self, pair, signal, balance):
        """Execută o tranzacție pe baza semnalului primit."""
        try:
            limiter.wait()
            price = float(client.get_symbol_ticker(symbol=pair)["price"])
            quantity = self.risk_manager.calculate_quantity(balance, price)

            if signal == "buy":
                order = self.place_market_order(pair, "buy", quantity)
                entry_price = float(order["fills"][0]["price"])
                order_id = order["orderId"]
                position = {
                    "symbol": pair,
                    "amount": quantity,
                    "entry_price": entry_price,
                    "order_id": str(order_id),
                    "risk": self.risk_manager.stop_loss
                }
                db.save_position(position)
                self.telegram.notify_position_opened(pair, quantity, entry_price)
                tp_price = entry_price * (1 + self.risk_manager.take_profit)
                sl_price = entry_price * (1 - self.risk_manager.stop_loss)
                self.place_oco_order(pair, quantity, tp_price, sl_price)
                return None
            elif signal == "sell":
                positions = db.load_positions()
                for pos in positions:
                    if pos["symbol"] == pair:
                        order = self.place_market_order(pair, "sell", pos["amount"])
                        exit_price = float(order["fills"][0]["price"])
                        profit = (exit_price - pos["entry_price"]) * pos["amount"]
                        db.remove_position(pos["order_id"])
                        self.telegram.notify_position_closed(pair, pos["amount"], exit_price, profit)
                        return profit
            return None
        except Exception as e:
            logger.error(f"Error executing trade for {pair}: {str(e)}")
            return None

    def execute_smart_order(self, symbol, side, amount):
        """Plasează un ordin smart cu verificare slipaj și precizie."""
        try:
            book = client.get_order_book(symbol=symbol)
            best_ask = float(book["asks"][0][0])
            best_bid = float(book["bids"][0][0])
            price = best_ask * 1.005 if side == "buy" else best_bid * 0.995
            notional_value = price * amount
            if notional_value < 15:
                amount = 15 / price
            elif notional_value > 20:
                amount = 20 / price

            # Rotunjim cantitatea la precizia perechii
            symbol_info = next((s for s in client.get_exchange_info()["symbols"] if s["symbol"] == symbol), None)
            if not symbol_info:
                raise ValueError(f"Symbol info not found for {symbol}")

            qty_precision = int(symbol_info.get('baseAssetPrecision', 8))
            price_precision = int(symbol_info.get('quotePrecision', 8))

            amount = round(amount, qty_precision)
            price = round(price, price_precision)

            logger.debug(f"Adjusted order: {symbol} amount={amount} price={price}")

            min_notional = float(next(f['minNotional'] for f in symbol_info['filters'] if f['filterType'] == 'MIN_NOTIONAL'))
            if price * amount < min_notional:
                raise ValueError(f"Order value {price * amount} below min notional {min_notional}")

            order_func = lambda: client.create_order(
                symbol=symbol,
                side=side.upper(),
                type="LIMIT",
                timeInForce="GTC",
                quantity=amount,
                price=str(price)
            )
            order = limiter.execute_with_rate_limit(order_func, weight=1)
            logger.info(f"Smart {side} order executed for {symbol}: {amount} @ {price}")
            self._check_rate_limits(order)
            return order
        except Exception as e:
            logger.error(f"Order validation failed for {symbol}: {str(e)}")
            raise

    def execute_smart_order_with_retry(self, symbol, side, amount, max_retries=3, retry_delay=5):
        """Execută un ordin smart cu retry."""
        for attempt in range(max_retries):
            try:
                order = self.execute_smart_order(symbol, side, amount)
                if order:
                    return order
            except Exception as e:
                logger.error(f"Order failed: {str(e)}. Attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay)
        return None

    def close_position(self, position):
        """Închide o poziție."""
        try:
            order = self.execute_smart_order_with_retry(position["symbol"], "sell", position["amount"])
            if order:
                exit_price = float(order["fills"][0]["price"]) if "fills" in order and order["fills"] else float(client.get_symbol_ticker(symbol=position["symbol"])["price"])
                profit = (exit_price - position["entry_price"]) * position["amount"]
                self.telegram.notify_position_closed(position["symbol"], position["amount"], exit_price, profit)
                db.remove_position(position["order_id"])
                logger.info(f"Closed position for {position['symbol']}")
        except Exception as e:
            logger.error(f"Error closing position for {position['symbol']}: {str(e)}")

    def get_current_price(self, symbol):
        """Obține prețul curent."""
        try:
            data = self.websocket_manager.get_market_data(symbol)
            return data["close"] if data else float(client.get_symbol_ticker(symbol=symbol)["price"])
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {str(e)}")
            return 0.0

    def _check_rate_limits(self, response):
        """Verifică limitele de rată din răspunsul API."""
        if "rateLimits" in response:
            for limit in response["rateLimits"]:
                if limit["rateLimitType"] == "REQUEST_WEIGHT" and limit["count"] > 0.9 * limit["limit"]:
                    logger.warning(f"Approaching REQUEST_WEIGHT limit: {limit['count']}/{limit['limit']}")
                elif limit["rateLimitType"] == "ORDERS" and limit["count"] > 0.9 * limit["limit"]:
                    logger.warning(f"Approaching ORDERS limit: {limit['count']}/{limit['limit']}")