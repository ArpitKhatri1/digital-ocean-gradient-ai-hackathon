"""
/api/suppliers — endpoints to browse suppliers and see their medicines.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload

from db.db import get_db
from models.models import Supplier, SupplierProduct
from schemas.response import (
    PaginatedSuppliers,
    SupplierListItem,
    SupplierWithMedicines,
    MedicineListItem,
)

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


# ── List all suppliers (paginated) ────────────────────────────────────────
@router.get("", response_model=PaginatedSuppliers)
def list_suppliers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Supplier)
    total = q.count()
    items = (
        q.order_by(Supplier.name)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return PaginatedSuppliers(
        total=total,
        page=page,
        per_page=per_page,
        items=[SupplierListItem.model_validate(i) for i in items],
    )


# ── Get supplier detail with all its medicines ───────────────────────────
@router.get("/{supplier_id}", response_model=SupplierWithMedicines)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    sup = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")

    sp_rows = (
        db.query(SupplierProduct)
        .options(joinedload(SupplierProduct.product))
        .filter(SupplierProduct.supplier_id == supplier_id)
        .all()
    )
    medicines = [
        MedicineListItem.model_validate(row.product)
        for row in sp_rows
        if row.product
    ]

    data = SupplierListItem.model_validate(sup).model_dump()
    data["medicines"] = medicines
    return SupplierWithMedicines(**data)
