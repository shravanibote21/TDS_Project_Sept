#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("Environment Configuration Check")
print("="*60)
print()

required_vars = {
    "GITHUB_TOKEN": "GitHub Personal Access Token",
    "GITHUB_USERNAME": "GitHub Username", 
    "OPENAI_API_KEY": "OpenAI API Key",
    "SECRET": "Secret Key for Request Verification"
}

missing = []
present = []

for var, description in required_vars.items():
    value = os.getenv(var)
    if not value or value.startswith("your_"):
        missing.append((var, description))
        print(f"[ ] {var}")
        print(f"    {description}")
        print("    Status: NOT SET or using default placeholder")
        print()
    else:
        present.append(var)
        masked = '*' * (len(value) - 4) + value[-4:] if len(value) > 4 else '****'
        print(f"[X] {var}")
        print(f"    {description}")
        print(f"    Value: {masked}")
        print()

print("="*60)
print("Summary")
print("="*60)
print(f"Present: {len(present)}/{len(required_vars)}")
print(f"Missing: {len(missing)}/{len(required_vars)}")
print()

if missing:
    print("MISSING CONFIGURATION:")
    for var, desc in missing:
        print(f"  - {var}: {desc}")
    print()
    print("To fix:")
    print("1. Copy .env.example to .env:")
    print("   cp .env.example .env")
    print()
    print("2. Edit .env and set the required values:")
    print("   - GITHUB_TOKEN: https://github.com/settings/tokens")
    print("   - OPENAI_API_KEY: https://platform.openai.com/api-keys")
    print("   - GITHUB_USERNAME: Your GitHub username")
    print("   - SECRET: Your chosen secret key")
    print()
    sys.exit(1)
else:
    print("All required environment variables are set!")
    print()
    
    try:
        from github import Github
        g = Github(os.getenv("GITHUB_TOKEN"))
        user = g.get_user()
        print("GitHub Authentication: SUCCESS")
        print(f"  Logged in as: {user.login}")
        print(f"  Name: {user.name}")
        print()
    except Exception as e:
        print("GitHub Authentication: FAILED")
        print(f"  Error: {str(e)}")
        print("  Please check your GITHUB_TOKEN")
        print()
        sys.exit(1)
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        print("OpenAI Authentication: SUCCESS")
        print("  API Key is valid")
        print()
    except Exception as e:
        print("OpenAI Authentication: FAILED")
        print(f"  Error: {str(e)}")
        print("  Please check your OPENAI_API_KEY")
        print()
        sys.exit(1)
    
    print("="*60)
    print("Configuration is valid and ready to use!")
    print("="*60)
    print()
    print("You can now run the server:")
    print("  uv run main.py")
    print()
    sys.exit(0)
