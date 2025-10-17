---
title: LLM Code Deployment System
emoji: 🐋
colorFrom: blue
colorTo: green
sdk: docker
python_version: "3.13"
app_file: main.py
pinned: false
---

# LLM Code Deployment System

An automated application deployment system that receives briefs, generates apps using LLMs, deploys them to GitHub Pages, and handles iterative updates.

## Overview

This project implements an automated workflow for building and deploying web applications:

1. **Build Phase**: Receives a brief, generates code using OpenAI, creates a GitHub repository, and deploys to GitHub Pages
2. **Revise Phase**: Accepts update requests, modifies existing code, and redeploys

## Features

- **LLM-Powered Code Generation**: Uses OpenAI GPT-4 to generate complete web applications
- **Automated GitHub Deployment**: Creates repositories, manages code, and enables GitHub Pages
- **Multi-Round Support**: Handles initial build and subsequent revision requests
- **Secret Verification**: Validates requests with a secret key
- **Professional Documentation**: Auto-generates README files and includes MIT License
- **Retry Logic**: Ensures evaluation API notifications with exponential backoff

## Setup Instructions

### 1. Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- GitHub account with a Personal Access Token
- OpenAI API key

### 2. Install Dependencies

```bash
# Install packages with uv
uv sync
```

All required packages are already defined in `pyproject.toml`.

### 3. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and set:

- `GITHUB_TOKEN`: Your GitHub Personal Access Token
  - Create at: <https://github.com/settings/personal-access-tokens/new>
  - Required scopes: `repo`, `workflow`, `admin:repo_hook`
- `GITHUB_USERNAME`: Your GitHub username
- `OPENAI_API_KEY`: Your GEMINI API key
  - Get from: <https://aistudio.google.com/api-keys>
  - Watch how to create one: <https://youtu.be/6BRyynZkvf0>
- `SECRET`: Your secret key for request verification
- `PORT`: (Optional) Server port, defaults to 5000
- `AIPIPE_AKI_KEY`: (Optional) AI Pipe API token for fallback when Gemini API fails
  - Generate from: <https://aipipe.org/login>
  - Login with Google account to get your token

### 4. GitHub Personal Access Token Setup

1. Go to <https://github.com/settings/tokens/new>
2. Give it a descriptive name (e.g., "LLM Deployment System")
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `admin:repo_hook` (Manage repository webhooks)
4. Click "Generate token" and copy it to your `.env` file

![Access Token](.github/assets/access_token.png)
![Permissions](.github/assets/permissions.png)

### 5. Verify Configuration

Before running the server, verify your configuration:

```bash
uv run check_config.py
```

This will:

- Check if all required environment variables are set
- Validate your GitHub token by authenticating
- Validate your OpenAI API key
- Display masked values for confirmation

If any issues are found, you'll get clear instructions on how to fix them.

## Usage

### Running the Server

```bash
uv run main.py
```

The server will start on `http://localhost:5000` (or the port specified in your `.env`).

### Run with Docker

Build the image and run the container (exposes port 5000 by default):

```bash
# Build
docker build -t llm-deploy:latest .

# Run (maps host 5000 -> container 5000)
docker run --env-file .env -p 5000:5000 llm-deploy:latest
```

Notes:

- The Docker image installs Python 3.13 and uv, copies `.env` early for better caching, and starts the app via `uv run main.py`.
- Override the port by setting `PORT` in your `.env` and mapping it accordingly, e.g. `-p 8080:8080`.

### Deploy to Vercel

You can deploy this application to Vercel for production hosting:

#### 1. Install Vercel CLI

```bash
npm i vercel -g
```

#### 2. Authenticate with Vercel

Run the following command and follow the prompts to authenticate. Create a Vercel account if you don't have one:

```bash
vercel
```

This will:
- Prompt you to log in or sign up
- Link your project to Vercel
- Set up the project configuration

#### 3. Test Locally with Vercel

Before deploying to production, test your app locally with Vercel's environment:

```bash
vercel dev
```

This starts a local development server that mimics Vercel's production environment.

#### 4. Deploy to Production

Once you're ready, deploy to production:

```bash
vercel --prod
```
## Optional
#### 5. Configure Environment Variables

After deploying, add your environment variables in the Vercel dashboard:

