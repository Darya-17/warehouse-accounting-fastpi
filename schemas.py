from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class SeasonEnum(str, Enum):
    SUMMER = "summer"
    WINTER = "winter"


class ComponentCategoryEnum(str, Enum):
    COVERS = "covers"
    STANDS = "stands"
    ALLOY_WHEEL = "alloy_wheel"
    STEEL_WHEEL = "steel_wheel"
    FORGED_WHEEL = "forged_wheel"
    BOLTS = "bolts"
    CAPS = "caps"
    RINGS = "rings"
    VALVES = "valves"
    VALVE_CAPS = "valve_caps"
    SEAL_TAPE = "seal_tape"
    SEALANT = "sealant"
    WEIGHTS = "weights"
    INNER_TUBES = "inner_tubes"
    PATCHES = "patches"
    CLEANERS = "cleaners"
    PROTECTANTS = "protectants"
    COATINGS = "coatings"
    COMPRESSORS = "compressors"
    GAUGES = "gauges"
    TPMS = "tpms"
    JACKS = "jacks"
    WRENCHES = "wrenches"
    TOOLS = "tools"
    ANTIFLAT = "antiflat"
    WASHER_FLUID = "washer_fluid"
    BRUSHES = "brushes"
    CAR_CARE = "car_care"


class OrderStatusEnum(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PROCESSED = "processed"
    CANCELLED = "cancelled"


class ProductBase(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    price: Optional[float] = None
    note: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int

    class Config:
        orm_mode = True


class TireCreate(BaseModel):
    product_id: int

    width: Optional[str] = None
    profile: Optional[str] = None
    diameter: Optional[str] = None
    index: Optional[str] = None
    spikes: Optional[str] = None
    year: Optional[int] = None
    country: Optional[str] = None
    season: Optional[SeasonEnum] = None


class TireUpdate(BaseModel):
    product_id: Optional[int] = None
    width: Optional[str] = None
    profile: Optional[str] = None
    diameter: Optional[str] = None
    index: Optional[str] = None
    spikes: Optional[str] = None
    year: Optional[int] = None
    country: Optional[str] = None
    season: Optional[SeasonEnum] = None


class TireRead(BaseModel):
    id: int
    product_id: int
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


class ComponentCreate(BaseModel):
    product_id: int

    category: ComponentCategoryEnum
    parameters: Optional[str] = None
    compatibility: Optional[str] = None
    weight: float
    material: str
    color: Optional[str] = None


class ComponentRead(BaseModel):
    id: int
    product_id: int
    category: ComponentCategoryEnum
    parameters: Optional[str]
    compatibility: Optional[str]
    weight: float
    material: str
    color: Optional[str]

    class Config:
        orm_mode = True


class ComponentUpdate(BaseModel):
    id: int
    product_id: Optional[int] = None
    category: Optional[ComponentCategoryEnum] = None
    parameters: Optional[str] = None
    compatibility: Optional[str] = None
    weight: Optional[float] = None
    material: Optional[str] = None
    color: Optional[str] = None

    class Config:
        orm_mode = True


class ProductReadWithDetails(ProductRead):
    tire: Optional[TireRead] = None
    component: Optional[ComponentRead] = None


class WarehouseUpdate(BaseModel):
    product_id: Optional[int] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None
    cell: Optional[str] = None
    quantity: Optional[int] = None


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
    product: ProductReadWithDetails

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


class StorageUpdate(StorageBase):
    product_id: Optional[int] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None
    cell: Optional[str] = None
    quantity: Optional[int] = None


class StorageRead(StorageBase):
    id: int
    product: ProductReadWithDetails

    class Config:
        orm_mode = True


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: Optional[float] = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    id: int
    product: ProductReadWithDetails

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    status: Optional[OrderStatusEnum] = OrderStatusEnum.DRAFT
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    service: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(OrderBase):
    items: Optional[List[OrderItemRead]] = None


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
    product: ProductReadWithDetails
    tire: Optional[TireRead] = None
    component: Optional[ComponentRead] = None


class InventoryCheckItem(BaseModel):
    id: int
    actual_quantity: int
