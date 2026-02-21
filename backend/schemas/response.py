from pydantic import BaseModel, ConfigDict
from datetime import datetime


# ── Hospital ───────────────────────────────────────────────────────────────
class HospitalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    latitude: float | None = None
    longitude: float | None = None


# ── Ingredient ─────────────────────────────────────────────────────────────
class IngredientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str | None = None
    strength: str | None = None
    unii: str | None = None


# ── Medicine / DrugProduct ─────────────────────────────────────────────────
class MedicineListItem(BaseModel):
    """Compact view for listing medicines."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    brand_name: str | None = None
    generic_name: str | None = None
    dosage_form: str | None = None
    route: str | None = None
    marketing_status: str | None = None
    product_ndc: str | None = None
    manufacturer_name: str | None = None


class MedicineDetail(MedicineListItem):
    """Full detail view including ingredients."""
    rxcui: str | None = None
    created_at: datetime | None = None
    ingredients: list[IngredientResponse] = []


# ── Supplier ───────────────────────────────────────────────────────────────
class SupplierListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str | None = None
    phone: str | None = None
    is_active: bool = True


class SupplierWithMedicines(SupplierListItem):
    """Supplier with the list of medicines it provides."""
    medicines: list[MedicineListItem] = []


class MedicineWithSuppliers(MedicineDetail):
    """Medicine with the list of suppliers."""
    suppliers: list[SupplierListItem] = []


# ── Paginated wrapper ─────────────────────────────────────────────────────
class PaginatedMedicines(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[MedicineListItem]


class PaginatedSuppliers(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[SupplierListItem]
