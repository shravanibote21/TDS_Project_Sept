from flask import Flask, request, jsonify
from utils import (
    load_config,
    validate_config,
    validate_request,
    generate_app_code,
    create_or_update_repo,
    update_readme,
    notify_evaluation_api,
)
from utils.evidence import send_evidence_log
from utils.logger import get_logger

app = Flask(__name__)
logger = get_logger(__name__)


@app.route("/api-endpoint", methods=["POST"])
def handle_request():
    current_step = "initialization"
    data = None

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400

        current_step = "validation"
        is_valid, message = validate_request(data)
        if not is_valid:
            return jsonify({"status": "error", "message": message}), 400

        email = data.get("email", "")
        task = data.get("task", "")
        round_num = data.get("round", 1)
        nonce = data.get("nonce", "")
        brief = data.get("brief", "")
        checks = data.get("checks", [])
        evaluation_url = data.get("evaluation_url", "")
        attachments = data.get("attachments", [])

        logger.info(f"Processing request for %s, task: %s, round: %s", email, task, round_num)

        existing_code = ""
        if round_num > 1:
            current_step = "fetching existing code"
            try:
                from utils.github_manager import get_existing_code

                existing_code = get_existing_code(task)
                if existing_code:
                    logger.info("Fetched existing code from previous round")
                else:
                    logger.info("No existing code found for task '%s' (first-time or missing file)", task)
            except Exception as e:
                logger.warning("Could not fetch existing code: %s. Proceeding fresh.", str(e))

        current_step = "generating code"
        logger.info("Generating app code with LLM...")
        try:
            code_files = generate_app_code(
                brief, checks, attachments, existing_code, round_num
            )
        except Exception as e:
            return jsonify({"status": "error", "message": f"Code generation failed: {str(e)}"}), 500

        current_step = "creating/updating repository"
        logger.info("Creating/updating GitHub repository...")
        try:
            repo_info = create_or_update_repo(task, code_files, round_num)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Repository operation failed: {str(e)}"}), 500

        current_step = "updating README"
        logger.info("Updating README...")
        try:
            update_readme(
                repo_info["repo"],
                task,
                brief,
                repo_info["repo_url"],
                repo_info["pages_url"],
            )
        except Exception as e:
            logger.warning("README update failed: %s", str(e))

        current_step = "fetching commit info"
        try:
            commits = repo_info["repo"].get_commits()
            latest_commit_sha = commits[0].sha
        except Exception as e:
            logger.warning("Could not fetch commits: %s", str(e))
            latest_commit_sha = repo_info.get("commit_sha", "unknown")

        eval_data = {
            "email": email,
            "task": task,
            "round": round_num,
            "nonce": nonce,
            "repo_url": repo_info["repo_url"],
            "commit_sha": latest_commit_sha,
            "pages_url": repo_info["pages_url"],
        }

        current_step = "notifying evaluation API"
        logger.info("Notifying evaluation API...")
        notify_result = False
        try:
            notify_result = notify_evaluation_api(evaluation_url, eval_data)
        except Exception as e:
            logger.warning("Evaluation API notification failed: %s", str(e))

        response_data = {
            "status": "success",
            "repo_url": repo_info["repo_url"],
            "pages_url": repo_info["pages_url"],
            "commit_sha": latest_commit_sha,
        }

        if not notify_result:
            response_data["warning"] = "Failed to notify evaluation API after retries"

        try:
            send_evidence_log(data, response_data, request.remote_addr, request.url)
        except Exception as log_error:
            logger.warning("Failed to send evidence log: %s", str(log_error))

        return jsonify(response_data), 200

    except Exception as e:
        logger.exception("Error processing request at step '%s': %s", current_step, str(e))

        error_message = str(e)
        if current_step != "initialization":
            error_message = f"Failed at step '{current_step}': {error_message}"

        error_response = {
            "status": "error",
            "message": error_message,
        }

        if data and all(k in data for k in ["email", "task", "round", "nonce"]):
            error_response.update(
                {
                    "email": data["email"],
                    "task": data["task"],
                    "round": data["round"],
                    "nonce": data["nonce"],
                }
            )

        try:
            if data:
                send_evidence_log(data, error_response, request.remote_addr, request.url)
                logger.info("Error details logged for evidence")
        except Exception as log_error:
            logger.warning("Evidence log failed: %s", str(log_error))

        return jsonify(error_response), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


def main():
    validate_config()
    config = load_config()
    port = config.get("port", 5000)
    logger.info("Starting LLM Code Deployment API on port %s", port)
    logger.info("API endpoint: http://localhost:%s/api-endpoint", port)
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()
