import os
import sys
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI
from github import Github
from .logger import get_logger

load_dotenv()
logger = get_logger(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SECRET = os.getenv("SECRET", "")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")
PORT = int(os.getenv("PORT", 5000))

FALLBACK_API_KEY = os.getenv("AIPIPE_AKI_KEY", "")
FALLBACK_BASE_URL = "https://aipipe.org/openai/v1"

_openai_client = None
_fallback_client = None
_github_client = None


def validate_config() -> None:
    missing = []

    if not GITHUB_TOKEN:
        missing.append("GITHUB_TOKEN")
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not SECRET:
        missing.append("SECRET")
    if not GITHUB_USERNAME:
        missing.append("GITHUB_USERNAME")

    if missing:
        logger.error("Missing required environment variables: %s", ", ".join(missing))
        logger.error("Please set these variables in your .env file. See .env.example for reference.")
        sys.exit(1)

    logger.info("Configuration validated successfully")
    logger.info("  - GitHub Username: %s", GITHUB_USERNAME)
    logger.info("  - GitHub Token: **********%s", GITHUB_TOKEN[-4:] if len(GITHUB_TOKEN) > 4 else "****")
    logger.info("  - OpenAI API Key: **********%s", OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 4 else "****")
    logger.info("  - Secret: %s", "*" * len(SECRET))
    logger.info("  - Port: %s", PORT)


def load_config() -> Dict[str, object]:
    return {
        "github_token": GITHUB_TOKEN,
        "openai_api_key": OPENAI_API_KEY,
        "secret": SECRET,
        "github_username": GITHUB_USERNAME,
        "port": PORT,
    }


def get_openai_client():
    global _openai_client
    if _openai_client is None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")
        _openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
    return _openai_client


def get_fallback_client():
    global _fallback_client
    if _fallback_client is None:
        _fallback_client = OpenAI(
            api_key=FALLBACK_API_KEY,
            base_url=FALLBACK_BASE_URL,
        )
    return _fallback_client


def get_github_client():
    global _github_client
    if _github_client is None:
        if not GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN not set in environment")
        _github_client = Github(GITHUB_TOKEN)
    return _github_client
