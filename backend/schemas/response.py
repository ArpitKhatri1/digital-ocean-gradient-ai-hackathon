from pydantic import BaseModel

class HospitalResponse(BaseModel):
    id:int
    name:str
    latitude:float
    longitude:float
    
    class Config:
        from_attributes= True