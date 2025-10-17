import time
from typing import Dict, Any
import requests
from .logger import get_logger

logger = get_logger(__name__)


def notify_evaluation_api(
    evaluation_url: str, data: Dict[str, Any], max_retries: int = 5
) -> bool:
    delay = 1
    session = requests.Session()
    for attempt in range(max_retries):
        try:
            response = session.post(
                evaluation_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                logger.info("Successfully notified evaluation API")
                return True
            else:
                logger.warning("Evaluation API status %s: %s", response.status_code, response.text)

        except requests.RequestException as e:
            logger.warning("Evaluation API attempt %s failed: %s", attempt + 1, str(e))

        if attempt < max_retries - 1:
            logger.info("Retrying evaluation API in %s seconds...", delay)
            time.sleep(delay)
            delay *= 2

    logger.error("Failed to notify evaluation API after all retries")
    return False
