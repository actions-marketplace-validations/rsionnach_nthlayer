"""Tests for provider-agnostic deployment detection.

Covers: providers, registry, DeploymentRecorder.record_event, and webhook route.
"""

from __future__ import annotations

import hashlib
import hmac
from unittest.mock import AsyncMock, MagicMock

import pytest
from nthlayer.deployments.base import DeploymentEvent
from nthlayer.deployments.errors import DeploymentProviderError
from nthlayer.deployments.providers.argocd import ArgocdDeploymentProvider
from nthlayer.deployments.providers.github import GithubDeploymentProvider
from nthlayer.deployments.providers.gitlab import GitlabDeploymentProvider
from nthlayer.deployments.registry import DeploymentProviderRegistry
from nthlayer.slos.deployment import DeploymentRecorder

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.create_deployment = AsyncMock()
    return repo


@pytest.fixture
def argocd_payload():
    return {
        "type": "app.sync.succeeded",
        "app": {
            "metadata": {"name": "order-service"},
            "spec": {"source": {"targetRevision": "abc123def456789012345678901234567890abcd"}},
        },
        "timestamp": "2025-06-15T10:30:00Z",
    }


@pytest.fixture
def github_payload():
    return {
        "action": "completed",
        "workflow_run": {
            "name": "Deploy to Production",
            "head_sha": "def456abc789012345678901234567890abcdef01",
            "conclusion": "success",
            "created_at": "2025-06-15T11:00:00Z",
            "pull_requests": [{"number": 42}],
        },
        "repository": {"name": "payment-service"},
        "sender": {"login": "developer"},
    }


@pytest.fixture
def gitlab_payload():
    return {
        "object_kind": "pipeline",
        "object_attributes": {
            "id": 12345,
            "status": "success",
            "ref": "main",
            "sha": "aaa111bbb222ccc333ddd444eee555fff666777a",
            "finished_at": "2025-06-15T12:00:00Z",
        },
        "project": {"name": "inventory-service"},
        "commit": {
            "id": "aaa111bbb222ccc333ddd444eee555fff666777a",
            "author": {"name": "alice"},
        },
        "user": {"username": "alice"},
    }


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestDeploymentProviderRegistry:
    def test_register_and_get(self):
        registry = DeploymentProviderRegistry()
        provider = ArgocdDeploymentProvider()
        registry.register("argocd", provider)

        assert registry.get("argocd") is provider

    def test_get_unknown_raises(self):
        registry = DeploymentProviderRegistry()

        with pytest.raises(DeploymentProviderError, match="not registered"):
            registry.get("nope")

    def test_register_empty_name_raises(self):
        registry = DeploymentProviderRegistry()

        with pytest.raises(ValueError, match="required"):
            registry.register("", ArgocdDeploymentProvider())

    def test_list(self):
        registry = DeploymentProviderRegistry()
        registry.register("a", ArgocdDeploymentProvider())
        registry.register("b", GithubDeploymentProvider())

        assert sorted(registry.list()) == ["a", "b"]


# ---------------------------------------------------------------------------
# ArgoCD provider
# ---------------------------------------------------------------------------


class TestArgocdProvider:
    def test_name(self):
        assert ArgocdDeploymentProvider().name == "argocd"

    def test_parse_sync_succeeded(self, argocd_payload):
        provider = ArgocdDeploymentProvider()
        event = provider.parse_webhook({}, argocd_payload)

        assert event is not None
        assert event.service == "order-service"
        assert event.commit_sha == "abc123def456789012345678901234567890abcd"
        assert event.source == "argocd"
        assert event.extra_data["sync_type"] == "app.sync.succeeded"
        assert event.deployed_at is not None

    def test_parse_non_deploy_event_returns_none(self):
        provider = ArgocdDeploymentProvider()
        payload = {"type": "app.sync.failed", "app": {}}

        assert provider.parse_webhook({}, payload) is None

    def test_parse_missing_fields(self):
        provider = ArgocdDeploymentProvider()
        payload = {"type": "app.sync.succeeded"}

        event = provider.parse_webhook({}, payload)
        assert event is not None
        assert event.service == "unknown"
        assert event.commit_sha == "unknown"
        assert event.deployed_at is None

    def test_verify_no_secret_always_passes(self):
        provider = ArgocdDeploymentProvider(webhook_secret=None)
        assert provider.verify_webhook({}, b"anything") is True

    def test_verify_valid_signature(self):
        secret = "my-secret"
        body = b'{"type":"app.sync.succeeded"}'
        sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        provider = ArgocdDeploymentProvider(webhook_secret=secret)
        assert provider.verify_webhook({"x-argo-signature": f"sha256={sig}"}, body) is True

    def test_verify_invalid_signature(self):
        provider = ArgocdDeploymentProvider(webhook_secret="my-secret")
        assert provider.verify_webhook({"x-argo-signature": "sha256=bad"}, b"body") is False

    def test_verify_missing_signature_header(self):
        provider = ArgocdDeploymentProvider(webhook_secret="my-secret")
        assert provider.verify_webhook({}, b"body") is False


