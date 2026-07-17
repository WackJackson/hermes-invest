from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from investment_core.dependencies import get_storage
from investment_core.models import HoldingRecord
from investment_core.services.importer import parse_holdings_upload
from investment_core.storage import Storage

router = APIRouter(prefix="/api/v1/holdings", tags=["holdings"])


@router.post("/import")
async def import_holdings(
    file: UploadFile = File(...),
    storage: Storage = Depends(get_storage),
) -> dict[str, int]:
    content = await file.read()
    try:
        records = parse_holdings_upload(file.filename or "holdings.csv", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    imported = storage.replace_holdings(records)
    return {"imported": imported}


@router.get("")
def list_holdings(storage: Storage = Depends(get_storage)) -> list[HoldingRecord]:
    return storage.list_holdings()
