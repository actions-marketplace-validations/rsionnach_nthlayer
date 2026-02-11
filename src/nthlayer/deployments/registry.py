"""Registry for deployment detection providers."""

from __future__ import annotations

from nthlayer.deployments.base import BaseDeploymentProvider
from nthlayer.deployments.errors import DeploymentProviderError


class DeploymentProviderRegistry:
    """In-memory registry for deployment providers."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseDeploymentProvider] = {}

    def register(self, name: str, provider: BaseDeploymentProvider) -> None:
        if not name:
            raise ValueError("Provider name is required")
        self._providers[name] = provider

    def get(self, name: str) -> BaseDeploymentProvider:
        provider = self._providers.get(name)
        if provider is None:
            raise DeploymentProviderError(
                f"Deployment provider '{name}' is not registered",
                details={"available": list(self._providers.keys())},
            )
        return provider

    def list(self) -> list[str]:
        return list(self._providers.keys())


deployment_registry = DeploymentProviderRegistry()


def register_deployment_provider(name: str, provider: BaseDeploymentProvider) -> None:
    deployment_registry.register(name, provider)


def get_deployment_provider(name: str) -> BaseDeploymentProvider:
    return deployment_registry.get(name)
