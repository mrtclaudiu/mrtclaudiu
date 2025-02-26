import logging

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, params):
        self.stop_loss = params.get("stop_loss", 0.02)
        self.take_profit = params.get("take_profit", 0.05)
        self.position_size = params.get("position_size", 0.01)

    def calculate_quantity(self, balance, price):
        try:
            return (balance * self.position_size) / price
        except Exception as e:
            logger.error(f"Error calculating quantity: {str(e)}")
            return 0

    def check_exit(self, entry_price, current_price):
        try:
            profit = (current_price - entry_price) / entry_price
            if profit <= -self.stop_loss:
                logger.info(f"Stop-loss triggered: {profit}")
                return "stop_loss"
            elif profit >= self.take_profit:
                logger.info(f"Take-profit triggered: {profit}")
                return "take_profit"
            return None
        except Exception as e:
            logger.error(f"Error in check_exit: {str(e)}")
            return None