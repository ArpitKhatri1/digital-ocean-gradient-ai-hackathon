import json
import random
from pathlib import Path
from typing import Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import String

from db.db import SessionLocal
from models.models import Hospital


DATA_PATH = Path(__file__).parent / "us-hospitals.json"


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def safe_float(value: Any) -> Optional[float]:
    try:
        if value in (None, "", "null"):
            return None
        return float(value)
    except (ValueError, TypeError):
        return None


def is_valid_lat_lon(lat: Optional[float], lon: Optional[float]) -> bool:
    if lat is None or lon is None:
        return False
    return -90 <= lat <= 90 and -180 <= lon <= 180


def get_column_string_limits(model) -> dict[str, int]:
    """
    Dynamically extract VARCHAR limits from SQLAlchemy model.
    """
    limits = {}
    for column in model.__table__.columns:
        if isinstance(column.type, String) and column.type.length:
            limits[column.name] = column.type.length
    return limits


COLUMN_LIMITS = get_column_string_limits(Hospital)


def enforce_string_limits(data: dict[str, Any]) -> bool:
    """
    Return False if any string field exceeds DB limit.
    """
    for field, max_len in COLUMN_LIMITS.items():
        value = data.get(field)
        if value and isinstance(value, str):
            if len(value) > max_len:
                return False
    return True


# --------------------------------------------------
# Load JSON Safely
# --------------------------------------------------

def load_hospitals() -> list[dict[str, Any]]:
    if not DATA_PATH.exists():
        print(f"Dataset not found at {DATA_PATH}")
        return []

    try:
        with DATA_PATH.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as e:
        print(f"Corrupted JSON file: {e}")
        return []
    except Exception as e:
        print(f"Unexpected file read error: {e}")
        return []

    if not isinstance(data, list):
        print("Invalid dataset format. Expected list at root.")
        return []

    return data


# --------------------------------------------------
# Record Mapping with Full Validation
# --------------------------------------------------

def map_record_to_hospital(rec: dict[str, Any]) -> Optional[dict[str, Any]]:
    if not isinstance(rec, dict):
        return None

    name = rec.get("name") or rec.get("alt_name")
    if not name or not isinstance(name, str) or not name.strip():
        return None

    # Extract coordinates safely
    gp = rec.get("geo_point") or {}
    geo_shape = rec.get("geo_shape") or {}
    geometry = geo_shape.get("geometry") or {}
    coords = geometry.get("coordinates") or [None, None]

    lon = gp.get("lon") if isinstance(gp, dict) else None
    lat = gp.get("lat") if isinstance(gp, dict) else None

    if lon is None and isinstance(coords, (list, tuple)) and len(coords) >= 2:
        lon = coords[0]
    if lat is None and isinstance(coords, (list, tuple)) and len(coords) >= 2:
        lat = coords[1]

    lat = safe_float(lat)
    lon = safe_float(lon)

    if not is_valid_lat_lon(lat, lon):
        return None

    mapped = {
        "name": name.strip(),
        "email": None,
        "phone": rec.get("telephone"),
        "address_line1": rec.get("address"),
        "address_line2": rec.get("address2"),
        "city": rec.get("city"),
        "state": rec.get("state"),
        "country": rec.get("country"),
        "postal_code": rec.get("zip"),
        "latitude": lat,
        "longitude": lon,
        "is_active": True,
    }

    if not enforce_string_limits(mapped):
        return None

    return mapped


# --------------------------------------------------
# Insert Clean Records
# --------------------------------------------------

def insert_random_hospitals(n: int = 3000):
    records = load_hospitals()

    if not records:
        print("No valid dataset loaded.")
        return

    n = min(n, len(records))
    sampled = random.sample(records, n)

    valid_records = []
    skipped = 0

    for rec in sampled:
        try:
            mapped = map_record_to_hospital(rec)
            if mapped:
                valid_records.append(mapped)
            else:
                skipped += 1
        except Exception:
            skipped += 1

    if not valid_records:
        print("No valid records to insert.")
        return

    db: Session = SessionLocal()

    try:
        db.bulk_insert_mappings(Hospital, valid_records)
        db.commit()
        print(f"Inserted {len(valid_records)} hospital records")
        print(f"Skipped {skipped} corrupted/invalid records")
    except Exception as e:
        db.rollback()
        print(f"Database error occurred: {e}")
    finally:
        db.close()


# --------------------------------------------------
# Run
# --------------------------------------------------

if __name__ == "__main__":
    insert_random_hospitals(3000)