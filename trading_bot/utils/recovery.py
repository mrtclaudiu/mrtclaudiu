import logging
from datetime import datetime
import sqlite3
from binance.client import Client
from utils.env_loader import BINANCE_API_KEY, BINANCE_SECRET_KEY
from utils.telegram_notifier import sync_send_message
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
db = DatabaseManager()

class RecoverySystem:
    """Gestionează recuperarea și riscul pozițiilor de trading."""
    def __init__(self):
        self.logger = logger

    def validate_and_recover_positions(self):
        """Validează și recuperează pozițiile la pornirea botului."""
        positions = db.load_positions()
        positions_to_remove = []

        for position in positions[:]:
            try:
                self._process_position(position, positions_to_remove)
            except Exception as e:
                self.logger.error(f"Eroare la verificarea poziției {position['symbol']}: {str(e)}")

        self._cleanup_positions(positions_to_remove)
        self._notify_recovery_complete(len(positions), len(positions_to_remove))

    def _process_position(self, position, positions_to_remove):
        """Procesează statusul și recuperarea unei poziții."""
        try:
            order_info = client.get_order(symbol=position['symbol'], orderId=position['order_id'])
            if order_info['status'] not in ['NEW', 'PARTIALLY_FILLED']:
                positions_to_remove.append(position)
                return

            current_price = self.get_current_price(position['symbol'])
            if current_price:
                self.manage_risk(position['symbol'], position['entry_price'], current_price)
                self.logger.info(f"Restaurat protecția pentru {position['symbol']}")
        except Exception as e:
            if "order does not exist" in str(e).lower():
                positions_to_remove.append(position)
                self.logger.info(f"Ordinul nu există pentru {position['symbol']}, încerc recuperare")
                self._attempt_position_closure(position)
            else:
                self.logger.error(f"Recuperare eșuată pentru {position['symbol']}: {str(e)}")

    def _cleanup_positions(self, positions_to_remove):
        """Elimină pozițiile invalide."""
        for position in positions_to_remove:
            db.remove_position(position['order_id'])
            self.logger.info(f"Eliminat poziția pentru {position['symbol']} la pornire")

    def _notify_recovery_complete(self, total_positions, removed_count):
        """Trimite notificare despre finalizarea recuperării."""
        msg = (
            "🔄 Bot repornit și sistem de recuperare activat\n"
            f"Poziții verificate: {total_positions}\n"
            f"Poziții eliminate: {removed_count}"
        )
        sync_send_message(msg)

    def get_current_price(self, symbol):
        """Obține prețul curent pentru un simbol."""
        try:
            ticker = client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            self.logger.error(f"Eroare la obținerea prețului pentru {symbol}: {str(e)}")
            return None

    def manage_risk(self, symbol, entry_price, current_price):
        """Gestionează riscul poziției cu trailing stop-loss."""
        profit_percentage = (current_price - entry_price) / entry_price
        stop_loss = self._calculate_stop_loss(current_price, entry_price, profit_percentage)

        self.logger.info(f"Risc gestionat pentru {symbol}: Trailing Stop Loss @ {stop_loss}")
        # Aici ar trebui actualizat ordinul OCO existent sau creat unul nou (logică viitoare)

    def _calculate_stop_loss(self, current_price, entry_price, profit_percentage):
        """Calculează stop-loss-ul trailing."""
        if profit_percentage > 1.0:  # Profit > 100%
            return current_price * 0.75
        elif profit_percentage > 0.1:  # Profit > 10%
            return current_price * 0.95
        return entry_price * 0.95  # Default: 5% sub prețul de intrare

    def _attempt_position_closure(self, position):
        """Încearcă să închidă o poziție pierdută."""
        try:
            # Placeholder: Logică pentru închiderea manuală a poziției
            self.logger.info(f"Închidere manuală poziție {position['symbol']} nu e implementată încă")
            # Ex: Plasare ordin de piață pentru a vinde `position['amount']`
        except Exception as e:
            self.logger.error(f"Eroare la închiderea poziției {position['symbol']}: {str(e)}")

    def recover(self, func, *args, **kwargs):
        """Recuperează apelurile eșuate cu retry."""
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempts += 1
                self.logger.error(f"Eroare: {e}. Încercarea {attempts}/{max_attempts}")
                sync_send_message(f"Eroare bot: {e}. Reîncerc ({attempts}/{max_attempts})")
                time.sleep(2 ** attempts)  # Backoff exponențial
        self.logger.critical("Maxim de încercări atins. Oprire.")
        sync_send_message("Bot oprit după maxim de retry!")
        raise Exception("Recuperare eșuată")