1. Go to your project settings on Vercel
2. Navigate to "Environment Variables"
3. Add the following variables:
   - `GITHUB_TOKEN`
   - `GITHUB_USERNAME`
   - `OPENAI_API_KEY`
   - `SECRET`
   - `PORT` (optional)

Alternatively, you can add environment variables via CLI:

```bash
vercel env add GITHUB_TOKEN
vercel env add GITHUB_USERNAME
vercel env add OPENAI_API_KEY
vercel env add SECRET
```

#### Notes

- Vercel will automatically detect the Python runtime from `requirements.txt`
- The `vercel.json` file configures routing and build settings
- Production URL will be provided after deployment
- Vercel provides automatic HTTPS and CDN

### Deploy to Hugging Face Spaces

Hugging Face Spaces provides free hosting for ML and web applications using Docker containers.

#### Method 1: Using Git (Recommended)

##### Step 1: Generate Hugging Face Token

1. Go to [Hugging Face Tokens](https://huggingface.co/settings/tokens)
2. Click **"New token"**
3. Name it (e.g., "deployment-token")
4. Select **"Write"** permission
5. Click **"Generate"** and copy the token

##### Step 2: Create New Space

1. Go to [Create New Space](https://huggingface.co/new-space?sdk=docker)
2. Choose a **Space name** (e.g., "llm-code-deployment")
3. Select **"Docker"** as SDK
4. Choose visibility (Public/Private)
5. Click **"Create Space"**

##### Step 3: Configure Space Secrets

1. Go to your Space settings: `https://huggingface.co/spaces/{username}/{spacename}/settings`
2. Scroll down to **"Repository secrets"** section
3. Add the following secrets one by one:
   - `GITHUB_TOKEN`: Your GitHub Personal Access Token
   - `GITHUB_USERNAME`: Your GitHub username
   - `OPENAI_API_KEY`: Your Gemini API key
   - `SECRET`: Your secret key for request verification
   - `AIPIPE_AKI_KEY`: Your AI Pipe API key (fallback)

![Space Secrets Configuration](.github/assets/space_secret.png)

##### Step 4: Deploy Using Git

Add Hugging Face remote and push:

```bash
git remote add hf https://huggingface.co/spaces/{username}/{spacename}
git add .
git commit -m "Deploy to Hugging Face Spaces"
git push hf main
```

If you encounter authentication issues, use your token:

```bash
git remote set-url hf https://{username}:{your_hf_token}@huggingface.co/spaces/{username}/{spacename}
git push hf main
```

#### Method 2: Using Hugging Face CLI

##### Step 1: Install Hugging Face CLI

```bash
pip install huggingface_hub
```

##### Step 2: Login

```bash
huggingface-cli login
```

Enter your Hugging Face token when prompted.

##### Step 3: Upload to Space

```bash
huggingface-cli upload {username}/{spacename} . --repo-type=space
```

#### Verify Deployment

1. Go to `https://huggingface.co/spaces/{username}/{spacename}`
2. Wait for the build to complete (usually 2-5 minutes)
3. Once running, your API will be available at:
   - `https://{username}-{spacename}.hf.space/api-endpoint`
   - `https://{username}-{spacename}.hf.space/health`

#### Space Configuration

The Space is configured via the YAML frontmatter in README.md:

```yaml
---
title: LLM Code Deployment System
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
python_version: "3.13"
app_file: main.py
pinned: false
---
```

Key parameters:
- **`sdk: docker`**: Uses the Dockerfile for deployment
- **`python_version`**: Python version (informational)
- **`app_file`**: Main application file
- **`title`** and **`emoji`**: Display information

For more configuration options, see [Hugging Face Spaces Config Reference](https://huggingface.co/docs/hub/spaces-config-reference).

#### Troubleshooting Spaces Deployment

**Build Fails:**
- Check Docker logs in the Space's "Logs" tab
- Verify all files are committed and pushed
- Ensure requirements.txt is present and valid

**App Not Starting:**
- Check that port 5000 is exposed in Dockerfile
- Verify environment secrets are set correctly
- Review application logs in Space dashboard

**Secrets Not Working:**
- Ensure secret names match exactly (case-sensitive)
- Restart the Space after adding secrets
- Check that secrets are in the correct format

**Git Push Fails:**
- Verify you have write access to the Space
- Check your token has "Write" permission
- Try re-authenticating with `huggingface-cli login`

### API Endpoints

#### POST `/api-endpoint`

Main endpoint for build and revise requests.

**Request Format:**

```json
{
  "email": "student@example.com",
  "secret": "your_secret_key",
  "task": "captcha-solver-xyz",
  "round": 1,
  "nonce": "ab12-cd34",
  "brief": "Create a captcha solver that handles ?url=https://.../image.png",
  "checks": [
    "Repo has MIT license",
    "README.md is professional",
    "Page displays captcha URL passed at ?url=...",
    "Page displays solved captcha text within 15 seconds"
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": [
    {
      "name": "sample.png",
      "url": "data:image/png;base64,iVBORw..."
    }
  ]
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Successfully processed round 1",
  "repo_url": "https://github.com/username/captcha-solver-xyz-round-1",
  "pages_url": "https://username.github.io/captcha-solver-xyz-round-1/",
  "commit_sha": "abc123def456"
}
```

#### GET `/health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

### Testing with cURL

```bash
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret_key",
    "task": "test-app-001",
    "round": 1,
    "nonce": "test-nonce-123",
    "brief": "Create a simple calculator app",
    "checks": [
      "Has MIT license",
      "README is professional",
      "Calculator works correctly"
    ],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

## Architecture

### Core Components

#### 1. Configuration Module (`utils/config.py`)
- **Environment Management**: Loads and validates configuration from `.env`
- **API Client Initialization**: 
  - Primary: Gemini API via `get_openai_client()`
  - Fallback: AI Pipe API via `get_fallback_client()`
- **GitHub Client**: Authenticates and manages GitHub API access
- **Config Validation**: Ensures all required credentials are present

#### 2. Request Handler (`main.py`)
- **Flask API Endpoint**: `/api-endpoint` for processing requests
- **Request Validation**: Uses `validate_request()` to verify required fields
- **Secret Verification**: Authenticates requests using shared secret
- **Step-by-Step Processing**: Orchestrates the entire workflow with error tracking
- **Health Check**: `/health` endpoint for monitoring

#### 3. Validation Module (`utils/validation.py`)
- **Request Validation**: Checks for required fields (email, secret, round, nonce, brief, evaluation_url)
- **Type Checking**: Validates data types (round must be int ≥ 1, attachments must be list)
- **Secret Verification**: Compares provided secret with configured secret
- **Good-to-have Fields**: Warns about missing optional fields (task, checks)

#### 4. File Handler (`utils/file_handler.py`)
- **Multi-Format Support**: Handles text, CSV, JSON, markdown, images, videos, audio, documents
- **Smart Content Detection**: Sends full content (≤20,000 chars) or preview based on size
- **Encoding Support**: Multiple encoding fallbacks (UTF-8, Latin-1, CP1252, ISO-8859-1, ASCII)
- **Base64 Decoding**: Robust decoding with automatic padding correction
- **Data URI Processing**: Extracts MIME types, decodes content, generates usage examples
- **File Type Detection**: Identifies text files, images, videos, audio, documents
- **Conversion Flags**: Marks files needing conversion (.md, .docx → HTML)

#### 5. Code Generator (`utils/code_generator.py`)
- **LLM Integration**: 
  - Primary: Gemini 2.5 Flash model
  - Fallback: GPT-4 via AI Pipe (automatic failover)
- **Attachment Processing**: Uses file_handler to process all attachment types
- **Prompt Engineering**: Creates detailed prompts with brief, checks, and attachment info
- **Round Support**: Handles both new generation and code updates
- **Content Extraction**: Removes markdown code blocks from LLM responses
- **README Generation**: Creates professional documentation using LLM

#### 6. GitHub Manager (`utils/github_manager.py`)
- **Repository Operations**:
  - Creates new repositories for round 1
  - Updates existing repositories for round 2+
  - Retrieves existing code from previous rounds
- **File Management**:
  - Creates/updates `index.html` with generated code
  - Adds MIT LICENSE automatically
  - Generates and updates README.md
- **GitHub Pages Setup**:
  - Enables Pages on main branch
  - Configures deployment source
  - Requests Pages build with retry logic
  - Handles race conditions and API errors
- **Error Handling**: Comprehensive retry logic for API failures

#### 7. API Notifier (`utils/api_notifier.py`)
- **Evaluation Notification**: POSTs results to evaluation URL
- **Retry Logic**: Exponential backoff (1, 2, 4, 8, 16 seconds)
- **Timeout Handling**: 30-second timeout per request
- **Error Recovery**: Up to 5 retry attempts
- **Status Reporting**: Logs all attempts and final status

### System Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     Incoming POST Request                   │
│                      /api-endpoint                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Request Validation & Authentication            │
│  - Check required fields (email, secret, round, etc.)       │
│  - Verify secret matches configured value                   │
│  - Validate data types and constraints                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Process Attachments                        │
│  - Load files from data URIs, URLs, or paths                │
│  - Decode base64 with multi-encoding support                │
│  - Extract metadata (MIME types, sizes, previews)           │
│  - Format for LLM prompt (full content or preview)          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            Fetch Existing Code (Round 2+)                   │
│  - Query GitHub for repository from previous round          │
│  - Retrieve index.html content                              │
│  - Include in prompt for code modification                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                Generate Code with LLM                       │
│  Primary: Gemini 2.5 Flash                                  │
│  ┌──────────────────────────────────────────┐               │
│  │ Prompt includes:                         │               │
│  │ - Brief and requirements                 │               │
│  │ - Evaluation checks                      │               │
│  │ - Attachment information                 │               │
│  │ - Existing code (if round 2+)            │               │
│  └──────────────────────────────────────────┘               │
│         │                                                   │
│         │ On Failure                                        │
│         ▼                                                   │
│  Fallback: GPT-4 via AI Pipe                                │
│  ┌──────────────────────────────────────────┐               │
│  │ Same prompt with alternative API         │              │
│  └──────────────────────────────────────────┘               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Create/Update GitHub Repository                │
│  Round 1:                          Round 2+:                │
│  - Create new repository           - Get existing repo      │
│  - Add LICENSE file                - Update index.html      │
│  - Create initial README           - Increment version      │
│  Round-independent:                                         │
│  - Upload/update index.html with generated code             │
│  - Commit changes with descriptive message                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Enable GitHub Pages                        │
│  - Check if Pages exists (GET /repos/{owner}/{repo}/pages)  │
│  - Create Pages if not exists (POST)                        │
│  - Update Pages config (PATCH)                              │
│  - Request Pages build                                      │
│  - Retry on failures with exponential backoff               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Generate & Update README                  │
│  - Create professional README using LLM                     │
│  - Include project description, features, usage             │
│  - Add repository and Pages URLs                            │
│  - Update or create README.md in repository                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Fetch Latest Commit SHA                    │
│  - Query repository for recent commits                      │
│  - Extract SHA from latest commit                           │
│  - Use for evaluation notification                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Notify Evaluation API                          │
│  - POST to evaluation_url with:                             │
│    * email, task, round, nonce                              │
│    * repo_url, pages_url, commit_sha                        │
│  - Retry up to 5 times with exponential backoff             │
│  - Log success/failure status                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Return Success Response                    │
│  {                                                          │
│    "status": "success",                                     │
│    "repo_url": "https://github.com/...",                    │
│    "pages_url": "https://username.github.io/...",           │
│    "commit_sha": "abc123..."                                │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

### Error Handling Strategy

- **Validation Errors**: Return HTTP 400 with specific error message
- **API Failures**: Automatic failover from Gemini to AI Pipe
- **GitHub Errors**: Retry logic with exponential backoff
- **Pages Setup Issues**: Continue with file upload even if Pages config fails
- **README Failures**: Log warning but continue with deployment
- **Evaluation API Errors**: Retry multiple times, mark as warning if all fail
- **Internal Errors**: Return HTTP 500 with error details and step information

## Round 2 (Revise) Handling

The system automatically handles Round 2 requests:

1. Detects `"round": 2` in the request
2. Finds the existing repository from Round 1
3. Generates updated code based on the new brief
4. Updates files in the repository
5. Regenerates README with new information
6. Notifies evaluation API with updated commit SHA

## Security Considerations

- Secret verification prevents unauthorized access
- No secrets stored in git history
- Environment variables for sensitive data
- `.env` file excluded from git (add to `.gitignore`)

## Error Handling

- Invalid requests return HTTP 400 with error details
- Internal errors return HTTP 500 with error messages
- Evaluation API failures trigger automatic retries
- All errors are logged to console for debugging

## Dependencies

Core libraries:

- `flask`: Web framework for API endpoint
- `openai`: LLM integration for code generation (supports Gemini and OpenAI-compatible APIs)
- `pygithub`: GitHub API client for repository management
- `requests`: HTTP client for evaluation API and GitHub Pages setup
- `python-dotenv`: Environment variable management
- `gunicorn`: Production WSGI server (Docker deployment)

## Limitations & Future Improvements

- Currently generates single-page HTML applications
- GitHub Pages may take 1-2 minutes to deploy
- Rate limits on OpenAI and GitHub APIs
- Could add support for multi-file projects
- Could implement caching for faster regeneration

## License

MIT License - see LICENSE file for details

## Troubleshooting

### GitHub Token Issues

- Ensure all required scopes are enabled
- Token must have `repo` access for public repositories
- Verify token hasn't expired

### OpenAI API Issues

- Check API key is valid and has credits
- Verify internet connectivity
- Review rate limits on your OpenAI account

### GitHub Pages Not Deploying

- Wait 1-2 minutes after creation
- Check repository settings → Pages section
- Ensure repository is public
- Verify `index.html` exists in main branch

### Port Already in Use

- Change `PORT` in `.env` file
- Or kill the process using: `lsof -ti:5000 | xargs kill -9`

## Submission

Once your API is deployed and working, submit your project details:

### Submission Form

Submit your deployment at: [Project Submission Form](https://docs.google.com/forms/d/e/1FAIpQLScInfLkTCeVow9Z-4LL3TjM8NuTX90akPxryCwHhDjUm6laaw/viewform?pli=1)

You will need to provide:

1. **What is the URL of your API?**
   - Format: `{deployed_link}/api-endpoint`
   - Example: `https://your-username-your-space.hf.space/api-endpoint`
   - Or: `https://your-project.vercel.app/api-endpoint`
   - Or: `http://your-domain.com:5000/api-endpoint`

2. **What "secret" value should we send your API?**
   - Use the same secret value you configured in your `.env` file
   - This is the `SECRET` environment variable
   - Keep it consistent with what your API expects

3. **What is the GitHub home page URL of your repo?**
   - Format: `https://github.com/{username}/{repo-name}`
   - Example: `https://github.com/23f2005217/project1-tds-t3-2025`
   - **Important**: Make your repository **PUBLIC** by the deadline
   - If concerned about copying, you can keep it private during development

![Submission Form](.github/assets/g_form.png)

### Before Submitting

Checklist:
- [ ] API is deployed and accessible at the provided URL
- [ ] `/health` endpoint returns `{"status": "healthy"}`
- [ ] `/api-endpoint` accepts POST requests with proper authentication
- [ ] Repository is PUBLIC on GitHub (or will be by deadline)
- [ ] All environment variables are properly configured as secrets
- [ ] Test with a sample request to ensure everything works

### Testing Your Deployment

Test your deployed API before submitting:

```bash
curl https://your-deployment-url.hf.space/health

curl https://your-deployment-url.hf.space/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret_here",
    "task": "test-deployment",
    "round": 1,
    "nonce": "test-123",
    "brief": "Create a simple test page",
    "checks": [],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

## Evidence & Logging

### Request/Response Tracking

All API requests and responses are automatically logged to a dedicated evidence storage system for verification and audit purposes:

**Evidence Dashboard**: [View Request/Response Logs](https://store-evidence.vercel.app/api/logs)

You can see the request/response details during the evaluation. **This solution is robust enough to cover all edge cases.** Still, if you get zero or less marks for some reason, you can use this information to argue with the evaluation or IITM team.

Each log entry includes:
- Complete request payload (email, task, round, brief, checks, attachments)
- Response data (repo_url, pages_url, commit_sha, status)
- Timestamp, client IP, and request URL
- Success/error status and messages

This logging is:
- **Asynchronous** - Doesn't slow down request processing
- **Non-intrusive** - Silent failures won't break the API
- **Comprehensive** - Captures every request for audit trail
- **Dispute-ready** - Evidence for evaluation disputes

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review error messages in console output
3. Verify all environment variables are set correctly
4. Ensure GitHub and OpenAI credentials are valid
5. Check the [evidence dashboard](https://store-evidence.vercel.app/api/logs) for logged requests#