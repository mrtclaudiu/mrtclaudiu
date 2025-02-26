import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Adaugă directorul curent în calea de import
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from bot_launcher import BotLauncher

# Configurare logging avansat
script_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(script_dir, "logs"), exist_ok=True)
logger = logging.getLogger(__name__)
logger.handlers.clear()
logger.setLevel(logging.INFO)

# Handler pentru fișierul de log
file_handler = RotatingFileHandler(
    os.path.join(script_dir, "logs", "trade_log.txt"),
    maxBytes=10000,
    backupCount=5
)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Handler pentru consolă
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Adaugă handler-ele la logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Încărcare configurație
config_path = os.path.join(script_dir, "config.json")
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

def main():
    bot = None
    try:
        logger.info("Starting Advanced Trading Bot...")
        logger.info("Initializing BotLauncher...")
        bot = BotLauncher(config)
        logger.info("BotLauncher initialized successfully")
        logger.info("Starting bot.run()...")
        bot.run()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        if bot:
            bot.stop()
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}")
        logger.exception("Full error traceback:")
        if bot:
            try:
                bot.stop()
            except:
                pass
        sys.exit(1)

if __name__ == "__main__":
    main()