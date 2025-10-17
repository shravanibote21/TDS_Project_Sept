# Calculator App (basic arithmetic operations)
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "'"${SECRET}"'",
    "task": "calculator-app-xyz789",
    "round": 1,
    "nonce": "test-nonce-123456",
    "brief": "Create a simple calculator web app that can perform basic arithmetic operations (addition, subtraction, multiplication, division). The interface should be clean and user-friendly with buttons for numbers 0-9 and operation symbols. Display the result clearly.",
    "checks": [
      "Repo has MIT license",
      "README.md is professional and complete",
      "Calculator UI is clean and intuitive",
      "All basic operations work correctly",
      "Result is displayed properly"
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'

# Sales Summary (CSV parsing, Bootstrap, sum calculation)
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "'"${SECRET}"'",
    "task": "sum-of-sales",
    "round": 1,
    "nonce": "sales-nonce-001",
    "brief": "Publish a single-page site that fetches data.csv from attachments, sums its sales column, sets the title to '\''Sales Summary 12345'\'', displays the total inside #total-sales, and loads Bootstrap 5 from jsdelivr.",
    "checks": [
      "js: document.title === '\''Sales Summary 12345'\''",
      "js: !!document.querySelector(\"link[href*='bootstrap']\")",
      "js: Math.abs(parseFloat(document.querySelector(\"#total-sales\").textContent) - 15000) < 0.01"
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
      {
        "name": "data.csv",
        "url": "data:text/csv;base64,cHJvZHVjdCxzYWxlcwpBLDUwMDAKQiwxMDAwMApDLDUwMDA="
      }
    ]
  }'

# GitHub User Created (API fetch, date formatting)
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "'"${SECRET}"'",
    "task": "github-user-created",
    "round": 1,
    "nonce": "github-nonce-001",
    "brief": "Publish a Bootstrap page with form id='\''github-user-abc123'\'' that fetches a GitHub username, optionally uses ?token=, and displays the account creation date in YYYY-MM-DD UTC inside #github-created-at.",
    "checks": [
      "js: document.querySelector(\"#github-user-abc123\").tagName === \"FORM\"",
      "js: document.querySelector(\"#github-created-at\").textContent.includes(\"20\")",
      "js: !!document.querySelector(\"script\").textContent.includes(\"https://api.github.com/users/\")"
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'

# Markdown to HTML (marked, highlight.js)
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "'"${SECRET}"'",
    "task": "markdown-to-html",
    "round": 1,
    "nonce": "md-nonce-001",
    "brief": "Publish a static page that converts input.md from attachments to HTML with marked, renders it inside #markdown-output, and loads highlight.js for code blocks.",
    "checks": [
      "js: !!document.querySelector(\"script[src*='marked']\")",
      "js: !!document.querySelector(\"script[src*='highlight.js']\")",
      "js: document.querySelector(\"#markdown-output\").innerHTML.includes(\"<h\")"
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
      {
        "name": "input.md",
        "url": "data:text/markdown;base64,IyBIZWxsbyBXb3JsZAoKVGhpcyBpcyBhIHNhbXBsZSBtYXJrZG93biBmaWxlLgoKYGBgYApjb2RlIGJsb2NrCmBgYAo="
      }
    ]
  }'

# Counter App (static, button increments value)
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "'"${SECRET}"'",
    "task": "counter-app",
    "round": 1,
    "nonce": "counter-nonce-001",
    "brief": "Publish a static page with a button #increment-btn and a number inside #counter-value that increments by 1 each time the button is clicked.",
    "checks": [
      "js: !!document.querySelector(\"#increment-btn\")",
      "js: !!document.querySelector(\"#counter-value\")",
      "js: (() => { const v = document.querySelector(\"#counter-value\"); const b = document.querySelector(\"#increment-btn\"); const before = parseInt(v.textContent, 10); b.click(); return parseInt(v.textContent, 10) === before + 1; })()"
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'

# Dark Mode Toggle (static, theme switch)
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "'"${SECRET}"'",
    "task": "dark-mode-toggle",
    "round": 1,
    "nonce": "darkmode-nonce-001",
    "brief": "Publish a static page with a toggle #dark-mode-toggle that switches the page between light and dark themes, updating the body class.",
    "checks": [
      "js: !!document.querySelector(\"#dark-mode-toggle\")",
      "js: (() => { const t = document.querySelector(\"#dark-mode-toggle\"); const b = document.body; t.click(); return b.classList.contains(\"dark\"); })()"
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'
