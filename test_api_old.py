#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

B_URL = "http://localhost:5000/"
# B_URL = "https://project1-tds-t3-2025.vercel.app/"
API_URL = B_URL + "api-endpoint"
SECRET = os.getenv("SECRET", "your_secret_key_here")

timeouts = {"test_health": 5, "round1": 500, "round2": 500}

test_request_calculator = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "calculator-app-xyz789",
    "round": 1,
    "nonce": "test-nonce-123456",
    "brief": "Create a simple calculator web app that can perform basic arithmetic operations (addition, subtraction, multiplication, division). The interface should be clean and user-friendly with buttons for numbers 0-9 and operation symbols. Display the result clearly.",
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [],
}

test_request_sales_summary = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "sum-of-sales",
    "round": 1,
    "nonce": "sales-nonce-001",
    "brief": "Publish a single-page site that fetches data.csv from attachments, sums its sales column, sets the title to 'Sales Summary 12345', displays the total inside #total-sales, and loads Bootstrap 5 from jsdelivr.",
    "checks": [
        "js: document.title === 'Sales Summary 12345'",
        "js: !!document.querySelector(\"link[href*='bootstrap']\")",
        'js: Math.abs(parseFloat(document.querySelector("#total-sales").textContent) - 15000) < 0.01',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
        {
            "name": "data.csv",
            "url": "data:text/csv;base64,cHJvZHVjdCxzYWxlcwpBLDUwMDAKQiwxMDAwMApDLDUwMDA=",
        }
    ],
}

test_request_github_user = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "github-user-created",
    "round": 1,
    "nonce": "github-nonce-001",
    "brief": "Publish a Bootstrap page with form id='github-user-abc123' that fetches a GitHub username, optionally uses ?token=, and displays the account creation date in YYYY-MM-DD UTC inside #github-created-at.",
    "checks": [
        'js: document.querySelector("#github-user-abc123").tagName === "FORM"',
        'js: document.querySelector("#github-created-at").textContent.includes("20")',
        'js: !!document.querySelector("script").textContent.includes("https://api.github.com/users/")',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [],
}

test_request_markdown_to_html = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "markdown-to-html",
    "round": 1,
    "nonce": "md-nonce-001",
    "brief": "Publish a static page that converts input.md from attachments to HTML with marked, renders it inside #markdown-output, and loads highlight.js for code blocks.",
    "checks": [
        "js: !!document.querySelector(\"script[src*='marked']\")",
        "js: !!document.querySelector(\"script[src*='highlight.js']\")",
        'js: document.querySelector("#markdown-output").innerHTML.includes("<h")',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
        {
            "name": "input.md",
            "url": "data:text/markdown;base64,IyBIZWxsbyBXb3JsZAoKVGhpcyBpcyBhIHNhbXBsZSBtYXJrZG93biBmaWxlLgoKYGBgYApjb2RlIGJsb2NrCmBgYAo=",
        }
    ],
}

test_request_sum_of_sales = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "sum-of-sales",
    "round": 1,
    "nonce": "sales-nonce-001",
    "brief": "Publish a single-page site that fetches data.csv from attachments, sums its sales column, sets the title to 'Sales Summary 12345', displays the total inside #total-sales, and loads Bootstrap 5 from jsdelivr.",
    "checks": [
        "js: document.title === 'Sales Summary 12345'",
        "js: !!document.querySelector(\"link[href*='bootstrap']\")",
        'js: Math.abs(parseFloat(document.querySelector("#total-sales").textContent) - 15000) < 0.01',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
        {
            "name": "data.csv",
            "url": "data:text/csv;base64,cHJvZHVjdCxzYWxlcwpBLDUwMDAKQiwxMDAwMApDLDUwMDA=",
        }
    ],
}

test_request_github_user_created = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "github-user-created",
    "round": 1,
    "nonce": "github-nonce-001",
    "brief": "Publish a Bootstrap page with form id='github-user-abc123' that fetches a GitHub username, optionally uses ?token=, and displays the account creation date in YYYY-MM-DD UTC inside #github-created-at.",
    "checks": [
        'js: document.querySelector("#github-user-abc123").tagName === "FORM"',
        'js: document.querySelector("#github-created-at").textContent.includes("20")',
        'js: !!document.querySelector("script").textContent.includes("https://api.github.com/users/")',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [],
}

test_request_counter_app = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "counter-app",
    "round": 1,
    "nonce": "counter-nonce-001",
    "brief": "Publish a static page with a button #increment-btn and a number inside #counter-value that increments by 1 each time the button is clicked.",
    "checks": [
        'js: !!document.querySelector("#increment-btn")',
        'js: !!document.querySelector("#counter-value")',
        'js: (() => { const v = document.querySelector("#counter-value"); const b = document.querySelector("#increment-btn"); const before = parseInt(v.textContent, 10); b.click(); return parseInt(v.textContent, 10) === before + 1; })()',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [],
}

