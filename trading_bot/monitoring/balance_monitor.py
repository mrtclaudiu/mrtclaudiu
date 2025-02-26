import time
import logging
from utils.telegram_notifier import sync_send_message
from binance.client import Client
from utils.env_loader import BINANCE_API_KEY, BINANCE_SECRET_KEY

logger = logging.getLogger(__name__)
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

class BalanceMonitor:
    def __init__(self):
        self.running = True
        logger.info("BalanceMonitor initialized")

    def monitor_balance(self):
        """Monitorizează soldul contului Binance la fiecare 5 minute."""
        while self.running:
            try:
                # Obține soldul pentru USDT
                balance = float(client.get_asset_balance(asset="USDT")["free"])
                logger.info(f"Current balance: {balance} USDT")

                # Trimite notificare pe Telegram dacă soldul este sub un anumit prag
                if balance < 15:  # Pragul poate fi ajustat
                    sync_send_message(f"Warning: Low balance! Current balance: {balance} USDT")

            except Exception as e:
                logger.error(f"Failed to check balance: {e}")
                sync_send_message(f"Failed to check balance: {e}")

            time.sleep(300)  # Verificare la fiecare 5 minute

    def stop(self):
        """Oprește monitorizarea soldului."""
        self.running = False
        logger.info("BalanceMonitor stopped")
