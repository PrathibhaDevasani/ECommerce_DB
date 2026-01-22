from sqlalchemy import Column, Integer, String, Float
from database import Base
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_purchase: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")
