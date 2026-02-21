from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db.db import Base, engine, get_db
from models.models import Hospital, DrugApplication
from typing import List
import random
import uuid

from routers.medicines import router as medicines_router
from routers.suppliers import router as suppliers_router

app = FastAPI()

# ── CORS (allow frontend dev server) ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────
app.include_router(medicines_router)
app.include_router(suppliers_router)

@app.post("/test/add-random-hospital")
def add_random_hospital(db: Session = Depends(get_db)):
	name = f"Hospital {uuid.uuid4().hex[:6]}"
	email = f"{name.replace(' ', '').lower()}@example.com"
	phone = f"+1{random.randint(1000000000,9999999999)}"
	address_line1 = f"{random.randint(1,9999)} Main St"
	address_line2 = ""
	city = "Testville"
	state = "TS"
	country = "Testland"
	postal_code = f"{random.randint(10000,99999)}"
	latitude = random.uniform(-90.0, 90.0)
	longitude = random.uniform(-180.0, 180.0)

	hospital = Hospital(
		name=name,
		email=email,
		phone=phone,
		address_line1=address_line1,
		address_line2=address_line2,
		city=city,
		state=state,
		country=country,
		postal_code=postal_code,
		latitude=latitude,
		longitude=longitude,
		is_active=True,
	)

	db.add(hospital)
	db.commit()
	db.refresh(hospital)

	# serialize only column values (avoid SQLAlchemy internals)
	data = {c.name: getattr(hospital, c.name) for c in hospital.__table__.columns}
	return data

@app.get("/gethospital")
def get_hospitals(db:Session = Depends(get_db)):
    hospital =  db.query(DrugApplication).count()
    return hospital
    