# Additional example: static page with a dark mode toggle
test_request_dark_mode = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "dark-mode-toggle",
    "round": 1,
    "nonce": "darkmode-nonce-001",
    "brief": "Publish a static page with a toggle #dark-mode-toggle that switches the page between light and dark themes, updating the body class.",
    "checks": [
        'js: !!document.querySelector("#dark-mode-toggle")',
        'js: (() => { const t = document.querySelector("#dark-mode-toggle"); const b = document.body; t.click(); return b.classList.contains("dark"); })()',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [],
}

test_request_file_preview = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "file-preview-test",
    "round": 1,
    "nonce": "file-preview-nonce-001",
    "brief": "Create a page that displays data from the CSV file showing employee information. Parse the CSV data and display it in a Bootstrap table with id='employee-table'. Also show the first line of the notes.txt file in a div with id='notes-preview'.",
    "checks": [
        'js: !!document.querySelector("#employee-table")',
        'js: document.querySelectorAll("#employee-table tbody tr").length >= 3',
        'js: !!document.querySelector("#notes-preview")',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
        {
            "name": "sample_data.csv",
            "url": "data:text/csv;base64,bmFtZSxhZ2UsY2l0eSxzYWxhcnkKSm9obiBEb2UsMjgsTmV3IFlvcmssNzUwMDAKSmFuZSBTbWl0aCwzNCxMb3MgQW5nZWxlcyw4MjAwMApCb2IgSm9obnNvbiw0NSxDaGljYWdvLDY1MDAwCkFsaWNlIFdpbGxpYW1zLDI5LEhvdXN0b24sNzEwMDAKQ2hhcmxpZSBCcm93biwzOCxQaG9lbml4LDY4MDAwCkRhdmlkIExlZSw1MixQaGlsYWRlbHBoaWEsOTUwMDAKRW1tYSBEYXZpcywzMSxTYW4gQW50b25pbyw3MzAwMApGcmFuayBNaWxsZXIsNDEsU2FuIERpZWdvLDc5MDAwCkdyYWNlIFdpbHNvbiwyNyxEYWxsYXMsNjcwMDAKSGVucnkgTW9vcmUsMzYsU2FuIEpvc2UsODgwMDA=",
        },
        {
            "name": "notes.txt",
            "url": "data:text/plain;base64,UHJvamVjdCBSZXF1aXJlbWVudHMgRG9jdW1lbnQKPT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KVmVyc2lvbjogMS4wCkRhdGU6IDIwMjUtMTAtMTQKQXV0aG9yOiBUZXN0IFRlYW0KClRoaXMgaXMgYSBzYW1wbGUgdGV4dCBmaWxlIGZvciB0ZXN0aW5nIGZpbGUgcHJldmlldyBmdW5jdGlvbmFsaXR5LgpUaGUgc3lzdGVtIHNob3VsZCBiZSBhYmxlIHRvIHJlYWQgdGhlIGZpcnN0IDUgbGluZXMgb2YgdGhpcyBmaWxlLgpFYWNoIGxpbmUgY29udGFpbnMgaW1wb3J0YW50IGluZm9ybWF0aW9uLgpMaW5lIDQ6IFRlc3RpbmcgcHJvcGVyIGxpbmUgcmVhZGluZy4KTGluZSA1OiBUaGlzIHNob3VsZCBiZSB0aGUgbGFzdCBsaW5lIGRpc3BsYXllZCBpbiBwcmV2aWV3LgpMaW5lIDY6IFRoaXMgbGluZSBzaG91bGQgTk9UIGFwcGVhciBpbiB0aGUgcHJldmlldy4KQWRkaXRpb25hbCBjb250ZW50IGZvbGxvd3MgYnV0IHdvbid0IGJlIHZpc2libGUgaW4gdGhlIGluaXRpYWwgcHJldmlldy4=",
        },
    ],
}

test_request_image_gallery = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "image-gallery-test",
    "round": 1,
    "nonce": "image-gallery-nonce-001",
    "brief": "Create a responsive image gallery page that displays the attached logo image. The page should have a title 'Image Gallery', use Bootstrap for styling, and display the image with id='gallery-image'. Add a caption below the image with id='image-caption' that says 'Company Logo'.",
    "checks": [
        'js: !!document.querySelector("#gallery-image")',
        'js: document.querySelector("#gallery-image").tagName === "IMG"',
        'js: !!document.querySelector("#image-caption")',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
        {
            "name": "logo.png",
            "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        },
    ],
}

