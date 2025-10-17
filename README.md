# LLM Code Deployment System

**Overview**
- Flask API that generates single‑page apps via an LLM and deploys to GitHub Pages.
- Entry: `main.py`; endpoint: `POST /api-endpoint`; health: `GET /health`.
- Uses OpenAI SDK (Gemini-compatible base URL), PyGithub, and `.env` for config.

**Setup**
- Python `>=3.12`, Git, and [uv](https://github.com/astral-sh/uv) installed.
- Clone the repo and `cd` into it.
- Optional: run `uv run check_config.py` to validate credentials.

**Install Dependencies**
- Preferred (uv): `uv sync`
- Alternative (pip): `pip install -r requirements.txt`

**Configure Environment Variables**
- Create `.env` in the project root with:
  - `GITHUB_TOKEN` — GitHub Personal Access Token (scopes: `repo`, `workflow`).
  - `GITHUB_USERNAME` — Your GitHub username.
  - `OPENAI_API_KEY` — Gemini API key (used via OpenAI SDK).
  - `SECRET` — Shared secret for request validation.
  - `PORT` — Optional, defaults to `5000`.
  - `AIPIPE_AKI_KEY` — Optional fallback API key for `aipipe.org`.

**Deploy On Vercel**
- Install CLI: `npm i -g vercel` and login: `vercel login`.
- Link and initialize the project: `vercel` (follow prompts).
- Add env vars (CLI or dashboard):
  - `vercel env add GITHUB_TOKEN`
  - `vercel env add GITHUB_USERNAME`
  - `vercel env add OPENAI_API_KEY`
  - `vercel env add SECRET`
  - `vercel env add PORT` (optional)
- Deploy to production: `vercel --prod`.
- Notes: `api/index.py` exposes the Flask `app` for Vercel; `vercel.json` configures routing.
