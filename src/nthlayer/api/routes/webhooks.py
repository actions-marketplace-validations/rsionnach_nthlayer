"""Webhook routes for deployment detection."""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from nthlayer.api.deps import session_dependency
from nthlayer.deployments.errors import DeploymentProviderError
from nthlayer.deployments.registry import get_deployment_provider
from nthlayer.slos.deployment import DeploymentRecorder
from nthlayer.slos.storage import SLORepository

router = APIRouter()
logger = structlog.get_logger()


class WebhookResponse(BaseModel):
    deployment_id: str
    service: str
    source: str


@router.post(
    "/webhooks/deployments/{provider_name}",
    status_code=status.HTTP_201_CREATED,
    response_model=WebhookResponse,
    responses={
        204: {"description": "Event skipped (non-deployment)"},
        401: {"description": "Invalid webhook signature"},
        404: {"description": "Unknown provider"},
    },
)
async def receive_deployment_webhook(
    provider_name: str,
    request: Request,
    session: AsyncSession = Depends(session_dependency),  # noqa: B008
) -> WebhookResponse:
    """Receive a deployment webhook and record the event."""
    # Ensure providers are imported so self-registration runs
    import nthlayer.deployments.providers  # noqa: F401

    try:
        provider = get_deployment_provider(provider_name)
    except DeploymentProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown deployment provider: {provider_name}",
        ) from exc

    body = await request.body()
    headers = {k.lower(): v for k, v in request.headers.items()}

    if not provider.verify_webhook(headers, body):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    payload = await request.json()
    event = provider.parse_webhook(headers, payload)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
        )

    repository = SLORepository(session)
    recorder = DeploymentRecorder(repository)
    deployment = await recorder.record_event(event)
    await session.commit()

    logger.info(
        "deployment_webhook_recorded",
        provider=provider_name,
        deployment_id=deployment.id,
        service=deployment.service,
    )

    return WebhookResponse(
        deployment_id=deployment.id,
        service=deployment.service,
        source=deployment.source,
    )
