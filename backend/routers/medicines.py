"""
/api/medicines — endpoints to browse, search, and inspect drug products.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from db.db import get_db
from models.models import DrugProduct, SupplierProduct, Supplier
from schemas.response import (
    PaginatedMedicines,
    MedicineListItem,
    MedicineDetail,
    MedicineWithSuppliers,
    SupplierListItem,
)

router = APIRouter(prefix="/api/medicines", tags=["medicines"])


# ── List all medicines (paginated) ────────────────────────────────────────
@router.get("", response_model=PaginatedMedicines)
def list_medicines(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(DrugProduct)
    total = q.count()
    items = (
        q.order_by(DrugProduct.brand_name)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return PaginatedMedicines(
        total=total,
        page=page,
        per_page=per_page,
        items=[MedicineListItem.model_validate(i) for i in items],
    )


# ── Search medicines by name (brand or generic) ──────────────────────────
@router.get("/search", response_model=PaginatedMedicines)
def search_medicines(
    q: str = Query("", min_length=1, description="Search term"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    pattern = f"%{q}%"
    query = db.query(DrugProduct).filter(
        or_(
            DrugProduct.brand_name.ilike(pattern),
            DrugProduct.generic_name.ilike(pattern),
            DrugProduct.manufacturer_name.ilike(pattern),
        )
    )
    total = query.count()
    items = (
        query.order_by(DrugProduct.brand_name)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return PaginatedMedicines(
        total=total,
        page=page,
        per_page=per_page,
        items=[MedicineListItem.model_validate(i) for i in items],
    )


# ── Get single medicine detail (with ingredients) ────────────────────────
@router.get("/{medicine_id}", response_model=MedicineDetail)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    med = (
        db.query(DrugProduct)
        .options(joinedload(DrugProduct.ingredients))
        .filter(DrugProduct.id == medicine_id)
        .first()
    )
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return MedicineDetail.model_validate(med)


# ── Get suppliers for a medicine ─────────────────────────────────────────
@router.get("/{medicine_id}/suppliers", response_model=MedicineWithSuppliers)
def get_medicine_suppliers(medicine_id: int, db: Session = Depends(get_db)):
    med = (
        db.query(DrugProduct)
        .options(joinedload(DrugProduct.ingredients))
        .filter(DrugProduct.id == medicine_id)
        .first()
    )
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")

    sp_rows = (
        db.query(SupplierProduct)
        .options(joinedload(SupplierProduct.supplier))
        .filter(SupplierProduct.product_id == medicine_id)
        .all()
    )
    suppliers = [
        SupplierListItem.model_validate(row.supplier)
        for row in sp_rows
        if row.supplier
    ]

    data = MedicineDetail.model_validate(med).model_dump()
    data["suppliers"] = suppliers
    return MedicineWithSuppliers(**data)
