import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manager pentru baza de date SQLite.
    Gestionarea tabelelor și operațiilor de bază de date.
    """

    def __init__(self, db_name: str = "trading_bot.db"):
        """
        Inițializează conexiunea la baza de date și creează tabelele necesare.

        :param db_name: Numele fișierului bazei de date.
        """
        self.db_name = db_name
        self.conn = self._create_connection()
        self.create_tables()

    def _create_connection(self) -> sqlite3.Connection:
        """
        Creează o conexiune la baza de date SQLite.

        :return: Conexiunea la baza de date.
        """
        try:
            conn = sqlite3.connect(self.db_name, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")  # Îmbunătățește performanța pentru scrieri simultane
            logger.info(f"Connected to database: {self.db_name}")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def create_tables(self):
        """Creează tabelele necesare în baza de date dacă nu există deja."""
        with self.conn:
            try:
                # Tabela pentru tranzacții
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pair TEXT,
                        entry_price REAL,
                        exit_price REAL,
                        profit REAL,
                        timestamp TEXT
                    )
                """)

                # Tabela pentru date OHLCV
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS ohlcv (
                        pair TEXT,
                        timestamp TEXT,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume REAL,
                        PRIMARY KEY (pair, timestamp)
                    )
                """)

                # Tabela pentru performanță
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS performance (
                        pair TEXT PRIMARY KEY,
                        total_profit REAL,
                        win_rate REAL,
                        trade_count INTEGER
                    )
                """)

                # Tabela pentru poziții deschise
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS open_positions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        amount REAL NOT NULL,
                        entry_price REAL NOT NULL,
                        order_id TEXT UNIQUE NOT NULL,
                        entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        risk REAL
                    )
                """)

                # Indexuri pentru tabele
                self.conn.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON open_positions(symbol)")
                self.conn.execute("CREATE INDEX IF NOT EXISTS idx_order_id ON open_positions(order_id)")

                # Tabela pentru analiza tehnică
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS technical_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        rsi REAL,
                        macd REAL,
                        volume REAL,
                        regime TEXT,
                        opportunity_score REAL
                    )
                """)

                # Tabela pentru istoricul tranzacțiilor
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS trade_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT,
                        side TEXT,
                        amount REAL,
                        price REAL,
                        timestamp TEXT
                    )
                """)

                logger.info("Tables created or verified successfully")
            except sqlite3.Error as e:
                logger.error(f"Error creating tables: {e}")
                raise

    def save_trade(self, pair: str, entry_price: float, exit_price: float, profit: float, timestamp: str):
        """Salvează o tranzacție în baza de date."""
        with self.conn:
            try:
                self.conn.execute(
                    "INSERT INTO trades (pair, entry_price, exit_price, profit, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (pair, entry_price, exit_price, profit, timestamp)
                )
                logger.info(f"Saved trade: {pair}, Profit: {profit}")
            except sqlite3.Error as e:
                logger.error(f"Error saving trade: {e}")
                raise

    def save_ohlcv(self, pair: str, timestamp: str, open: float, high: float, low: float, close: float, volume: float):
        """Salvează date OHLCV în baza de date."""
        with self.conn:
            try:
                self.conn.execute(
                    "INSERT OR REPLACE INTO ohlcv (pair, timestamp, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (pair, timestamp, open, high, low, close, volume)
                )
                logger.debug(f"Saved OHLCV data for {pair} at {timestamp}")
            except sqlite3.Error as e:
                logger.error(f"Error saving OHLCV data: {e}")
                raise

    def update_performance(self, pair: str, profit: float, win: bool):
        """Actualizează performanța pentru o pereche de tranzacționare."""
        with self.conn:
            try:
                cursor = self.conn.execute("SELECT total_profit, win_rate, trade_count FROM performance WHERE pair = ?", (pair,))
                data = cursor.fetchone()
                if data:
                    total_profit, win_rate, trade_count = data
                    total_profit += profit
                    trade_count += 1
                    win_rate = ((win_rate * (trade_count - 1)) + (1 if win else 0)) / trade_count
                    self.conn.execute(
                        "UPDATE performance SET total_profit = ?, win_rate = ?, trade_count = ? WHERE pair = ?",
                        (total_profit, win_rate, trade_count, pair)
                    )
                else:
                    self.conn.execute(
                        "INSERT INTO performance (pair, total_profit, win_rate, trade_count) VALUES (?, ?, ?, ?)",
                        (pair, profit, 1 if win else 0, 1)
                    )
                logger.info(f"Updated performance for {pair}")
            except sqlite3.Error as e:
                logger.error(f"Error updating performance: {e}")
                raise

    def save_technical_analysis(self, symbol: str, rsi: float, macd: float, volume: float, regime: str, opportunity_score: float):
        """Salvează analiza tehnică pentru un simbol."""
        with self.conn:
            try:
                self.conn.execute(
                    """
                    INSERT INTO technical_analysis (symbol, timestamp, rsi, macd, volume, regime, opportunity_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (symbol, datetime.now().isoformat(), rsi, macd, volume, regime, opportunity_score)
                )
                logger.info(f"Saved technical analysis for {symbol}")
            except sqlite3.Error as e:
                logger.error(f"Error saving technical analysis: {e}")
                raise

    def save_position(self, position: Dict[str, Any]) -> bool:
        """Salvează o poziție deschisă în baza de date."""
        with self.conn:
            try:
                self.conn.execute(
                    """
                    INSERT INTO open_positions (symbol, amount, entry_price, order_id, risk)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (position['symbol'], position['amount'], position['entry_price'],
                     position['order_id'], position.get('risk', 0))
                )
                logger.info(f"Saved position for {position['symbol']}")
                return True
            except sqlite3.Error as e:
                logger.error(f"Error saving position: {e}")
                return False

    def remove_position(self, order_id: str):
        """Șterge o poziție deschisă din baza de date."""
        with self.conn:
            try:
                self.conn.execute("DELETE FROM open_positions WHERE order_id = ?", (order_id,))
                logger.info(f"Position {order_id} removed from database")
            except sqlite3.Error as e:
                logger.error(f"Error removing position: {e}")
                raise

    def load_positions(self) -> List[Dict[str, Any]]:
        """Încarcă toate pozițiile deschise din baza de date."""
        with self.conn:
            try:
                cursor = self.conn.execute("""
                    SELECT symbol, amount, entry_price, order_id, risk, entry_time
                    FROM open_positions
                    ORDER BY entry_time DESC
                """)
                positions = [
                    {
                        'symbol': row[0],
                        'amount': float(row[1]),
                        'entry_price': float(row[2]),
                        'order_id': row[3],
                        'risk': float(row[4]) if row[4] is not None else 0.0,
                        'entry_time': row[5]
                    }
                    for row in cursor.fetchall()
                ]
                logger.info(f"Loaded {len(positions)} open positions")
                return positions
            except sqlite3.Error as e:
                logger.error(f"Error loading positions: {e}")
                return []

    def save_trade_history(self, symbol: str, side: str, amount: float, price: float, timestamp: str):
        """Salvează istoricul unei tranzacții."""
        with self.conn:
            try:
                self.conn.execute(
                    """
                    INSERT INTO trade_history (symbol, side, amount, price, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (symbol, side, amount, price, timestamp)
                )
                logger.info(f"Saved trade history for {symbol}")
            except sqlite3.Error as e:
                logger.error(f"Error saving trade history: {e}")
                raise

    def get_ohlcv_data(self, pair: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Returnează datele OHLCV pentru o pereche specificată.

        :param pair: Perechea de tranzacționare (e.g., 'BTCUSDT').
        :param limit: Numărul maxim de rânduri returnate.
        :return: Lista de dicționare cu date OHLCV.
        """
        with self.conn:
            try:
                cursor = self.conn.execute("""
                    SELECT pair, timestamp, open, high, low, close, volume
                    FROM ohlcv
                    WHERE pair = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (pair, limit))
                data = [
                    {
                        'pair': row[0],
                        'timestamp': row[1],
                        'open': float(row[2]),
                        'high': float(row[3]),
                        'low': float(row[4]),
                        'close': float(row[5]),
                        'volume': float(row[6])
                    }
                    for row in cursor.fetchall()
                ]
                logger.debug(f"Loaded {len(data)} OHLCV rows for {pair}")
                return data
            except sqlite3.Error as e:
                logger.error(f"Error loading OHLCV data: {e}")
                return []

    def get_all_pairs(self) -> List[str]:
        """Fetch all unique trading pairs from the OHLCV table."""
        with self.conn:
            try:
                cursor = self.conn.execute("SELECT DISTINCT pair FROM ohlcv")
                pairs = [row[0] for row in cursor.fetchall()]
                logger.info(f"Fetched {len(pairs)} trading pairs from OHLCV data")
                return pairs
            except sqlite3.Error as e:
                logger.error(f"Error fetching trading pairs: {e}")
                return []