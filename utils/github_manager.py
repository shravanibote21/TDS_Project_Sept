from typing import Dict, Optional
import requests
import time
from github import GithubException
from .config import get_github_client, GITHUB_USERNAME, GITHUB_TOKEN
from .code_generator import generate_readme as generate_readme_content
from .asset_handler import process_html_assets
from requests import RequestException
from .logger import get_logger

logger = get_logger(__name__)


def get_existing_code(task: str, path: str = "index.html") -> Optional[str]:
    try:
        github_client = get_github_client()
        user = github_client.get_user()
        
        try:
            repo = user.get_repo(task)
        except GithubException as e:
            if e.status == 404:
                logger.info("Repository '%s' not found (first time is OK)", task)
                return None
            elif e.status == 403:
                logger.warning("Permission denied accessing repository '%s'", task)
                return None
            else:
                logger.warning("Error accessing repository '%s': %s", task, str(e))
                return None

        try:
            contents = repo.get_contents(path, ref="main")
            if hasattr(contents, "decoded_content"):
                decoded = contents.decoded_content.decode("utf-8")
                logger.info("Retrieved %s from %s (size: %s chars)", path, task, len(decoded))
                return decoded
            else:
                logger.info("File %s exists but has no content", path)
                return None
        except GithubException as e:
            if e.status == 404:
                logger.info("File '%s' not found in repository '%s' (OK)", path, task)
                return None
            else:
                logger.warning("Error fetching %s from %s: %s", path, task, str(e))
                return None
                
    except Exception as e:
        logger.warning("Unexpected error fetching existing code from %s: %s", task, str(e))
        return None


