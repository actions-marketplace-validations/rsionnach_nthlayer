"""GitLab CI/CD deployment detection provider."""

from __future__ import annotations

import hmac
from datetime import datetime
from typing import Any

from nthlayer.deployments.base import BaseDeploymentProvider, DeploymentEvent
from nthlayer.deployments.registry import register_deployment_provider


class GitlabDeploymentProvider(BaseDeploymentProvider):
    """Detects deployments from GitLab CI/CD pipeline webhook payloads."""

    def __init__(self, webhook_secret: str | None = None) -> None:
        self._webhook_secret = webhook_secret

    @property
    def name(self) -> str:
        return "gitlab"

    def verify_webhook(self, headers: dict[str, str], body: bytes) -> bool:
        if self._webhook_secret is None:
            return True
        token = headers.get("x-gitlab-token", "")
        if not token:
            return False
        return hmac.compare_digest(token, self._webhook_secret)

    def parse_webhook(
        self, headers: dict[str, str], payload: dict[str, Any]
    ) -> DeploymentEvent | None:
        object_kind = payload.get("object_kind", "")
        if object_kind != "pipeline":
            return None

        object_attrs = payload.get("object_attributes", {})
        status = object_attrs.get("status", "")
        ref = object_attrs.get("ref", "")

        if status != "success" or ref not in ("main", "master"):
            return None

        project = payload.get("project", {})
        commit = payload.get("commit", {})
        user = payload.get("user", {})

        service = project.get("name", "unknown")
        commit_sha = commit.get("id", object_attrs.get("sha", "unknown"))
        author_name = user.get("username") or commit.get("author", {}).get("name")
        deployed_at_str = object_attrs.get("finished_at") or object_attrs.get("created_at")

        deployed_at = None
        if deployed_at_str:
            try:
                deployed_at = datetime.fromisoformat(deployed_at_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return DeploymentEvent(
            service=service,
            commit_sha=commit_sha,
            environment="production",
            author=author_name,
            deployed_at=deployed_at,
            source="gitlab-ci",
            extra_data={
                "pipeline_id": object_attrs.get("id"),
                "ref": ref,
            },
        )


register_deployment_provider("gitlab", GitlabDeploymentProvider())
