"""GitHub Actions deployment detection provider."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime
from typing import Any

from nthlayer.deployments.base import BaseDeploymentProvider, DeploymentEvent
from nthlayer.deployments.registry import register_deployment_provider


class GithubDeploymentProvider(BaseDeploymentProvider):
    """Detects deployments from GitHub Actions webhook payloads."""

    def __init__(self, webhook_secret: str | None = None) -> None:
        self._webhook_secret = webhook_secret

    @property
    def name(self) -> str:
        return "github"

    def verify_webhook(self, headers: dict[str, str], body: bytes) -> bool:
        if self._webhook_secret is None:
            return True
        signature = headers.get("x-hub-signature-256", "")
        if not signature:
            return False
        expected = hmac.new(self._webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, f"sha256={expected}")

    def parse_webhook(
        self, headers: dict[str, str], payload: dict[str, Any]
    ) -> DeploymentEvent | None:
        action = payload.get("action", "")
        workflow_run = payload.get("workflow_run", {})
        conclusion = workflow_run.get("conclusion", "")

        if action != "completed" or conclusion != "success":
            return None

        repository = payload.get("repository", {})
        sender = payload.get("sender", {})

        service = repository.get("name", "unknown")
        commit_sha = workflow_run.get("head_sha", "unknown")
        login = sender.get("login")
        author = f"{login}@github.com" if login else None
        deployed_at_str = workflow_run.get("created_at")

        deployed_at = (
            datetime.fromisoformat(deployed_at_str.replace("Z", "+00:00"))
            if deployed_at_str
            else None
        )

        pr_number = None
        pull_requests = workflow_run.get("pull_requests", [])
        if pull_requests:
            pr_number = str(pull_requests[0].get("number"))

        return DeploymentEvent(
            service=service,
            commit_sha=commit_sha,
            environment="production",
            author=author,
            pr_number=pr_number,
            deployed_at=deployed_at,
            source="github-actions",
            extra_data={
                "workflow_name": workflow_run.get("name"),
                "conclusion": conclusion,
            },
        )


register_deployment_provider("github", GithubDeploymentProvider())
