import pandas as pd
from database.db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)
db = DatabaseManager()

def export_to_csv(pair, filename="ml_data.csv"):
    with db.conn:
        df = pd.read_sql_query("SELECT * FROM ohlcv WHERE pair = ?", db.conn, params=(pair,))
    df.to_csv(filename, index=False)
    logger.info(f"Exported OHLCV data for {pair} to {filename}")
