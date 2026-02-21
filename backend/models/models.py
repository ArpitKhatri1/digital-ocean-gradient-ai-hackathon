from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.db import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True)
    phone = Column(String(20))
    zipCode = Column(Integer)

    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(200))
    state = Column(String(200))
   

    latitude = Column(Float)     # for redistribution optimization
    longitude = Column(Float)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    inventories = relationship(
        "Inventory",
        back_populates="hospital",
        cascade="all, delete-orphan"
    )

    usage_logs = relationship(
        "UsageLog",
        back_populates="hospital",
        cascade="all, delete-orphan"
    )

    purchase_orders = relationship(
        "PurchaseOrder",
        back_populates="hospital"
    )
   
# =========================
# DRUG APPLICATION (NDA / ANDA)
# =========================
class DrugApplication(Base):
    __tablename__ = "drug_applications"

    id = Column(Integer, primary_key=True)

    application_number = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    sponsor_name = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship(
        "DrugProduct",
        back_populates="application",
        cascade="all, delete-orphan"
    )


# =========================
# DRUG PRODUCT (Core Entity)
# =========================
class DrugProduct(Base):
    __tablename__ = "drug_products"

    id = Column(Integer, primary_key=True)

    application_id = Column(
        Integer,
        ForeignKey("drug_applications.id"),
        index=True
    )

    brand_name = Column(String(255), index=True)
    generic_name = Column(String(255), index=True)

    dosage_form = Column(String(200))
    route = Column(String(200))
    marketing_status = Column(String(200))

    product_ndc = Column(
        String(20),
        unique=True,
        index=True
    )

    manufacturer_name = Column(String(255))
    rxcui = Column(String(50), index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    application = relationship("DrugApplication", back_populates="products")

    ingredients = relationship(
        "DrugIngredient",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    inventories = relationship(
        "Inventory",
        back_populates="product"
    )


# =========================
# DRUG INGREDIENT
# =========================
class DrugIngredient(Base):
    __tablename__ = "drug_ingredients"

    id = Column(Integer, primary_key=True)

    product_id = Column(
        Integer,
        ForeignKey("drug_products.id"),
        index=True
    )

    name = Column(String(255))
    strength = Column(String(200))
    unii = Column(String(50))

    product = relationship("DrugProduct", back_populates="ingredients")


# =========================
# INVENTORY (Batch Level)
# =========================
class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True)

    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id"),
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("drug_products.id"),
        index=True
    )

    batch_number = Column(String(200))
    expiry_date = Column(DateTime(timezone=True))

    current_stock = Column(Integer, nullable=False)
    safety_stock_level = Column(Integer, default=0)

    predicted_days_to_zero = Column(Float)
    predicted_risk_score = Column(Float)

    last_restocked_at = Column(DateTime(timezone=True))
    lead_time_days = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "product_id",
            "batch_number",
            name="unique_inventory_batch"
        ),
    )

    hospital = relationship("Hospital", back_populates="inventories")
    product = relationship("DrugProduct", back_populates="inventories")


# =========================
# USAGE LOG (For ML Forecasting)
# =========================
class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)

    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id"),
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("drug_products.id"),
        index=True
    )

    date = Column(DateTime(timezone=True), nullable=False)
    quantity_used = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hospital = relationship("Hospital", back_populates="usage_logs")
    product = relationship("DrugProduct")


# =========================
# SUPPLIER
# =========================
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(250), nullable=False)
    email = Column(String(150))
    phone = Column(String(20))

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    supplier_products = relationship(
        "SupplierProduct",
        back_populates="supplier",
        cascade="all, delete-orphan"
    )


# =========================
# SUPPLIER PRODUCT PRICING
# =========================
class SupplierProduct(Base):
    __tablename__ = "supplier_products"

    id = Column(Integer, primary_key=True, index=True)

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("drug_products.id"),
        index=True
    )

    price_per_unit = Column(Float)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "supplier_id",
            "product_id",
            name="unique_supplier_product"
        ),
    )

    supplier = relationship("Supplier", back_populates="supplier_products")
    product = relationship("DrugProduct")


# =========================
# PURCHASE ORDER
# =========================
class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)

    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id"),
        index=True
    )

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        index=True
    )

    status = Column(String(50))  # Pending, Shipped, Delivered
    expected_delivery_date = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hospital = relationship("Hospital", back_populates="purchase_orders")
    items = relationship(
        "PurchaseOrderItem",
        back_populates="purchase_order",
        cascade="all, delete-orphan"
    )


# =========================
# PURCHASE ORDER ITEMS
# =========================
class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True)

    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id"),
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("drug_products.id"),
        index=True
    )

    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("DrugProduct")