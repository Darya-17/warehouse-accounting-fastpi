from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from sqlalchemy import or_

import models
import schemas
from db import get_db

router = APIRouter()


def product_to_pydantic(product: models.Product) -> schemas.ProductReadWithDetails:
    tire_read = None
    component_read = None

    if product.tire:
        tire_read = schemas.TireRead(
            id=product.tire.id,
            product_id=product.tire.product_id,
            width=product.tire.width,
            profile=product.tire.profile,
            diameter=product.tire.diameter,
            index=product.tire.index,
            spikes=product.tire.spikes,
            year=product.tire.year,
            country=product.tire.country,
            season=product.tire.season,
        )

    if product.component:
        component_read = schemas.ComponentRead(
            id=product.component.id,
            product_id=product.component.product_id,  
            category=product.component.category,
            parameters=product.component.parameters,
            compatibility=product.component.compatibility,
            weight=product.component.weight,
            material=product.component.material,
            color=product.component.color,
        )

    return schemas.ProductReadWithDetails(
        id=product.id,
        brand=product.brand,
        model=product.model,
        price=product.price,
        note=product.note,
        tire=tire_read,
        component=component_read,
    )


def find_free_warehouse_location(db: Session, prefix: str) -> tuple[str, str, str]:
    """Находит свободную ячейку в стеллажах с префиксом (З, Л, К)"""
    CELLS_PER_SHELF = 50

    occupied = db.query(
        models.Warehouse.rack,
        models.Warehouse.shelf,
        models.Warehouse.cell
    ).filter(
        models.Warehouse.rack.ilike(f"{prefix}%"),
        models.Warehouse.quantity > 0
    ).all()

    max_cell_per_rack = {}
    for rack, shelf, cell in occupied:
        try:
            cell_num = int(cell)
            current = max_cell_per_rack.get(rack, -1)
            max_cell_per_rack[rack] = max(current, cell_num)
        except:
            continue

    for i in range(1, 30):
        rack = f"{prefix}{i}"
        next_cell = max_cell_per_rack.get(rack, -1) + 1
        shelf = next_cell // CELLS_PER_SHELF
        cell_in_shelf = next_cell % CELLS_PER_SHELF
        return rack, str(shelf), str(cell_in_shelf)

    raise HTTPException(status_code=400, detail=f"Нет места в стеллажах {prefix}*")


