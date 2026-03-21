from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..services.runtime_service import RuntimeService, get_runtime_service

router = APIRouter(prefix="/runtime", tags=["Runtime"])
RuntimeDep = Annotated[RuntimeService, Depends(get_runtime_service)]


class RuntimeSkillResponse(BaseModel):
    name: str
    description: str
    scopes: list[str] = Field(default_factory=list)


class RuntimeSessionCreate(BaseModel):
    tenant_id: str


class RuntimeSessionResponse(BaseModel):
    tenant_id: str
    session_id: str
    created_at: str


class RuntimeAuthorizeRequest(BaseModel):
    tenant_id: str
    skill_name: str
    allowed_skills: list[str] = Field(default_factory=list)
    blocked_scopes: list[str] = Field(default_factory=list)


class RuntimeAuthorizeResponse(BaseModel):
    allowed: bool
    reason: str


@router.get("/skills", response_model=list[RuntimeSkillResponse])
async def list_runtime_skills(runtime_service: RuntimeDep):
    return [
        RuntimeSkillResponse(name=skill.name, description=skill.description, scopes=sorted(skill.scopes))
        for skill in runtime_service.list_skills()
    ]


@router.post("/sessions", response_model=RuntimeSessionResponse)
async def create_runtime_session(body: RuntimeSessionCreate, runtime_service: RuntimeDep):
    session = runtime_service.start_session(body.tenant_id)
    return RuntimeSessionResponse(tenant_id=session.tenant_id, session_id=session.session_id, created_at=session.created_at)


@router.post("/authorize", response_model=RuntimeAuthorizeResponse)
async def authorize_runtime_skill(body: RuntimeAuthorizeRequest, runtime_service: RuntimeDep):
    decision = runtime_service.authorize(
        tenant_id=body.tenant_id,
        skill_name=body.skill_name,
        allowed_skills=set(body.allowed_skills),
        blocked_scopes=set(body.blocked_scopes),
    )
    return RuntimeAuthorizeResponse(allowed=decision.allowed, reason=decision.reason)
