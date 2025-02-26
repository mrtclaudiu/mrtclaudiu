import unittest
from database.db_manager import DatabaseManager
from trading.strategy import TradingStrategy

class TestSystems(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager("test_trading_bot.db")
        self.config = {"strategy": {"short_period": 10, "long_period": 50}}

    def test_db_init(self):
        self.db.create_tables()
        self.assertTrue(self.db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())

    def test_strategy_init(self):
        strategy = TradingStrategy(self.config)
        self.assertEqual(strategy.short_period, 10)

if __name__ == "__main__":
    unittest.main()