@router.get("/products/", response_model=List[dict])
@router.get("/products", response_model=List[dict])
def get_products(db: Session = Depends(get_db)):
    # Получаем записи с ID и количеством
    warehouse_items = db.query(models.Warehouse).all()
    storage_items = db.query(models.Storage).all()

    products = db.query(models.Product).options(
        joinedload(models.Product.tire),
        joinedload(models.Product.component)
    ).all()

    # Словарь: product_id → {id: ..., quantity: ...}
    warehouse_map = {w.product_id: {"id": w.id, "quantity": w.quantity} for w in warehouse_items}
    storage_map = {s.product_id: {"id": s.id, "quantity": s.quantity} for s in storage_items}

    result = []
    for p in products:
        tire_data = None
        component_data = None

        if p.tire:
            tire_data = {
                "id": p.tire.id,
                "width": p.tire.width,
                "profile": p.tire.profile,
                "diameter": p.tire.diameter,
                "index": p.tire.index,
                "spikes": p.tire.spikes,
                "year": p.tire.year,
                "country": p.tire.country,
                "season": p.tire.season,
            }

        if p.component:
            component_data = {
                "id": p.component.id,
                "category": p.component.category,
                "parameters": p.component.parameters,
                "compatibility": p.component.compatibility,
                "weight": p.component.weight,
                "material": p.component.material,
                "color": p.component.color,
            }

        w_data = warehouse_map.get(p.id, None)
        s_data = storage_map.get(p.id, None)

        w_qty = w_data["quantity"] if w_data else 0
        s_qty = s_data["quantity"] if s_data else 0

        location = []
        if w_qty > 0: location.append("склад")
        if s_qty > 0: location.append("хранение")
        location_str = ", ".join(location) if location else "нет на складе"

        result.append({
            "id": p.id,
            "brand": p.brand,
            "model": p.model,
            "price": p.price,
            "note": p.note,
            "tire": tire_data,
            "component": component_data,

            # Количество
            "total_qty": w_qty + s_qty,
            "warehouse_qty": w_qty,
            "storage_qty": s_qty,

            # ID записей — если есть
            "warehouse_id": w_data["id"] if w_data else None,
            "storage_id": s_data["id"] if s_data else None,

            # Для удобства
            "in_warehouse": w_qty > 0,
            "in_storage": s_qty > 0,
            "location": location_str,
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


@router.post("/tires", response_model=schemas.TireRead)
@router.post("/tires/", response_model=schemas.TireRead)
def create_tire(item: schemas.TireCreate, db: Session = Depends(get_db)):
    db_tire = models.Tire(**item.dict())
    db.add(db_tire)
    db.commit()
    db.refresh(db_tire)
    return db_tire


@router.post("/components", response_model=schemas.ComponentRead)
@router.post("/components/", response_model=schemas.ComponentRead)
def create_component(item: schemas.ComponentCreate, db: Session = Depends(get_db)):
    db_comp = models.Component(**item.dict())
    db.add(db_comp)
    db.commit()
    db.refresh(db_comp)
    return db_comp


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


@router.patch("/components/{id}", response_model=schemas.ComponentRead)
@router.patch("/components/{id}/", response_model=schemas.ComponentRead)
def update_component(id: int, item: schemas.ComponentUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.Component).get(id)
    for key, value in item.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/tires/{id}", response_model=schemas.TireRead)
@router.patch("/tires/{id}/", response_model=schemas.TireRead)
def update_tire(
        id: int,
        item: schemas.TireUpdate,  
        db: Session = Depends(get_db)
):
    obj = db.query(models.Tire).get(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Шина не найдена")

    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
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


@router.post("/warehouse/", response_model=schemas.WarehouseCreate)
@router.post("/warehouse", response_model=schemas.WarehouseCreate)
def create_warehouse(item: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    
    prefix = None

    if product.tire:
        season = product.tire.season
        if season == "winter":
            prefix = "З"    
        elif season == "summer":
            prefix = "Л"    
        else:
            prefix = "З"    
    elif product.component:
        prefix = "К"        
    else:
        raise HTTPException(status_code=400, detail="Неизвестный тип товара")

    
    rack, shelf, cell = find_free_warehouse_location(db, prefix)

    
    existing = db.query(models.Warehouse).filter_by(
        product_id=item.product_id,
        rack=rack,
        shelf=shelf,
        cell=cell
    ).first()

    if existing:
        existing.quantity += item.quantity
        db.commit()
        db.refresh(existing)
        return existing
    else:
        obj = models.Warehouse(
            product_id=item.product_id,
            rack=rack,
            shelf=shelf,
            cell=cell,
            quantity=item.quantity
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj



@router.patch("/warehouse/{id}", response_model=schemas.WarehouseRead)
@router.patch("/warehouse/{id}/", response_model=schemas.WarehouseRead)
def update_warehouse(
        id: int,
        item: schemas.WarehouseUpdate,  
        db: Session = Depends(get_db)
):
    obj = db.query(models.Warehouse).get(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Запись на складе не найдена")

    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
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


@router.patch("/storage/{id}", response_model=schemas.StorageRead)
@router.patch("/storage/{id}/", response_model=schemas.StorageRead)
def update_storage(id: int, item: schemas.StorageUpdate, db: Session = Depends(get_db)):
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
        status=models.OrderStatusEnum.DRAFT,  
        customer_name=item.customer_name,
        customer_phone=item.customer_phone,
        service=item.service
    )
    db.add(order_obj)
    db.commit()
    db.refresh(order_obj)

    
    for i in item.items:
        db.add(models.OrderItem(
            order_id=order_obj.id,
            product_id=i.product_id,
            quantity=i.quantity,
            price=i.price
        ))

    
    if order_obj.service == "хранение":
        for order_item in item.items:
            product_id = order_item.product_id
            qty = order_item.quantity

            
            
            product = db.query(models.Product).get(product_id)
            is_large = False
            if product.tire and product.tire.diameter:
                try:
                    diameter = int(product.tire.diameter.replace('"', '').strip())
                    is_large = diameter >= 18
                except:
                    is_large = False

            prefix = "Х" if is_large else "З"  

            rack, shelf, cell = find_free_location(db, prefix, is_large=is_large)

            
            existing = db.query(models.Storage).filter_by(
                product_id=product_id,
                rack=rack,
                shelf=shelf,
                cell=cell
            ).first()

            if existing:
                existing.quantity += qty
            else:
                db.add(models.Storage(
                    product_id=product_id,
                    rack=rack,
                    shelf=shelf,
                    cell=cell,
                    quantity=qty
                ))

    db.commit()
    db.refresh(order_obj)
    return order_obj


@router.patch("/orders/{id}", response_model=schemas.OrderRead)
@router.patch("/orders/{id}/", response_model=schemas.OrderRead)
def update_order(id: int, item: schemas.OrderUpdate, db: Session = Depends(get_db)):
    order_obj = db.query(models.Order).get(id)
    if not order_obj:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order_obj.status
    new_status = item.status or old_status
    is_storage_service = order_obj.service == "хранение"

    
    update_data = item.dict(exclude={"items"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(order_obj, key, value)

    
    if new_status != old_status:

        
        
        
        if is_storage_service:

            
            if new_status == models.OrderStatusEnum.DRAFT:
                for order_item in order_obj.items:
                    product_id = order_item.product_id
                    qty = order_item.quantity

                    
                    product = db.query(models.Product).get(product_id)
                    is_large = False
                    if product and product.tire and product.tire.diameter:
                        try:
                            diameter = int(product.tire.diameter.replace('"', '').strip())
                            is_large = diameter >= 18
                        except (ValueError, AttributeError):
                            is_large = False

                    prefix = "Х" if is_large else "З"  

                    
                    rack, shelf, cell = find_free_location(db, prefix)

                    
                    existing = db.query(models.Storage).filter_by(
                        product_id=product_id,
                        rack=rack,
                        shelf=shelf,
                        cell=cell
                    ).first()

                    if existing:
                        existing.quantity += qty
                    else:
                        db.add(models.Storage(
                            product_id=product_id,
                            rack=rack,
                            shelf=shelf,
                            cell=cell,
                            quantity=qty
                        ))

            
            elif new_status == models.OrderStatusEnum.PROCESSED and old_status == models.OrderStatusEnum.DRAFT:
                for order_item in order_obj.items:
                    storage_entry = db.query(models.Storage).filter_by(
                        product_id=order_item.product_id
                    ).first()

                    if not storage_entry or storage_entry.quantity < order_item.quantity:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Недостаточно товара на хранении (ID: {order_item.product_id})"
                        )

                    storage_entry.quantity -= order_item.quantity
                    if storage_entry.quantity <= 0:
                        db.delete(storage_entry)

            
            elif new_status == models.OrderStatusEnum.CANCELLED and old_status == models.OrderStatusEnum.DRAFT:
                for order_item in order_obj.items:
                    storage_entry = db.query(models.Storage).filter_by(
                        product_id=order_item.product_id
                    ).first()

                    if storage_entry:
                        storage_entry.quantity -= order_item.quantity
                        if storage_entry.quantity <= 0:
                            db.delete(storage_entry)

        
        
        
        else:
            
            if new_status == models.OrderStatusEnum.PROCESSED:
                for order_item in order_obj.items:
                    product_id = order_item.product_id
                    qty = order_item.quantity

                    
                    wh = db.query(models.Warehouse).filter_by(product_id=product_id).first()
                    st = db.query(models.Storage).filter_by(product_id=product_id).first()

                    if wh and wh.quantity >= qty:
                        wh.quantity -= qty
                    elif st and st.quantity >= qty:
                        st.quantity -= qty
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Недостаточно товара {product_id} на складе или хранении"
                        )

            
            elif new_status == models.OrderStatusEnum.CANCELLED and old_status == models.OrderStatusEnum.PROCESSED:
                for order_item in order_obj.items:
                    product_id = order_item.product_id
                    qty = order_item.quantity

                    wh = db.query(models.Warehouse).filter_by(product_id=product_id).first()
                    if wh:
                        wh.quantity += qty
                    else:
                        db.add(models.Warehouse(
                            product_id=product_id,
                            rack="Возврат",
                            shelf="Отмена",
                            cell="",
                            quantity=qty
                        )) 
                        
            elif new_status == models.OrderStatusEnum.DRAFT and old_status == models.OrderStatusEnum.PROCESSED:
                for order_item in order_obj.items:
                    product_id = order_item.product_id
                    qty = order_item.quantity

                    wh = db.query(models.Warehouse).filter_by(product_id=product_id).first()
                    if wh:
                        wh.quantity += qty
                    else:
                        db.add(models.Warehouse(
                            product_id=product_id,
                            rack="Возврат",
                            shelf="Отмена",
                            cell="",
                            quantity=qty
                        ))

    db.commit()
    db.refresh(order_obj)
    return order_obj


def delete_order(id: int, db: Session = Depends(get_db)):
    order_obj = db.query(models.Order).get(id)
    db.delete(order_obj)
    db.commit()
    return {"ok": True}


@router.get("/inventory", response_model=List[schemas.InventoryItem])
@router.get("/inventory/", response_model=List[schemas.InventoryItem])
def read_inventory(db: Session = Depends(get_db)):
    warehouse_items = db.query(models.Warehouse).options(
        joinedload(models.Warehouse.product).joinedload(models.Product.tire),
        joinedload(models.Warehouse.product).joinedload(models.Product.component),
    ).all()

    storage_items = db.query(models.Storage).options(
        joinedload(models.Storage.product).joinedload(models.Product.tire),
        joinedload(models.Storage.product).joinedload(models.Product.component),
    ).all()

    result = []

    def add_items(items: list, location_type: str):
        for item in items:
            if not item.product:
                continue

            product_pyd = product_to_pydantic(item.product)

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
                    component=product_pyd.component,
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
                note=product.note,
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
