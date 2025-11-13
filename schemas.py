from pydantic import BaseModel
from typing import Optional
from enum import Enum


class SeasonEnum(str, Enum):
    SUMMER = "summer"
    WINTER = "winter"


class ComponentCategoryEnum(str, Enum):
    
    COVERS = "covers"
    STANDS = "stands"
    ALLOY_WHEEL = "alloy_wheel"
    CLEANERS = "cleaners"
    TOOLS = "tools"


class OrderStatusEnum(str, Enum):
    DRAFT = "draft"
    PROCESSED = "processed"
    CANCELLED = "cancelled"


class ProductBase(BaseModel):
    brand: Optional[str]
    model: Optional[str]
    price: Optional[float]
    note: Optional[str]
    season: Optional[SeasonEnum]


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int

    class Config:
        orm_mode = True


class TireBase(BaseModel):
    product_id: int
    width: Optional[str]
    profile: Optional[str]
    diameter: Optional[str]
    index: Optional[str]
    spikes: Optional[str]
    year: Optional[int]
    country: Optional[str]


class TireCreate(TireBase):
    pass


class TireRead(TireBase):
    id: int

    class Config:
        orm_mode = True


class ComponentBase(BaseModel):
    product_id: int
    category: ComponentCategoryEnum


class ComponentCreate(ComponentBase):
    pass


class ComponentRead(ComponentBase):
    id: int

    class Config:
        orm_mode = True


class WarehouseBase(BaseModel):
    product_id: int
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
    shelf: str
    cell: str
    quantity: int


class StorageCreate(StorageBase):
    pass


class StorageRead(StorageBase):
    id: int

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    product_id: int
    quantity: int
    total_price: Optional[float]
    status: Optional[OrderStatusEnum]
    customer_name: Optional[str]
    customer_phone: Optional[str]
    service: Optional[str]


class OrderCreate(OrderBase):
    pass


class OrderRead(OrderBase):
    id: int

    class Config:
        orm_mode = True
