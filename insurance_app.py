from fastapi import FastAPI,Path,HTTPException,Query
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
import joblib
import pandas as pd
from fastapi.responses import JSONResponse
import numpy as np

#Import ML model
model = joblib.load("insurance_model.pkl")

app = FastAPI()
@app.get("/")
def home():
    return {"message": "Insurance Prediction API is running"}

tier_1_cities = {
    "Mumbai", "Delhi", "Bangalore", "Chennai",
    "Kolkata", "Hyderabad", "Pune"
}

tier_2_cities = {
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi",
    "Visakhapatnam", "Coimbatore", "Bhopal", "Nagpur", "Vadodara",
    "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati",
    "Thiruvananthapuram", "Ludhiana", "Nashik", "Allahabad",
    "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem",
    "Vijayawada", "Tiruchirappalli", "Bhavnagar", "Gwalior",
    "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode",
    "Warangal", "Kolhapur", "Bilaspur", "Jalandhar", "Noida",
    "Guntur", "Asansol", "Siliguri"
}

#pydantic model to validate user data
class UserInput(BaseModel):
    age : Annotated[int, Field(..., gt=0, lt=120, description='Enter Age')]
    weight : Annotated[float, Field(...,gt=0, description='Enter Weight in kgs')]
    height : Annotated[float, Field(...,gt=0, description='Enter Height in meters')]
    income_lpa : Annotated[int, Field(...,gt=0, description='Enter your annual salary in lpa')]
    smoker : Annotated[bool, Field(...,description='Are you a smoker?')]
    city : Annotated[str, Field(..., description='Enter your City')]
    occupation : Annotated[Literal['retired', 'freelancer', 'student', 'government_job', 'business_owner',
 'unemployed', 'private_job'], Field(..., description='Enter Patient Geneder')]

    @computed_field
    @property
    def bmi(self)->float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def lifestyle_risk(self)->str:
        if self.smoker and self.bmi >= 30:
            return "high"
        elif self.smoker or self.bmi >= 27:
            return "medium"
        else:
            return "low"
        
    @computed_field
    @property
    def age_group(self)->str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "adult"
        elif self.age < 60:
            return "middle_aged"
        else:
            return "senior"

    @computed_field
    @property
    def city_tier(self)->int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3
        
RISK_MAP = {
    0: "low",
    1: "medium",
    2: "high"
}

@app.post("/predict")
def predict_premium(data: UserInput):
    
    input_df = pd.DataFrame([{
        'bmi': data.bmi,
        'age_group': data.age_group,
        'lifestyle_risk': data.lifestyle_risk,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation
    }])

    #Prediction
    pred = model.predict(input_df)[0]
    if hasattr(pred, "item"):
        pred = pred.item()

    return JSONResponse(status_code=200, content={"predicted_category": RISK_MAP[pred]})

