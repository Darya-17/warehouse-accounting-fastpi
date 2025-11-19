from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from sqlalchemy import or_

import models
import schemas
from db import get_db

router = APIRouter()



@router.get("/products/", response_model=List[dict])
@router.get("/products", response_model=List[dict])
def get_products(db: Session = Depends(get_db)):
    warehouse = db.query(models.Warehouse).all()
    storage = db.query(models.Storage).all()
    products = db.query(models.Product).all()

    result = []
    for p in products:
        w_qty = sum(w.quantity for w in warehouse if w.product_id == p.id)
        s_qty = sum(s.quantity for s in storage if s.product_id == p.id)
        result.append({
            "id": p.id,
            "brand": p.brand,
            "model": p.model,
            "price": p.price,
            "warehouse_qty": w_qty,
            "storage_qty": s_qty,
        })
    return result


@router.post("/products/", response_model=schemas.ProductRead)
@router.post("/products", response_model=schemas.ProductRead)
def create_product(item: schemas.ProductCreate, db: Session = Depends(get_db)):
    obj = models.Product(**item.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/products/{id}", response_model=schemas.ProductRead)
@router.patch("/products/{id}/", response_model=schemas.ProductRead)
def update_product(id: int, item: schemas.ProductCreate, db: Session = Depends(get_db)):
    obj = db.query(models.Product).get(id)
    for key, value in item.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/products/{id}")
@router.delete("/products/{id}/")
def delete_product(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Product).get(id)
    db.delete(obj)
    db.commit()
    return {"ok": True}



@router.post("/tires/", response_model=schemas.TireRead)
@router.post("/tires", response_model=schemas.TireRead)
def create_tire(item: schemas.TireCreate, db: Session = Depends(get_db)):
    obj = models.Tire(**item.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tires/{id}", response_model=schemas.TireRead)
@router.put("/tires/{id}/", response_model=schemas.TireRead)
def update_tire(id: int, item: schemas.TireCreate, db: Session = Depends(get_db)):
    obj = db.query(models.Tire).get(id)
    for key, value in item.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tires/{id}")
@router.delete("/tires/{id}/")
def delete_tire(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Tire).get(id)
    db.delete(obj)
    db.commit()
    return {"ok": True}



@router.post("/components/", response_model=schemas.ComponentRead)
@router.post("/components", response_model=schemas.ComponentRead)
def create_component(item: schemas.ComponentCreate, db: Session = Depends(get_db)):
    obj = models.Component(**item.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/components/{id}", response_model=schemas.ComponentRead)
@router.put("/components/{id}/", response_model=schemas.ComponentRead)
def update_component(id: int, item: schemas.ComponentCreate, db: Session = Depends(get_db)):
    obj = db.query(models.Component).get(id)
    for key, value in item.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/components/{id}")
@router.delete("/components/{id}/")
def delete_component(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Component).get(id)
    db.delete(obj)
    db.commit()
    return {"ok": True}



@router.get("/warehouse/", response_model=List[schemas.WarehouseRead])
@router.get("/warehouse", response_model=List[schemas.WarehouseRead])
def read_warehouse(db: Session = Depends(get_db),
                   rack: Optional[str] = None,
                   shelf: Optional[str] = None,
                   cell: Optional[str] = None):
    query = db.query(models.Warehouse)
    if rack:
        query = query.filter(models.Warehouse.rack == rack)
    if shelf:
        query = query.filter(models.Warehouse.shelf == shelf)
    if cell:
        query = query.filter(models.Warehouse.cell == cell)
    return query.all()


@router.post("/warehouse/", response_model=schemas.WarehouseRead)
@router.post("/warehouse", response_model=schemas.WarehouseRead)
def create_warehouse(item: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    obj = models.Warehouse(**item.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/warehouse/{id}", response_model=schemas.WarehouseRead)
@router.put("/warehouse/{id}/", response_model=schemas.WarehouseRead)
def update_warehouse(id: int, item: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    obj = db.query(models.Warehouse).get(id)
    for key, value in item.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/warehouse/{id}")
@router.delete("/warehouse/{id}/")
def delete_warehouse(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Warehouse).get(id)
    db.delete(obj)
    db.commit()
    return {"ok": True}



@router.get("/storage/", response_model=List[schemas.StorageRead])
@router.get("/storage", response_model=List[schemas.StorageRead])
def read_storage(db: Session = Depends(get_db),
                 rack: Optional[str] = None,
                 shelf: Optional[str] = None,
                 cell: Optional[str] = None):
    query = db.query(models.Storage)
    if rack:
        query = query.filter(models.Storage.rack == rack)
    if shelf:
        query = query.filter(models.Storage.shelf == shelf)
    if cell:
        query = query.filter(models.Storage.cell == cell)
    return query.all()


@router.post("/storage/", response_model=schemas.StorageRead)
@router.post("/storage", response_model=schemas.StorageRead)
def create_storage(item: schemas.StorageCreate, db: Session = Depends(get_db)):
    obj = models.Storage(**item.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/storage/{id}", response_model=schemas.StorageRead)
@router.put("/storage/{id}/", response_model=schemas.StorageRead)
def update_storage(id: int, item: schemas.StorageCreate, db: Session = Depends(get_db)):
    obj = db.query(models.Storage).get(id)
    for key, value in item.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/storage/{id}")
@router.delete("/storage/{id}/")
def delete_storage(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Storage).get(id)
    db.delete(obj)
    db.commit()
    return {"ok": True}



@router.get("/orders/", response_model=List[schemas.OrderRead])
@router.get("/orders", response_model=List[schemas.OrderRead])
def read_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).options(joinedload(models.Order.items).joinedload(models.OrderItem.product)).all()
    return orders


@router.post("/orders/", response_model=schemas.OrderRead)
@router.post("/orders", response_model=schemas.OrderRead)
def create_order(item: schemas.OrderCreate, db: Session = Depends(get_db)):
    order_obj = models.Order(
        status=item.status or models.OrderStatusEnum.DRAFT,
        customer_name=item.customer_name,
        customer_phone=item.customer_phone,
        service=item.service
    )
    db.add(order_obj)
    db.commit()
    db.refresh(order_obj)

    for i in item.items:
        order_item_obj = models.OrderItem(
            order_id=order_obj.id,
            product_id=i.product_id,
            quantity=i.quantity,
            price=i.price
        )
        db.add(order_item_obj)
    db.commit()
    db.refresh(order_obj)
    return order_obj


@router.patch("/orders/{id}", response_model=schemas.OrderRead)
@router.patch("/orders/{id}/", response_model=schemas.OrderRead)
def update_order(id: int, item: schemas.OrderUpdate, db: Session = Depends(get_db)):
    order_obj = db.query(models.Order).get(id)
    for key, value in item.dict(exclude={"items"}, exclude_unset=True).items():
        setattr(order_obj, key, value)
    db.commit()
    db.refresh(order_obj)
    return order_obj


@router.delete("/orders/{id}")
@router.delete("/orders/{id}/")
def delete_order(id: int, db: Session = Depends(get_db)):
    order_obj = db.query(models.Order).get(id)
    db.delete(order_obj)
    db.commit()
    return {"ok": True}


@router.get("/inventory/", response_model=List[schemas.InventoryItem])
@router.get("/inventory", response_model=List[schemas.InventoryItem])
def read_inventory(db: Session = Depends(get_db)):
    warehouse_items = db.query(models.Warehouse).options(
        joinedload(models.Warehouse.product).joinedload(models.Product.tire),
        joinedload(models.Warehouse.product).joinedload(models.Product.component)
    ).all()

    storage_items = db.query(models.Storage).options(
        joinedload(models.Storage.product).joinedload(models.Product.tire),
        joinedload(models.Storage.product).joinedload(models.Product.component)
    ).all()

    result = []

    def add_items(items, location_type):
        for item in items:
            product_pyd = to_pydantic(item.product)
            result.append(
                schemas.InventoryItem(
                    id=item.id,
                    location_type=location_type,
                    rack=item.rack,
                    shelf=item.shelf,
                    cell=item.cell,
                    quantity=item.quantity,
                    product=product_pyd,
                    tire=product_pyd.tire,
                    component=product_pyd.component
                )
            )

    add_items(warehouse_items, "warehouse")
    add_items(storage_items, "storage")

    return result


def to_pydantic(product):
    tire_read = None
    component_read = None

    if product.tire is not None:
        tire_read = schemas.TireRead(
            id=product.tire.id,
            product=schemas.ProductBase(
                brand=product.brand,
                model=product.model,
                price=product.price,
                note=product.note
            ),
            width=product.tire.width,
            profile=product.tire.profile,
            diameter=product.tire.diameter,
            index=product.tire.index,
            spikes=product.tire.spikes,
            year=product.tire.year,
            country=product.tire.country,
            season=product.tire.season
        )

    if product.component is not None:
        component_read = schemas.ComponentRead(
            id=product.component.id,
            product=schemas.ProductBase(
                brand=product.brand,
                model=product.model,
                price=product.price,
                note=product.note
            ),
            category=product.component.category,
            parameters=product.component.parameters,
            compatibility=product.component.compatibility,
            weight=product.component.weight,
            color=product.component.color,
            material=product.component.material,
        )

    return schemas.ProductRead(
        id=product.id,
        brand=product.brand,
        model=product.model,
        price=product.price,
        note=product.note,
        tire=tire_read,
        component=component_read
    )
