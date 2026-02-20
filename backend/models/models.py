from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.db import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(20))

    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))

    latitude = Column(Float)     # for redistribution optimization
    longitude = Column(Float)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    inventories = relationship("Inventory", back_populates="hospital")


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), index=True, nullable=False)
    generic_name = Column(String(150))
    brand_name = Column(String(150))

    drug_class = Column(String(100))  # e.g. Antibiotic, Sedative
    dosage_form = Column(String(100))  # Tablet, Injection
    strength = Column(String(50))      # 500mg, 10mg/ml

    is_critical = Column(Boolean, default=False)  # ICU drugs
    is_injectable = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    inventories = relationship("Inventory", back_populates="medicine")
    
    
class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)

    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))

    current_stock = Column(Integer, nullable=False)
    safety_stock_level = Column(Integer, default=0)

    avg_daily_usage_30d = Column(Float)  # precomputed for ML
    avg_daily_usage_7d = Column(Float)

    predicted_days_to_zero = Column(Float)  # ML output
    predicted_risk_score = Column(Float)    # ML probability

    last_restocked_at = Column(DateTime(timezone=True))
    lead_time_days = Column(Integer)  # supplier delivery time

    expiry_date = Column(DateTime(timezone=True))

    hospital = relationship("Hospital", back_populates="inventories")
    medicine = relationship("Medicine", back_populates="inventories")

    __table_args__ = (
        UniqueConstraint('hospital_id', 'medicine_id', name='unique_hospital_medicine'),
    )
    
class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)

    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))

    date = Column(DateTime(timezone=True), nullable=False)
    quantity_used = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    email = Column(String(150))
    phone = Column(String(20))

    address_line1 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))

    reliability_score = Column(Float)  # ML computed
    avg_delivery_days = Column(Integer)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SupplierMedicine(Base):
    __tablename__ = "supplier_medicines"

    id = Column(Integer, primary_key=True, index=True)

    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))

    price_per_unit = Column(Float)

    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)

    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))

    status = Column(String(50))  # Pending, Shipped, Delivered
    expected_delivery_date = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())