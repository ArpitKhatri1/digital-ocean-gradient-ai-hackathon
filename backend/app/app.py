from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db.db import Base, engine, get_db
from models.models import Hospital
from schemas.response import HospitalResponse
from typing import List
import random
import uuid

app = FastAPI()

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

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

@app.get("/gethospital",response_model= HospitalResponse)
def get_hospitals(db:Session = Depends(get_db)) -> HospitalResponse:
    hospital =  db.query(Hospital).first()
    if not hospital:
        return {
            "id":1,
            "name":"not found",
            "latitude":2,
            "longitude":3
        }
    return hospital
    