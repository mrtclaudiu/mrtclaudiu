import json
import logging
import threading
import time
import websocket
from database.db_manager import DatabaseManager
from utils.recovery import RecoverySystem

logger = logging.getLogger(__name__)
db = DatabaseManager()
recovery = RecoverySystem()

class WebSocketManager:
    def __init__(self, symbols=None):
        self.symbols = symbols or []
        self.market_data = {}
        self.callbacks = {}
        self.running = False
        self.ws = None
        self.logger = logger
        if not self.symbols:
            self.logger.warning("No symbols provided at initialization. Awaiting symbols...")

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if "k" in data:
                kline = data["k"]
                symbol = kline["s"]
                timestamp = kline["t"]
                o, h, l, c, v = float(kline["o"]), float(kline["h"]), float(kline["l"]), float(kline["c"]), float(kline["v"])
                self.market_data[symbol] = {
                    'open': o,
                    'high': h,
                    'low': l,
                    'close': c,
                    'volume': v,
                    'timestamp': timestamp
                }
                db.save_ohlcv(symbol, timestamp, o, h, l, c, v)
                if symbol in self.callbacks:
                    self.callbacks[symbol](self.market_data[symbol])
                self.logger.debug(f"Received WebSocket data for {symbol}")
        except Exception as e:
            self.logger.error(f"Eroare la procesarea mesajului WebSocket: {str(e)}")

    def on_error(self, ws, error):
        self.logger.error(f"Eroare WebSocket: {str(error)}")
        if self.running:
            self.logger.info("Reconnecting WebSocket...")
            recovery.recover(self.start, self.symbols)

    def on_close(self, ws, close_status_code, close_msg):
        self.logger.info(f"Conexiune WebSocket închisă: {close_msg}")
        if self.running:
            self.logger.info("Reconnecting WebSocket...")
            recovery.recover(self.start, self.symbols)

    def on_open(self, ws):
        self.logger.info("Conexiune WebSocket stabilită")
        if not self.symbols:
            self.logger.warning("No symbols to subscribe to on WebSocket open")
            return
        streams = [f"{symbol.lower()}@kline_5m" for symbol in self.symbols]
        chunk_size = 1024
        for i in range(0, len(streams), chunk_size):
            chunk = streams[i:i + chunk_size]
            subscribe_message = {
                "method": "SUBSCRIBE",
                "params": chunk,
                "id": i + 1
            }
            ws.send(json.dumps(subscribe_message))
        self.logger.debug(f"Subscribed to {len(self.symbols)} symbols")

    def start(self, symbols=None):
        if symbols:
            self.symbols = symbols
        if not self.symbols:
            self.logger.warning("Niciun simbol specificat pentru WebSocket")
            return

        self.running = True
        url = "wss://stream.binance.com:9443/stream"
        self.ws = websocket.WebSocketApp(
            url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        wst = threading.Thread(target=self.ws.run_forever, daemon=True)
        wst.start()
        self.logger.info(f"WebSocket pornit pentru {len(self.symbols)} simboluri")

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()
            self.logger.info("WebSocket oprit")

    def add_symbol(self, symbol):
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            if self.ws and self.ws.sock and self.ws.sock.connected:
                subscribe_message = {
                    "method": "SUBSCRIBE",
                    "params": [f"{symbol.lower()}@kline_5m"],
                    "id": len(self.symbols)
                }
                self.ws.send(json.dumps(subscribe_message))
                self.logger.info(f"Adăugat simbol {symbol} la WebSocket")

    def add_callback(self, symbol, callback):
        self.callbacks[symbol] = callback
        self.logger.info(f"Callback adăugat pentru {symbol}")

    def get_market_data(self, symbol):
        if symbol in self.market_data:
            return self.market_data[symbol]
        with db.conn:
            cursor = db.conn.execute(
                "SELECT open, high, low, close, volume, timestamp FROM ohlcv WHERE pair = ? ORDER BY timestamp DESC LIMIT 1",
                (symbol,)
            )
            data = cursor.fetchone()
            if data:
                return {
                    'open': data[0],
                    'high': data[1],
                    'low': data[2],
                    'close': data[3],
                    'volume': data[4],
                    'timestamp': data[5]
                }
        return None