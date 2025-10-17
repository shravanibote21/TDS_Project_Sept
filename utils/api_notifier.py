import time
from typing import Dict, Any
import requests


def notify_evaluation_api(
    evaluation_url: str, data: Dict[str, Any], max_retries: int = 5
) -> bool:
    delay = 1
    for attempt in range(max_retries):
        try:
            response = requests.post(
                evaluation_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                print(f"Successfully notified evaluation API: {response.text}")
                return True
            else:
                print(
                    f"Evaluation API returned status {response.status_code}: {response.text}"
                )

        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")

        if attempt < max_retries - 1:
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2

    print("Failed to notify evaluation API after all retries")
    return False