# ---------------------------------------------------------------------------
# GitHub provider
# ---------------------------------------------------------------------------


class TestGithubProvider:
    def test_name(self):
        assert GithubDeploymentProvider().name == "github"

    def test_parse_successful_workflow(self, github_payload):
        provider = GithubDeploymentProvider()
        event = provider.parse_webhook({}, github_payload)

        assert event is not None
        assert event.service == "payment-service"
        assert event.commit_sha == "def456abc789012345678901234567890abcdef01"
        assert event.author == "developer@github.com"
        assert event.pr_number == "42"
        assert event.source == "github-actions"
        assert event.extra_data["workflow_name"] == "Deploy to Production"
        assert event.extra_data["conclusion"] == "success"

    def test_parse_non_completed_action_returns_none(self, github_payload):
        provider = GithubDeploymentProvider()
        github_payload["action"] = "requested"

        assert provider.parse_webhook({}, github_payload) is None

    def test_parse_failed_conclusion_returns_none(self, github_payload):
        provider = GithubDeploymentProvider()
        github_payload["workflow_run"]["conclusion"] = "failure"

        assert provider.parse_webhook({}, github_payload) is None

    def test_parse_no_pr(self, github_payload):
        provider = GithubDeploymentProvider()
        github_payload["workflow_run"]["pull_requests"] = []

        event = provider.parse_webhook({}, github_payload)
        assert event is not None
        assert event.pr_number is None

    def test_parse_no_sender_login(self, github_payload):
        provider = GithubDeploymentProvider()
        github_payload["sender"] = {}

        event = provider.parse_webhook({}, github_payload)
        assert event is not None
        assert event.author is None

    def test_verify_no_secret_always_passes(self):
        provider = GithubDeploymentProvider(webhook_secret=None)
        assert provider.verify_webhook({}, b"anything") is True

    def test_verify_valid_signature(self):
        secret = "gh-secret"
        body = b'{"action":"completed"}'
        sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        provider = GithubDeploymentProvider(webhook_secret=secret)
        assert provider.verify_webhook({"x-hub-signature-256": f"sha256={sig}"}, body) is True

    def test_verify_invalid_signature(self):
        provider = GithubDeploymentProvider(webhook_secret="gh-secret")
        assert provider.verify_webhook({"x-hub-signature-256": "sha256=wrong"}, b"body") is False

    def test_verify_missing_signature_header(self):
        provider = GithubDeploymentProvider(webhook_secret="gh-secret")
        assert provider.verify_webhook({}, b"body") is False


# ---------------------------------------------------------------------------
# GitLab provider
# ---------------------------------------------------------------------------


class TestGitlabProvider:
    def test_name(self):
        assert GitlabDeploymentProvider().name == "gitlab"

    def test_parse_successful_pipeline(self, gitlab_payload):
        provider = GitlabDeploymentProvider()
        event = provider.parse_webhook({}, gitlab_payload)

        assert event is not None
        assert event.service == "inventory-service"
        assert event.commit_sha == "aaa111bbb222ccc333ddd444eee555fff666777a"
        assert event.author == "alice"
        assert event.source == "gitlab-ci"
        assert event.extra_data["pipeline_id"] == 12345
        assert event.extra_data["ref"] == "main"

    def test_parse_non_pipeline_event_returns_none(self, gitlab_payload):
        provider = GitlabDeploymentProvider()
        gitlab_payload["object_kind"] = "push"

        assert provider.parse_webhook({}, gitlab_payload) is None

    def test_parse_failed_pipeline_returns_none(self, gitlab_payload):
        provider = GitlabDeploymentProvider()
        gitlab_payload["object_attributes"]["status"] = "failed"

        assert provider.parse_webhook({}, gitlab_payload) is None

    def test_parse_non_main_ref_returns_none(self, gitlab_payload):
        provider = GitlabDeploymentProvider()
        gitlab_payload["object_attributes"]["ref"] = "feature-branch"

        assert provider.parse_webhook({}, gitlab_payload) is None

    def test_parse_master_ref_accepted(self, gitlab_payload):
        provider = GitlabDeploymentProvider()
        gitlab_payload["object_attributes"]["ref"] = "master"

        event = provider.parse_webhook({}, gitlab_payload)
        assert event is not None

    def test_verify_no_secret_always_passes(self):
        provider = GitlabDeploymentProvider(webhook_secret=None)
        assert provider.verify_webhook({}, b"anything") is True

    def test_verify_valid_token(self):
        secret = "gl-token"
        provider = GitlabDeploymentProvider(webhook_secret=secret)
        assert provider.verify_webhook({"x-gitlab-token": secret}, b"") is True

    def test_verify_invalid_token(self):
        provider = GitlabDeploymentProvider(webhook_secret="gl-token")
        assert provider.verify_webhook({"x-gitlab-token": "wrong"}, b"") is False

    def test_verify_missing_token_header(self):
        provider = GitlabDeploymentProvider(webhook_secret="gl-token")
        assert provider.verify_webhook({}, b"") is False


