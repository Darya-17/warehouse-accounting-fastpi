from sqlalchemy import (
    String, Integer, Float, ForeignKey, Enum as SqlEnum, Boolean, text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
import datetime
import sqlalchemy as sa
from enum import Enum



created_at = sa.orm.mapped_column(
    sa.DateTime(timezone=True),
    server_default=sa.text("(utc_time())"),
    nullable=False
)
updated_at = sa.orm.mapped_column(
    sa.DateTime(timezone=True),
    server_default=sa.text("(utc_time())"),
    server_onupdate=sa.text("(utc_time())"),
    onupdate=datetime.datetime.now(datetime.UTC),
    nullable=False
)


class Base(DeclarativeBase):
    active: Mapped[bool] = mapped_column(default=True, server_default=sa.text("true"))
    created_at: Mapped[datetime.datetime] = created_at
    updated_at: Mapped[datetime.datetime] = updated_at



class SeasonEnum(str, Enum):
    SUMMER = "summer"
    WINTER = "winter"


class SectionEnum(str, Enum):
    STORAGE = "storage"
    WAREHOUSE = "warehouse"


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
    PROCESSED = "processed"
    CANCELLED = "cancelled"



class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    model: Mapped[Optional[str]] = mapped_column(String(255))
    price: Mapped[Optional[float]] = mapped_column(Float)
    note: Mapped[Optional[str]] = mapped_column(String(255))
    season: Mapped[Optional[SeasonEnum]] = mapped_column(SqlEnum(SeasonEnum), nullable=True)

    tire: Mapped["Tire"] = relationship(back_populates="product", uselist=False)
    component: Mapped["Component"] = relationship(back_populates="product", uselist=False)


class Tire(Base):
    __tablename__ = "tires"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    width: Mapped[Optional[str]] = mapped_column(String(255))
    profile: Mapped[Optional[str]] = mapped_column(String(255))
    diameter: Mapped[Optional[str]] = mapped_column(String(255))
    index: Mapped[Optional[str]] = mapped_column(String(255))
    spikes: Mapped[Optional[str]] = mapped_column(String(255))
    year: Mapped[Optional[int]] = mapped_column(Integer)
    country: Mapped[Optional[str]] = mapped_column(String(255))

    product: Mapped[Product] = relationship(back_populates="tire")


class Component(Base):
    __tablename__ = "components"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    category: Mapped[ComponentCategoryEnum] = mapped_column(SqlEnum(ComponentCategoryEnum))

    product: Mapped[Product] = relationship(back_populates="component")


class Warehouse(Base):
    __tablename__ = "warehouse"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    shelf: Mapped[str] = mapped_column(String(255))
    cell: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped[Product] = relationship()


class Storage(Base):
    __tablename__ = "storage"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    shelf: Mapped[str] = mapped_column(String(255))
    cell: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped[Product] = relationship()


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    total_price: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[OrderStatusEnum] = mapped_column(SqlEnum(OrderStatusEnum), default=OrderStatusEnum.DRAFT)
    customer_name: Mapped[Optional[str]] = mapped_column(String(255))
    customer_phone: Mapped[Optional[str]] = mapped_column(String(255))
    service: Mapped[Optional[str]] = mapped_column(String(255))

    product: Mapped[Product] = relationship()
