from fastapi import FastAPI,Path,HTTPException
import json

app = FastAPI()

def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
    return data

@app.get("/")
def intro():
    return {'message':'Patient Management System'}

@app.get("/about")
def about():
    return {'message':'API to manage patient records.'}

@app.get('/view')
def view():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id : str = Path(...,description='Enter your patient Id',example='P001')):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient Not Found')

