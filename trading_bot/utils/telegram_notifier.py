import requests
import logging
from utils.env_loader import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime

logger = logging.getLogger(__name__)

def send_message(message):
    """Trimite un mesaj sincron prin Telegram folosind API-ul HTTP."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f"Telegram message sent: {message}")
    except requests.RequestException as e:
        logger.error(f"Eroare la trimiterea mesajului Telegram: {str(e)}")

class TelegramNotifier:
    """Gestionează notificările Telegram pentru evenimentele botului."""
    def notify_bot_start(self):
        message = f"🟢 Trading Bot Started\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_message(message)

    def notify_bot_stop(self):
        message = f"🔴 Trading Bot Stopped\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_message(message)

    def notify_position_opened(self, symbol, amount, price):
        message = (
            f"📈 Position Opened\nSymbol: {symbol}\nAmount: {amount}\n"
            f"Price: {price}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_message(message)

    def notify_position_closed(self, symbol, amount, price, profit):
        message = (
            f"📉 Position Closed\nSymbol: {symbol}\nAmount: {amount}\n"
            f"Price: {price}\nProfit: {profit}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_message(message)

    def notify_balance_update(self, balance):
        message = (
            f"💰 Balance Update\nCurrent Balance: {balance} USDT\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_message(message)

# Compatibilitate cu apeluri existente
sync_send_message = send_message
