"""ArgoCD deployment detection provider."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime
from typing import Any

from nthlayer.deployments.base import BaseDeploymentProvider, DeploymentEvent
from nthlayer.deployments.registry import register_deployment_provider


class ArgocdDeploymentProvider(BaseDeploymentProvider):
    """Detects deployments from ArgoCD webhook payloads."""

    def __init__(self, webhook_secret: str | None = None) -> None:
        self._webhook_secret = webhook_secret

    @property
    def name(self) -> str:
        return "argocd"

    def verify_webhook(self, headers: dict[str, str], body: bytes) -> bool:
        if self._webhook_secret is None:
            return True
        signature = headers.get("x-argo-signature", "")
        if not signature:
            return False
        expected = hmac.new(self._webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, f"sha256={expected}")

    def parse_webhook(
        self, headers: dict[str, str], payload: dict[str, Any]
    ) -> DeploymentEvent | None:
        event_type = payload.get("type", "")
        if event_type != "app.sync.succeeded":
            return None

        app = payload.get("app", {})
        metadata = app.get("metadata", {})
        spec = app.get("spec", {})
        source = spec.get("source", {})

        service = metadata.get("name", "unknown")
        commit_sha = source.get("targetRevision", "unknown")
        deployed_at_str = payload.get("timestamp")

        deployed_at = (
            datetime.fromisoformat(deployed_at_str.replace("Z", "+00:00"))
            if deployed_at_str
            else None
        )

        return DeploymentEvent(
            service=service,
            commit_sha=commit_sha,
            environment="production",
            deployed_at=deployed_at,
            source="argocd",
            extra_data={"sync_type": event_type},
        )


register_deployment_provider("argocd", ArgocdDeploymentProvider())