def get_mit_license() -> str:
    year = "2025"
    name = GITHUB_USERNAME or "Student"

    return f"""MIT License

Copyright (c) {year} {name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def create_or_update_repo(
    task: str, code_files: Dict[str, str], round_num: int
) -> Dict[str, str]:
    """
    Create or update a GitHub repository with app code.
    
    CONCURRENCY SAFETY:
    - Multiple requests with DIFFERENT task names → Safe (different repos)
    - Multiple requests with SAME task name → Safe due to:
        1. GitHub repo creation race condition handling (catches 422 "already exists")
        2. SHA-based conflict detection in upsert_pages_index (retries on conflicts)
    - Each Flask request runs in isolation, so local variables and return values
      are thread-safe (calculator request gets calculator URL, not counter URL)
    """
    try:
        github_client = get_github_client()
        user = github_client.get_user()
    except Exception as e:
        logger.error("Failed to authenticate with GitHub: %s", str(e))
        logger.error("Please check your GITHUB_TOKEN in .env file")
        raise

    repo_name = task
    owner = user.login

    repo = None
    existing_repo = None
    try:
        existing_repo = user.get_repo(repo_name)
        logger.info("Repository %s already exists, updating for round %s...", repo_name, round_num)
        repo = existing_repo
    except GithubException as e:
        if e.status == 404:
            logger.info("Creating new repository %s...", repo_name)
            try:
                repo = user.create_repo(
                    name=repo_name,
                    description=f"Generated app for task: {task}",
                    private=False,
                    auto_init=False,
                )
                logger.info("Repository %s created successfully", repo_name)

                try:
                    repo.create_file(
                        path="LICENSE",
                        message="Add MIT License",
                        content=get_mit_license(),
                    )
                    logger.info("LICENSE file created")
                except GithubException as license_error:
                    if license_error.status == 422:
                        logger.info("LICENSE already exists, skipping...")
                    else:
                        logger.warning("Could not create LICENSE: %s", str(license_error))

                try:
                    repo.create_file(
                        path="README.md",
                        message="Add README",
                        content=f"# {task}\n\nGenerated application for {task}",
                    )
                    logger.info("README.md created")
                except GithubException as readme_error:
                    if readme_error.status == 422:
                        logger.info("README.md already exists, will be updated later...")
                    else:
                        logger.warning("Could not create README: %s", str(readme_error))

            except GithubException as create_error:
                if (
                    create_error.status == 422
                    and "name already exists" in str(create_error).lower()
                ):
                    logger.info("Repository %s was just created by another process, fetching it...", repo_name)
                    try:
                        repo = user.get_repo(repo_name)
                    except GithubException as fetch_error:
                        raise RuntimeError(
                            f"Repository creation race condition: cannot fetch {repo_name} after failed create. {str(fetch_error)}"
                        )
                else:
                    raise RuntimeError(f"Failed to create repository: {str(create_error)}")
        else:
            raise RuntimeError(f"Failed to check repository existence: {str(e)}")

    if repo is None:
        raise RuntimeError(f"Failed to get or create repository {repo_name}")

    index_content = code_files.get(
        "index.html", "<html><body><h1>Welcome</h1></body></html>"
    )

    logger.info("Processing HTML assets (extracting large base64 data URIs)...")
    try:
        index_content = process_html_assets(index_content, repo, round_num)
    except Exception as e:
        logger.warning("Asset processing failed: %s", str(e))
        logger.info("Continuing with original HTML (data URIs intact)...")

    try:
        upsert_pages_index(
            owner=owner,
            repo_name=repo_name,
            html=index_content,
            branch="main",
            path="index.html",
            commit_msg=f"Deploy app for round {round_num}",
        )
    except Exception as e:
        logger.warning("Error during Pages setup: %s", str(e))
        logger.info("Continuing despite Pages setup issues (file should be uploaded)...")

    try:
        commits = repo.get_commits()
        latest_commit_sha = commits[0].sha
    except Exception as e:
        logger.warning("Could not fetch latest commit: %s", str(e))
        latest_commit_sha = "unknown"

    pages_url = f"https://{owner}.github.io/{repo_name}/"

    return {
        "repo_url": repo.html_url,
        "commit_sha": latest_commit_sha,
        "pages_url": pages_url,
        "repo": repo,
    }


def upsert_pages_index(
    owner: str,
    repo_name: str,
    html: str,
    branch: str = "main",
    path: str = "index.html",
    commit_msg: Optional[str] = None,
) -> None:
    commit_msg = commit_msg or f"Update {path} for GitHub Pages"

    gh = get_github_client()
    repo = gh.get_repo(f"{owner}/{repo_name}")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            contents = repo.get_contents(path, ref=branch)
            repo.update_file(
                path=path,
                message=commit_msg,
                content=html,
                sha=contents.sha,
                branch=branch,
            )
            logger.info("%s updated on %s", path, branch)
            break 
        except GithubException as e:
            if getattr(e, "status", None) == 404 or "Not Found" in str(e):
                try:
                    repo.create_file(
                        path=path,
                        message=f"Add {path} for GitHub Pages",
                        content=html,
                        branch=branch,
                    )
                    logger.info("%s created on %s", path, branch)
                    break  
                except GithubException as create_error:
                    if create_error.status == 422 and "sha" in str(create_error).lower():
                        if attempt < max_retries - 1:
                            logger.info("File created concurrently, retrying update (attempt %s/%s)...", attempt + 2, max_retries)
                            time.sleep(1)
                            continue
                        else:
                            raise RuntimeError(f"Failed to create {path} after {max_retries} attempts due to concurrent operations")
                    else:
                        raise
            elif e.status == 409 or ("sha" in str(e).lower() and "does not match" in str(e).lower()):
                if attempt < max_retries - 1:
                    logger.info("SHA conflict detected (concurrent update), retrying (attempt %s/%s)...", attempt + 2, max_retries)
                    time.sleep(1)  
                    continue
                else:
                    raise RuntimeError(f"Failed to update {path} after {max_retries} attempts due to concurrent updates")
            else:
                raise

    base = "https://api.github.com"
    hdrs = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    max_retries = 3
    retry_delay = 2
    pages_configured = False
    
    for attempt in range(max_retries):
        try:
            r = requests.get(f"{base}/repos/{owner}/{repo_name}/pages", headers=hdrs, timeout=10)
            
            if r.status_code == 404:
                logger.info("GitHub Pages not found, creating (attempt %s/%s)...", attempt + 1, max_retries)
                body = {"source": {"branch": branch, "path": "/"}}
                cr = requests.post(
                    f"{base}/repos/{owner}/{repo_name}/pages", headers=hdrs, json=body, timeout=10
                )
                
                if cr.status_code in (201, 202):
                    logger.info("Pages site created successfully")
                    pages_configured = True
                    break  
                elif cr.status_code == 409:
                    logger.info("Pages site already exists (409 - concurrent)")
                    pages_configured = True
                    break 
                elif cr.status_code == 403:
                    logger.warning("Permission denied (403) for Pages: %s", cr.text)
                    break 
                else:
                    error_msg = f"Failed to create Pages site: {cr.status_code} {cr.text}"
                    if attempt < max_retries - 1:
                        logger.info("%s. Retrying in %s seconds...", error_msg, retry_delay)
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.warning("%s. File uploaded but Pages setup incomplete.", error_msg)
                        break
                        
            elif r.status_code == 200:
                logger.info("Pages site exists, ensuring correct configuration...")
                body = {"source": {"branch": branch, "path": "/"}}
                pr = requests.patch(
                    f"{base}/repos/{owner}/{repo_name}/pages", headers=hdrs, json=body, timeout=10
                )
                
                if pr.status_code in (200, 202, 204):
                    logger.info("Pages configuration confirmed/updated")
                    pages_configured = True
                    break  
                elif pr.status_code == 404:
                    logger.info("Pages deleted between checks, will retry creation...")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.warning("Could not update Pages config after retries. File is uploaded.")
                        break
                elif pr.status_code == 403:
                    logger.warning("Permission denied (403) updating Pages: %s", pr.text)
                    break 
                else:
                    error_msg = f"Failed to update Pages config: {pr.status_code} {pr.text}"
                    if attempt < max_retries - 1:
                        logger.info("%s. Retrying in %s seconds...", error_msg, retry_delay)
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.warning("%s. File uploaded but Pages update incomplete.", error_msg)
                        break
                        
            elif r.status_code == 403:
                logger.warning("Permission denied (403) querying Pages: %s", r.text)
                break 
            elif r.status_code == 401:
                raise RuntimeError(f"Authentication failed (401). Please check GITHUB_TOKEN. Details: {r.text}")
            else:
                error_msg = f"Unexpected response when querying Pages site: {r.status_code} {r.text}"
                if attempt < max_retries - 1:
                    logger.info("%s. Retrying in %s seconds...", error_msg, retry_delay)
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.warning("%s. File uploaded but Pages status unclear.", error_msg)
                    break
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                logger.info("Request timeout (attempt %s/%s). Retrying in %s seconds...", attempt + 1, max_retries, retry_delay)
                time.sleep(retry_delay)
                continue
            else:
                logger.warning("Request timeout after retries. File uploaded but Pages status unclear.")
                break
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                logger.info("Request error: %s (attempt %s/%s). Retrying in %s seconds...", str(e), attempt + 1, max_retries, retry_delay)
                time.sleep(retry_delay)
                continue
            else:
                logger.warning("Request error after retries: %s. File uploaded but Pages status unclear.", str(e))
                break

    # Request a fresh build and wait for it to complete
    # Note: The build request returns 201/202 immediately, but the actual build takes time
    if pages_configured:
        try:
            logger.info("Requesting Pages build...")
            br = requests.post(f"{base}/repos/{owner}/{repo_name}/pages/builds", headers=hdrs, timeout=10)
            
            if br.status_code in (201, 202):
                logger.info("Pages build started successfully. Waiting for Pages to become available...")
                def wait_for_github_pages(url: str, timeout: int = 600) -> bool:
                    logger.info("Waiting for GitHub Pages to become live at: %s", url)
                    start = time.time()

                    initial_wait = 30
                    time_elapsed = time.time() - start
                    if time_elapsed < timeout:
                        to_wait = min(initial_wait, timeout - time_elapsed)
                        if to_wait > 0:
                            logger.info("Initial wait for %s seconds before first check...", to_wait)
                            time.sleep(to_wait)

                    delay = 15  

                    while time.time() - start < timeout:
                        try:
                            r = requests.get(url, timeout=10)
                            if r.status_code == 200:
                                logger.info("GitHub Pages is live at: %s", url)
                                return True
                            else:
                                logger.info("Still building... (status: %s)", r.status_code)
                        except RequestException:
                            logger.info("Still building... (no response)")

                        remaining = timeout - (time.time() - start)
                        if remaining <= 0:
                            break
                        sleep_time = min(delay, remaining)
                        time.sleep(sleep_time)

                    logger.warning("Timeout: GitHub Pages did not go live within the expected time.")
                    return False

                try:
                    wait_for_github_pages(f"https://{owner}.github.io/{repo_name}/", timeout=300)
                except Exception as e:
                    logger.warning("Error while waiting for Pages: %s", str(e))
                logger.info("Pages build polling complete (may still be finalizing on GitHub's side)")
            else:
                logger.info("Pages build request returned %s: %s (non-critical)", br.status_code, br.text)
        except Exception as e:
            logger.info("Could not request Pages build (non-critical): %s", str(e))
            logger.info("Pages will build automatically in the background")


def update_readme(repo, task: str, brief: str, repo_url: str, pages_url: str):
    readme_content = generate_readme_content(task, brief, repo_url, pages_url)
    
    if not readme_content:
        logger.warning("No README content generated, skipping update")
        return

    try:
        readme_file = repo.get_contents("README.md")
        repo.update_file(
            path="README.md",
            message="Update README",
            content=readme_content,
            sha=readme_file.sha,
        )
    except GithubException as e:
        if e.status == 404:
            repo.create_file(path="README.md", message="Add README", content=readme_content)
        else:
            logger.warning("Could not update README: %s", str(e))


def test_github_manager():
    print("Testing GitHub Manager...")
    try:
        github_client = get_github_client()
        user = github_client.get_user()
        print(f"Authenticated as {user.login}")
    except Exception as e:
        print(f"Failed to authenticate with GitHub: {str(e)}")
        return

    task = "test-task"
    round_num = 1
    code_files = {"index.html": "<html><body><h1>Test App</h1></body></html>"}

    try:
        repo_info = create_or_update_repo(task, code_files, round_num)
        print(f"Repository URL: {repo_info['repo_url']}")
        print(f"Pages URL: {repo_info['pages_url']}")
        print(f"Latest Commit SHA: {repo_info['commit_sha']}")

        update_readme(
            repo_info["repo"],
            task,
            "This is a test brief.",
            repo_info["repo_url"],
            repo_info["pages_url"],
        )
        print("README updated successfully.")
    except Exception as e:
        print(f"Error during repository operations: {str(e)}")
