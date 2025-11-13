from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
from db import get_db

router = APIRouter()


@router.get("/products/", response_model=List[schemas.ProductRead])
def read_products(
        db: Session = Depends(get_db),
        search: Optional[str] = Query(None),
        brand: Optional[str] = None,
        model: Optional[str] = None,
        season: Optional[str] = None,
):
    query = db.query(models.Product)

    if search:
        like_str = f"%{search}%"
        query = query.filter(
            models.Product.brand.ilike(like_str)
            | models.Product.model.ilike(like_str)
            | models.Product.note.ilike(like_str)
        )
    if brand:
        query = query.filter(models.Product.brand == brand)
    if model:
        query = query.filter(models.Product.model == model)
    if season:
        query = query.filter(models.Product.season == season)

    return query.all()


@router.post("/products/", response_model=schemas.ProductRead)
def create_product(item: schemas.ProductCreate, db: Session = Depends(get_db)):
    obj = models.Product(**item.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/products/{id}", response_model=schemas.ProductRead)
def update_product(id: int, item: schemas.ProductCreate, db: Session = Depends(get_db)):
    obj = db.query(models.Product).get(id)
    for key, value in item.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Product).get(id)
    db.delete(obj)
    db.commit()
    return {"ok": True}
