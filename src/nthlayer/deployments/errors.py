"""Deployment provider errors."""

from __future__ import annotations

from nthlayer.core.errors import ProviderError


class DeploymentProviderError(ProviderError):
    """Raised when a deployment provider encounters an error."""
