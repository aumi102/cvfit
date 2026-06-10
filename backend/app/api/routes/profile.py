from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import CareerProfileItem, User
from app.db.session import get_db
from app.schemas.phase5 import (
    CareerProfileItemCreate,
    CareerProfileItemListResponse,
    CareerProfileItemResponse,
    CareerProfileItemUpdate,
)

router = APIRouter(prefix="/v1/profile", tags=["profile"])


def _item_to_response(item: CareerProfileItem) -> CareerProfileItemResponse:
    return CareerProfileItemResponse(
        id=str(item.id),
        user_id=str(item.user_id),
        item_type=item.item_type,
        title=item.title,
        description=item.description,
        skills_json=item.skills_json,
        evidence_text=item.evidence_text,
        source=item.source,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _get_owned_item(
    item_id: uuid.UUID,
    current_user: User,
    db: Session,
) -> CareerProfileItem:
    item = db.get(CareerProfileItem, item_id)
    if item is None or item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profile item not found")
    return item


@router.post("/items", status_code=status.HTTP_201_CREATED, response_model=CareerProfileItemResponse)
def create_profile_item(
    body: CareerProfileItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> CareerProfileItemResponse:
    item = CareerProfileItem(
        id=uuid.uuid4(),
        user_id=current_user.id,
        item_type=body.item_type,
        title=body.title,
        description=body.description,
        skills_json=body.skills_json,
        evidence_text=body.evidence_text,
        source=body.source,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _item_to_response(item)


@router.get("/items", response_model=CareerProfileItemListResponse)
def list_profile_items(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    item_type: Optional[str] = Query(default=None),
) -> CareerProfileItemListResponse:
    q = db.query(CareerProfileItem).filter(CareerProfileItem.user_id == current_user.id)
    if item_type is not None:
        q = q.filter(CareerProfileItem.item_type == item_type)
    items = q.order_by(CareerProfileItem.created_at.desc()).all()
    responses = [_item_to_response(i) for i in items]
    return CareerProfileItemListResponse(items=responses, total=len(responses))


@router.get("/items/{item_id}", response_model=CareerProfileItemResponse)
def get_profile_item(
    item_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> CareerProfileItemResponse:
    item = _get_owned_item(item_id, current_user, db)
    return _item_to_response(item)


@router.patch("/items/{item_id}", response_model=CareerProfileItemResponse)
def patch_profile_item(
    item_id: uuid.UUID,
    body: CareerProfileItemUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> CareerProfileItemResponse:
    item = _get_owned_item(item_id, current_user, db)

    if body.item_type is not None:
        item.item_type = body.item_type
    if body.title is not None:
        item.title = body.title
    if body.description is not None:
        item.description = body.description
    if body.skills_json is not None:
        item.skills_json = body.skills_json
    if body.evidence_text is not None:
        item.evidence_text = body.evidence_text
    if body.source is not None:
        item.source = body.source
    item.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(item)
    return _item_to_response(item)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_profile_item(
    item_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> None:
    item = _get_owned_item(item_id, current_user, db)
    db.delete(item)
    db.commit()
