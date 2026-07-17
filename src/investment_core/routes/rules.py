from __future__ import annotations

from fastapi import APIRouter, Depends

from investment_core.dependencies import get_storage
from investment_core.models import RuleProfile
from investment_core.storage import Storage

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


@router.get("/profile")
def get_profile(storage: Storage = Depends(get_storage)) -> RuleProfile:
    return storage.get_rule_profile()


@router.put("/profile")
def update_profile(profile: RuleProfile, storage: Storage = Depends(get_storage)) -> RuleProfile:
    return storage.save_rule_profile(profile)
