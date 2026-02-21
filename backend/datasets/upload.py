
"""
upload-drugs.py
───────────────
Reads the FDA drugs JSON, takes the first 1000 filtered records (those with
manufacturer_name present), and bulk-inserts:

  • DrugApplication  (one per application_number)
  • DrugProduct      (one per product × NDC combo)
  • DrugIngredient   (active ingredients per product)
  • Supplier         (deduplicated by manufacturer name)
  • SupplierProduct  (links every supplier ↔ product)

All inserts happen in a single transaction.
"""

import json
import sys
from pathlib import Path
from typing import Any

# ── ensure backend root is importable ──────────────────────────────────────
HERE = Path(__file__).resolve()
BACKEND_ROOT = HERE.parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy.orm import Session
from db.db import SessionLocal
from models.models import (
    DrugApplication,
    DrugProduct,
    DrugIngredient,
    Supplier,
    SupplierProduct,
)

DATA_PATH = HERE.parent / "drug-drugsfda-0001-of-0001.json"


# ── helpers ────────────────────────────────────────────────────────────────
def load_filtered(path: Path, limit: int = 1000) -> list[dict[str, Any]]:
    """Return first *limit* records that carry manufacturer_name."""
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    filtered = [
        item
        for item in raw["results"]
        if item.get("openfda", {}).get("manufacturer_name")
    ]
    return filtered[:limit]


def upload_drugs(limit: int = 1000) -> None:
    records = load_filtered(DATA_PATH, limit)
    if not records:
        print("no records found in dataset")
        return

    db: Session = SessionLocal()

    # ── de-duplication caches (keyed on the natural unique value) ──────────
    app_cache: dict[str, DrugApplication] = {}   # application_number -> obj
    supplier_cache: dict[str, Supplier] = {}      # manufacturer name   -> obj
    seen_ndcs: set[str] = set()                   # avoid duplicate product_ndc
    seen_sp: set[tuple[int, int]] = set()         # (supplier_id, product_id)

    try:
        for rec in records:
            ofd: dict = rec.get("openfda") or {}
            app_number: str = rec.get("application_number", "")

            # ── 1. DrugApplication ─────────────────────────────────────────
            if app_number and app_number not in app_cache:
                app_obj = DrugApplication(
                    application_number=app_number,
                    sponsor_name=rec.get("sponsor_name"),
                )
                db.add(app_obj)
                db.flush()                       # get app_obj.id
                app_cache[app_number] = app_obj
            app_obj = app_cache.get(app_number)

            # ── 2. Suppliers (from manufacturer_name list) ─────────────────
            mfr_names: list[str] = ofd.get("manufacturer_name") or []
            for mfr in mfr_names:
                mfr_key = mfr.strip()
                if mfr_key and mfr_key not in supplier_cache:
                    sup = Supplier(name=mfr_key, is_active=True)
                    db.add(sup)
                    db.flush()
                    supplier_cache[mfr_key] = sup

            # ── shared openfda fields ──────────────────────────────────────
            generic_name = (ofd.get("generic_name") or [None])[0]
            ndcs = ofd.get("product_ndc") or []
            rxcuis = ofd.get("rxcui") or []
            uniis = ofd.get("unii") or []

            # ── 3. Products + Ingredients ──────────────────────────────────
            products_raw: list[dict] = rec.get("products") or []
            for idx, prod in enumerate(products_raw):
                # pick an NDC for this product (round-robin from openfda list)
                ndc = ndcs[idx] if idx < len(ndcs) else (ndcs[0] if ndcs else None)

                # skip if we already inserted a product with this NDC
                if ndc and ndc in seen_ndcs:
                    continue
                if ndc:
                    seen_ndcs.add(ndc)

                rxcui = rxcuis[idx] if idx < len(rxcuis) else (rxcuis[0] if rxcuis else None)

                drug_product = DrugProduct(
                    application_id=app_obj.id if app_obj else None,
                    brand_name=prod.get("brand_name"),
                    generic_name=generic_name,
                    dosage_form=prod.get("dosage_form"),
                    route=prod.get("route"),
                    marketing_status=prod.get("marketing_status"),
                    product_ndc=ndc,
                    manufacturer_name=mfr_names[0] if mfr_names else None,
                    rxcui=rxcui,
                )
                db.add(drug_product)
                db.flush()  # get drug_product.id

                # ── 3a. Ingredients ────────────────────────────────────────
                for ai in prod.get("active_ingredients") or []:
                    unii = uniis[0] if uniis else None
                    ingredient = DrugIngredient(
                        product_id=drug_product.id,
                        name=ai.get("name"),
                        strength=ai.get("strength"),
                        unii=unii,
                    )
                    db.add(ingredient)

                # ── 4. SupplierProduct links ───────────────────────────────
                for mfr in mfr_names:
                    mfr_key = mfr.strip()
                    sup = supplier_cache.get(mfr_key)
                    if not sup:
                        continue
                    pair = (sup.id, drug_product.id)
                    if pair not in seen_sp:
                        seen_sp.add(pair)
                        db.add(SupplierProduct(
                            supplier_id=sup.id,
                            product_id=drug_product.id,
                        ))

        # ── commit everything in one shot ──────────────────────────────────
        db.commit()
        print(
            f"Done — inserted {len(app_cache)} applications, "
            f"{len(seen_ndcs)} products, "
            f"{len(supplier_cache)} suppliers, "
            f"{len(seen_sp)} supplier↔product links"
        )

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    upload_drugs(1000)