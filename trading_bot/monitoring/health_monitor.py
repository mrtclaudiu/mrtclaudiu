import time
import logging
from utils.telegram_notifier import sync_send_message
from binance.client import Client
from utils.env_loader import BINANCE_API_KEY, BINANCE_SECRET_KEY

logger = logging.getLogger(__name__)
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

class HealthMonitor:
    def __init__(self):
        self.running = True
        logger.info("HealthMonitor initialized")

    def check_health(self):
        """Verifică starea API-ului Binance la fiecare minut."""
        while self.running:
            try:
                client.ping()  # Verifică conexiunea la API
                logger.info("API health: OK")
            except Exception as e:
                logger.error(f"API health check failed: {e}")
                sync_send_message(f"Health check failed: {e}")
            time.sleep(60)  # Verificare la fiecare minut

    def stop(self):
        """Oprește monitorizarea sănătății."""
        self.running = False
        logger.info("HealthMonitor stopped")