test_request_multi_media = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "multi-media-test",
    "round": 1,
    "nonce": "multi-media-nonce-001",
    "brief": "Create a multimedia showcase page with Bootstrap styling. Display the logo image in an img tag with id='showcase-image', show the first 3 lines of data from data.csv in a div with id='data-preview', and add a section with id='file-info' that lists information about all attached files.",
    "checks": [
        'js: !!document.querySelector("#showcase-image")',
        'js: !!document.querySelector("#data-preview")',
        'js: !!document.querySelector("#file-info")',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
        {
            "name": "logo.png",
            "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        },
        {
            "name": "data.csv",
            "url": "data:text/csv;base64,bmFtZSxhZ2UsY2l0eSxzYWxhcnkKSm9obiBEb2UsMjgsTmV3IFlvcmssNzUwMDAKSmFuZSBTbWl0aCwzNCxMb3MgQW5nZWxlcyw4MjAwMA==",
        },
        {
            "name": "readme.txt",
            "url": "data:text/plain;base64,VGhpcyBpcyBhIHNhbXBsZSByZWFkbWUgZmlsZQpMaW5lIDIgb2YgdGhlIHJlYWRtZQpMaW5lIDMgb2YgdGhlIHJlYWRtZQ==",
        },
    ],
}

test_request = test_request_calculator


def test_health():
    print("Testing health endpoint...")
    try:
        response = requests.get(B_URL + "/health", timeout=timeouts["test_health"])
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Health check failed: {e}")
        return False


