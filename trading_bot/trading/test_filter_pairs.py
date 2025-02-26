
import sys
import os
import json
import logging
from trading_filter import TradingFilters

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Get the correct config path
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

def test_filter_pairs():
    filters = TradingFilters(config)
    filters.initialize_ohlcv_data()
    pairs = filters.filter_pairs()
    logger.info(f"Filtered pairs: {pairs}")
    return pairs

if __name__ == "__main__":
    test_filter_pairs()
