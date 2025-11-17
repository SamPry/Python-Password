"""Password router exposing validation/generation endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models.request_schemas import FullRequest, GenerateRequest, PasswordRequest
from ..models.response_schemas import (
    FullResponse,
    GeneratedPasswordResponse,
    StrengthResponse,
    ValidationResponse,
)
from ..services import password_service

router = APIRouter(prefix="/password", tags=["password"])


@router.post("/validate", response_model=ValidationResponse)
async def validate_password(request: PasswordRequest) -> ValidationResponse:
    result = password_service.validate_flow(request.password)
    return ValidationResponse(**result.__dict__, overall_result=result.overall_result)


@router.post("/generate", response_model=GeneratedPasswordResponse)
async def generate_password(request: GenerateRequest) -> GeneratedPasswordResponse:
    try:
        password = password_service.generate_flow(request.length)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return GeneratedPasswordResponse(password=password)


@router.post("/strength", response_model=StrengthResponse)
async def strength(request: PasswordRequest) -> StrengthResponse:
    result = password_service.strength_flow(request.password)
    return StrengthResponse(**result.__dict__)


@router.post("/full", response_model=FullResponse)
async def full_analysis(request: FullRequest) -> FullResponse:
    try:
        password, validation, strength = password_service.full_flow(
            password=request.password,
            length=request.length,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return FullResponse(
        password=password if request.password is None else None,
        validation=ValidationResponse(
            **validation.__dict__,
            overall_result=validation.overall_result,
        ),
        strength=StrengthResponse(**strength.__dict__),
    )