# ---------------------------------------------------------------------------
# DeploymentRecorder.record_event
# ---------------------------------------------------------------------------


class TestRecordEvent:
    @pytest.mark.asyncio
    async def test_record_event(self, mock_repository):
        recorder = DeploymentRecorder(mock_repository)
        event = DeploymentEvent(
            service="my-service",
            commit_sha="abc123def456789012345678901234567890abcd",
            environment="staging",
            author="dev@example.com",
            pr_number="99",
            source="argocd",
            extra_data={"key": "val"},
        )

        deployment = await recorder.record_event(event)

        assert deployment.id == "argocd-abc123def456"
        assert deployment.service == "my-service"
        assert deployment.environment == "staging"
        assert deployment.commit_sha == "abc123def456789012345678901234567890abcd"
        assert deployment.author == "dev@example.com"
        assert deployment.pr_number == "99"
        assert deployment.source == "argocd"
        assert deployment.extra_data == {"key": "val"}
        mock_repository.create_deployment.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_event_defaults_deployed_at(self, mock_repository):
        recorder = DeploymentRecorder(mock_repository)
        event = DeploymentEvent(service="svc", commit_sha="aaa111bbb222", source="test")

        deployment = await recorder.record_event(event)

        assert deployment.deployed_at is not None


# ---------------------------------------------------------------------------
# Webhook route (end-to-end with TestClient)
# ---------------------------------------------------------------------------


class TestWebhookRoute:
    @pytest.fixture
    def app_client(self):
        """Create a TestClient for the webhook route."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from nthlayer.api.routes.webhooks import router

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        return TestClient(app)

    def test_unknown_provider_returns_404(self, app_client):
        resp = app_client.post(
            "/api/v1/webhooks/deployments/nonexistent",
            json={},
        )
        assert resp.status_code == 404

    def test_invalid_signature_returns_401(self, app_client):
        """ArgoCD provider with a secret should reject unsigned requests."""
        from nthlayer.deployments.providers.argocd import ArgocdDeploymentProvider
        from nthlayer.deployments.registry import deployment_registry

        # Replace with a provider that has a secret configured
        deployment_registry.register(
            "argocd-secure", ArgocdDeploymentProvider(webhook_secret="s3cret")
        )
        try:
            resp = app_client.post(
                "/api/v1/webhooks/deployments/argocd-secure",
                json={"type": "app.sync.succeeded"},
            )
            assert resp.status_code == 401
        finally:
            # Clean up
            deployment_registry._providers.pop("argocd-secure", None)

    def test_skipped_event_returns_204(self, app_client):
        """Non-deploy ArgoCD events should return 204."""
        resp = app_client.post(
            "/api/v1/webhooks/deployments/argocd",
            json={"type": "app.sync.failed", "app": {}},
        )
        assert resp.status_code == 204

    def test_successful_argocd_webhook(self, app_client, argocd_payload, monkeypatch):
        """Successful ArgoCD webhook returns 201."""
        # Patch SLORepository.create_deployment to avoid DB calls
        monkeypatch.setattr(
            "nthlayer.slos.storage.SLORepository.create_deployment",
            AsyncMock(),
        )
        resp = app_client.post(
            "/api/v1/webhooks/deployments/argocd",
            json=argocd_payload,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["service"] == "order-service"
        assert data["source"] == "argocd"
        assert "deployment_id" in data

    def test_successful_github_webhook(self, app_client, github_payload, monkeypatch):
        monkeypatch.setattr(
            "nthlayer.slos.storage.SLORepository.create_deployment",
            AsyncMock(),
        )
        resp = app_client.post(
            "/api/v1/webhooks/deployments/github",
            json=github_payload,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["service"] == "payment-service"
        assert data["source"] == "github-actions"

    def test_successful_gitlab_webhook(self, app_client, gitlab_payload, monkeypatch):
        monkeypatch.setattr(
            "nthlayer.slos.storage.SLORepository.create_deployment",
            AsyncMock(),
        )
        resp = app_client.post(
            "/api/v1/webhooks/deployments/gitlab",
            json=gitlab_payload,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["service"] == "inventory-service"
        assert data["source"] == "gitlab-ci"