def test_deployment(request_data=None):
    if request_data is None:
        request_data = test_request

    print("\n" + "=" * 60)
    print("Testing deployment endpoint...")
    print("=" * 60)

    print("\nSending request:")
    print(json.dumps(request_data, indent=2))

    try:
        response = requests.post(
            API_URL,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=timeouts.get("round1"),  # Give it 2 minutes to complete
        )

        print(f"\nResponse Status: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            data = response.json()
            print("\n" + "=" * 60)
            print(" SUCCESS!")
            print("=" * 60)
            print(f"Repository: {data.get('repo_url')}")
            print(f"GitHub Pages: {data.get('pages_url')}")
            print(f"Commit SHA: {data.get('commit_sha')}")
            print("\nNote: GitHub Pages may take 1-2 minutes to deploy.")
            return True
        else:
            print("\n Request failed")
            return False

    except requests.RequestException as e:
        print(f"\n Request error: {e}")
        return False


def test_round_2(base_request=None, brief=None):
    if base_request is None:
        base_request = test_request
    if brief is None:
        brief = "Update the calculator to also support square root and percentage operations. Add a clear button to reset the calculator."

    print("\n" + "=" * 60)
    print("Testing Round 2 (Revision) endpoint...")
    print("=" * 60)

    round2_request = base_request.copy()
    round2_request["round"] = 2
    round2_request["brief"] = brief
    round2_request["nonce"] = base_request.get("nonce", "test-nonce") + "-round2"

    print("\nSending Round 2 request:")
    print(json.dumps(round2_request, indent=2))

    try:
        response = requests.post(
            API_URL,
            json=round2_request,
            headers={"Content-Type": "application/json"},
            timeout=timeouts.get("round2"),
        )

        print(f"\nResponse Status: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            data = response.json()
            print("\n" + "=" * 60)
            print(" ROUND 2 SUCCESS!")
            print("=" * 60)
            print(f"Repository: {data.get('repo_url')}")
            print(f"GitHub Pages: {data.get('pages_url')}")
            print(f"Commit SHA: {data.get('commit_sha')}")
            return True
        else:
            print("\n Round 2 request failed")
            return False

    except requests.RequestException as e:
        print(f"\n Request error: {e}")
        return False


def select_test_example():
    print("\nAvailable test examples:")
    print("1. Calculator App (basic arithmetic operations)")
    print("2. Sales Summary (CSV parsing, Bootstrap, sum calculation)")
    print("3. GitHub User Created (API fetch, date formatting)")
    print("4. Markdown to HTML (marked, highlight.js)")
    print("5. Counter App (static, button increments value)")
    print("6. Dark Mode Toggle (static, theme switch)")
    print("7. File Preview Test (CSV + TXT with first 5 lines preview)")
    print("8. Image Gallery Test (PNG image rendering)")
    print("9. Multi-Media Test (Image + CSV + TXT combined)")
    print(
        "\nSelect an example (1-9), or press Enter for default (Calculator): ", end=""
    )

    try:
        choice = input().strip()
        if not choice or choice == "1":
            return test_request_calculator, "Calculator App"
        elif choice == "2":
            return test_request_sum_of_sales, "Sales Summary"
        elif choice == "3":
            return test_request_github_user_created, "GitHub User Created"
        elif choice == "4":
            return test_request_markdown_to_html, "Markdown to HTML"
        elif choice == "5":
            return test_request_counter_app, "Counter App"
        elif choice == "6":
            return test_request_dark_mode, "Dark Mode Toggle"
        elif choice == "7":
            return test_request_file_preview, "File Preview Test"
        elif choice == "8":
            return test_request_image_gallery, "Image Gallery Test"
        elif choice == "9":
            return test_request_multi_media, "Multi-Media Test"
        else:
            print("Invalid choice, using default (Calculator App)")
            return test_request_calculator, "Calculator App"
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return None, None


def get_round2_examples(example_name):
    if example_name == "Sales Summary":
        return [
            {
                "brief": "Add a Bootstrap table #product-sales that lists each product with its total sales and keeps #total-sales accurate after render.",
                "checks": [
                    'js: document.querySelectorAll("#product-sales tbody tr").length >= 1',
                    'js: (() => { const rows = [...document.querySelectorAll("#product-sales tbody tr td:last-child")]; const sum = rows.reduce((acc, cell) => acc + parseFloat(cell.textContent), 0); return Math.abs(sum - 15000) < 0.01; })()',
                ],
            },
            {
                "brief": "Introduce a currency select #currency-picker that converts the computed total using rates.json from attachments and mirrors the active currency inside #total-currency.",
                "checks": [
                    "js: !!document.querySelector(\"#currency-picker option[value='USD']\")",
                    'js: !!document.querySelector("#total-currency")',
                ],
                "attachments": [
                    {
                        "name": "rates.json",
                        "url": "data:application/json;base64,eyJVU0QiOjEsIkVVUiI6MC44NX0=",
                    }
                ],
            },
            {
                "brief": "Allow filtering by region via #region-filter, update #total-sales with the filtered sum, and set data-region on that element to the active choice.",
                "checks": [
                    'js: document.querySelector("#region-filter").tagName === "SELECT"',
                    'js: document.querySelector("#total-sales").dataset.region !== undefined',
                ],
            },
        ]
    elif example_name == "GitHub User Created":
        return [
            {
                "brief": "Show an aria-live alert #github-status that reports when a lookup starts, succeeds, or fails.",
                "checks": [
                    'js: document.querySelector("#github-status").getAttribute("aria-live") === "polite"',
                    'js: !!document.querySelector("script").textContent.includes("github-status")',
                ],
            },
            {
                "brief": "Display the account age in whole years inside #github-account-age alongside the creation date.",
                "checks": [
                    'js: parseInt(document.querySelector("#github-account-age").textContent, 10) >= 0',
                    'js: document.querySelector("#github-account-age").textContent.toLowerCase().includes("years")',
                ],
            },
            {
                "brief": 'Cache the last successful lookup in localStorage under "github-user-abc123" and repopulate the form on load.',
                "checks": [
                    'js: !!document.querySelector("script").textContent.includes("localStorage.setItem(\\"github-user-abc123\\"")',
                    'js: !!document.querySelector("script").textContent.includes("localStorage.getItem(\\"github-user-abc123\\"")',
                ],
            },
        ]
    else:
        return []


def main():
    print("=" * 60)
    print("LLM Code Deployment System - Test Suite")
    print("=" * 60)
    print("\nMake sure the server is running (uv run main.py)")

    selected_request, example_name = select_test_example()
    if selected_request is None:
        return

    print(f"\nSelected: {example_name}")
    print("Press Enter to continue, or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return

    if not test_health():
        print("\n Server is not responding. Make sure it's running.")
        return

    print("\n\nStarting deployment test...")
    print("This will create a real GitHub repository and may take 30-60 seconds.")
    print("Press Enter to continue, or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return

    success = test_deployment(selected_request)

    if success:
        round2_examples = get_round2_examples(example_name)

        if round2_examples:
            print(
                f"\n\nThis example has {len(round2_examples)} Round 2 scenarios available."
            )
            print("Would you like to test Round 2 revisions? (y/n)")
            try:
                choice = input().strip().lower()
                if choice == "y":
                    for i, scenario in enumerate(round2_examples, 1):
                        print(f"\n\nRound 2 Scenario {i}/{len(round2_examples)}:")
                        print(f"Brief: {scenario['brief'][:80]}...")
                        print("Press Enter to test, or 's' to skip...")
                        try:
                            skip = input().strip().lower()
                            if skip != "s":
                                r2_request = selected_request.copy()
                                r2_request["brief"] = scenario["brief"]
                                r2_request["checks"] = scenario["checks"]
                                if "attachments" in scenario:
                                    r2_request["attachments"] = scenario["attachments"]
                                test_round_2(r2_request, scenario["brief"])
                        except KeyboardInterrupt:
                            print("\n\nSkipping remaining scenarios.")
                            break
            except KeyboardInterrupt:
                print("\n\nCancelled.")
        else:
            print("\n\nWould you like to test Round 2 (revision)? (y/n)")
            try:
                choice = input().strip().lower()
                if choice == "y":
                    test_round_2(selected_request)
            except KeyboardInterrupt:
                print("\n\nCancelled.")

    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
