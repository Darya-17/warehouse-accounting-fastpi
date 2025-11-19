from pydantic import BaseModel
from typing import Optional, Union, List
from enum import Enum

from models import OrderStatusEnum


class SeasonEnum(str, Enum):
    SUMMER = "summer"
    WINTER = "winter"


class ComponentCategoryEnum(str, Enum):
    
    COVERS = "covers"
    STANDS = "stands"
    ALLOY_WHEEL = "alloy_wheel"
    CLEANERS = "cleaners"
    TOOLS = "tools"



class ProductBase(BaseModel):
    brand: Optional[str]
    model: Optional[str]
    price: Optional[float]
    note: Optional[str]


class ProductCreate(ProductBase):
    pass




class TireBase(BaseModel):
    product: ProductBase
    width: Optional[str]
    profile: Optional[str]
    diameter: Optional[str]
    index: Optional[str]
    spikes: Optional[str]
    year: Optional[int]
    country: Optional[str]
    season: Optional[SeasonEnum]


class TireCreate(TireBase):
    pass


class TireRead(BaseModel):
    id: int
    width: Optional[str]
    profile: Optional[str]
    diameter: Optional[str]
    index: Optional[str]
    spikes: Optional[str]
    year: Optional[int]
    country: Optional[str]
    season: Optional[SeasonEnum]

    class Config:
        orm_mode = True


class ComponentBase(BaseModel):
    product: ProductBase
    category: ComponentCategoryEnum
    parameters: Optional[str]
    compatibility: Optional[str]
    weight: float
    material: str
    color: Optional[str]
    

class ComponentCreate(ComponentBase):
    pass


class ComponentRead(BaseModel):
    id: int
    category: ComponentCategoryEnum
    parameters: Optional[str]
    compatibility: Optional[str]
    weight: float
    color: Optional[str]
    material: str
    class Config:
        orm_mode = True

class ProductRead(BaseModel):
    id: int
    brand: Optional[str]
    model: Optional[str]
    price: Optional[float]
    note: Optional[str]
    tire: Optional[TireRead] = None
    component: Optional[ComponentRead] = None

    class Config:
        orm_mode = True



class WarehouseBase(BaseModel):
    product_id: int
    rack: str
    shelf: str
    cell: str
    quantity: int


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseRead(WarehouseBase):
    id: int

    class Config:
        orm_mode = True


class StorageBase(BaseModel):
    product_id: int
    rack: str
    shelf: str
    cell: str
    quantity: int


class StorageCreate(StorageBase):
    pass


class StorageRead(StorageBase):
    id: int

    class Config:
        orm_mode = True


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: Optional[float]  


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    id: int
    product: ProductRead

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    status: Optional[OrderStatusEnum] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    service: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(OrderBase):
    items: Optional[List[OrderItemRead]] = []

    class Config:
        orm_mode = True


class OrderRead(OrderBase):
    id: int
    items: List[OrderItemRead] = []

    class Config:
        orm_mode = True




class InventoryItem(BaseModel):
    id: int
    location_type: str
    rack: str
    shelf: str
    cell: str
    quantity: int

    product: ProductRead
    tire: Optional[TireRead] = None
    component: Optional[ComponentRead] = None

class InventoryCheckItem(BaseModel):
    id: int
    actual_quantity: int
