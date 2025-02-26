import time
import logging
from collections import deque
from datetime import datetime
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiter pentru gestionarea apelurilor API Binance.
    Suportă mai multe tipuri de limite (REQUEST_WEIGHT, ORDERS, etc.) și backoff exponențial.
    """

    def __init__(self, limits: List[Dict[str, Any]]):
        """
        Inițializează RateLimiter cu limitele specificate.

        :param limits: Lista de limite. Fiecare limită este un dicționar cu cheile:
                      - rateLimitType: Tipul limitei (e.g., 'REQUEST_WEIGHT', 'ORDERS').
                      - interval: Intervalul de timp ('SECOND', 'MINUTE', 'HOUR', 'DAY').
                      - intervalNum: Numărul de intervale.
                      - limit: Numărul maxim de cereri pe interval.
        """
        self.limits = limits
        self.requests = {limit['rateLimitType']: deque(maxlen=limit['limit']) for limit in limits}
        self.logger = logger

    def _clean_old_requests(self, limit_type: str, interval: int, interval_num: int):
        """
        Elimină cererile mai vechi de intervalul specificat.

        :param limit_type: Tipul limitei (e.g., 'REQUEST_WEIGHT').
        :param interval: Intervalul de timp în secunde.
        :param interval_num: Numărul de intervale.
        """
        now = datetime.now()
        while self.requests[limit_type] and (now - self.requests[limit_type][0]).total_seconds() > interval_num * interval:
            self.requests[limit_type].popleft()

    def wait(self, weight: int = 1, limit_type: str = 'REQUEST_WEIGHT'):
        """
        Așteaptă dacă limitele sunt aproape de a fi depășite.

        :param weight: Greutatea cererii (cât consumă din limită).
        :param limit_type: Tipul limitei (e.g., 'REQUEST_WEIGHT').
        """
        limit = next((l for l in self.limits if l['rateLimitType'] == limit_type), None)
        if not limit:
            raise ValueError(f"Unknown limit type: {limit_type}")

        interval = {'SECOND': 1, 'MINUTE': 60, 'HOUR': 3600, 'DAY': 86400}[limit['interval']]
        interval_num = limit['intervalNum']
        self._clean_old_requests(limit_type, interval, interval_num)
        now = datetime.now()

        if len(self.requests[limit_type]) + weight > limit['limit']:
            wait_time = interval_num * interval - (now - self.requests[limit_type][0]).total_seconds()
            self.logger.warning(f"Limită {limit_type} aproape de a fi depășită. Aștept {wait_time:.2f}s")
            time.sleep(max(wait_time, 0.1))

        for _ in range(weight):
            self.requests[limit_type].append(now)
        self.logger.debug(f"Request adăugat pentru {limit_type}. Total requests: {len(self.requests[limit_type])}")

    def execute_with_rate_limit(self, func: Callable, weight: int = 1, limit_type: str = 'REQUEST_WEIGHT', max_retries: int = 3) -> Any:
        """
        Execută o funcție cu limitare de rată.

        :param func: Funcția de executat.
        :param weight: Greutatea cererii (cât consumă din limită).
        :param limit_type: Tipul limitei (e.g., 'REQUEST_WEIGHT').
        :param max_retries: Numărul maxim de reîncercări.
        :return: Rezultatul funcției.
        """
        retries = 0
        while retries < max_retries:
            try:
                self.wait(weight, limit_type)
                result = func()
                return result
            except Exception as e:
                if "rate limit" in str(e).lower():
                    wait_time = min(60 * (2 ** retries), 300)  # Backoff exponențial
                    self.logger.warning(f"Limită API depășită. Aștept {wait_time}s")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    self.logger.error(f"Eroare neașteptată: {e}")
                    raise
        raise RuntimeError(f"Depășit numărul maxim de retry-uri ({max_retries}) pentru limitarea ratei")