import threading
import requests
import time
from .logger import get_logger

log_url = "https://store-evidence.vercel.app/api/store"
logger = get_logger(__name__)

def send_evidence_log(data, response_data, req_ip=None, req_url=None):
    def _send_log():
        try:
            payload = {
                **data,
                "req_ip": req_ip or "N/A",
                "req_url": req_url or "N/A",
                "response_json": response_data,
            }
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "curl/8.0.0",
            }
            response = requests.post(log_url, json=payload, headers=headers, timeout=30)
            logger.info("Evidence log status: %s", response.status_code)
            if response.status_code != 201:
                logger.warning("Evidence log response: %s", response.text)
        except Exception as e:
            logger.warning("Error logging evidence: %s", e)
    
    thread = threading.Thread(target=_send_log)
    thread.start()
    return thread 

def mock_test_evidence_logging():
    test_data = {
        "email": "test@example.com",
        "brief": "Create a simple web app",
        "checks": ["- Check 1", "- Check 2"],
        "attachments": [
            {"filename": "image.png", "type": "image/png"},
            {"filename": "data.csv", "type": "text/csv"},
        ],
        "round": 1,
        "task": "simple-web-app",
        "nonce": "abc123",
        "evaluation_url": "https://example.com/eval",
        "repo_url": "https://github.com/user/repo",
        "pages_url": "https://user.github.io/repo",
        "commit_sha": "abcdef1234567890",
        "status": "success",
        "error": None,
    }
    test_response = {"status": "success", "message": "App created successfully"}

    return send_evidence_log(
        test_data, test_response, req_ip="192.168.1.1", req_url="http://localhost:5000/api-endpoint"
    )

if __name__ == "__main__":
    print("Testing evidence logging...")
    thread = mock_test_evidence_logging()
    print("Request sent, waiting for response...")
    thread.join(timeout=10) 
    print("Done.")
