"""Base class and models for deployment detection providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class DeploymentEvent:
    """Provider-agnostic intermediate model between webhook and Deployment."""

    service: str
    commit_sha: str
    environment: str = "production"
    author: str | None = None
    pr_number: str | None = None
    deployed_at: datetime | None = None
    source: str = ""
    extra_data: dict[str, Any] = field(default_factory=dict)


class BaseDeploymentProvider(ABC):
    """Abstract base class for deployment detection providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for identification."""

    @abstractmethod
    def verify_webhook(self, headers: dict[str, str], body: bytes) -> bool:
        """Verify webhook signature/authenticity. Return True if valid."""

    @abstractmethod
    def parse_webhook(
        self, headers: dict[str, str], payload: dict[str, Any]
    ) -> DeploymentEvent | None:
        """Parse webhook payload into DeploymentEvent.

        Return None to skip non-deployment events (e.g. non-deploy webhook types).
        """
