import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from utils.rate_limiter import RateLimiter

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def dummy_api_call():
    logger.info("API call executed")
    return "success"

if __name__ == "__main__":
    # Definirea limitelor pentru testare
    limits = [
        {'rateLimitType': 'REQUEST_WEIGHT', 'interval': 'SECOND', 'intervalNum': 1, 'limit': 2},
        {'rateLimitType': 'REQUEST_WEIGHT', 'interval': 'MINUTE', 'intervalNum': 1, 'limit': 10},
        {'rateLimitType': 'REQUEST_WEIGHT', 'interval': 'MINUTE', 'intervalNum': 1, 'limit': 50}
    ]
    
    rate_limiter = RateLimiter(limits)
    
    for _ in range(15):
        result = rate_limiter.execute_with_rate_limit(dummy_api_call, weight=5)
        logger.info(f"Result: {result}")