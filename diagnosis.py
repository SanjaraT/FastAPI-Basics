from fastapi import FastAPI,Path,HTTPException,Query
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
from fastapi.responses import JSONResponse

app = FastAPI()

#Model for creation
class Patient(BaseModel):
    id : Annotated[str, Field(...,description='Enter the Patient Id please', examples=['P001'])]
    name : Annotated[str, Field(..., description='Enter Patient Name')]
    city : Annotated[str, Field(..., description='Enter Patient City')]
    age : Annotated[int, Field(..., gt=0, lt=120, description='Enter Patient Age')]
    gender : Annotated[Literal['male','female','others'], Field(..., description='Enter Patient Geneder')]
    height : Annotated[float, Field(...,gt=0, description='Enter Patient Height in meters')]
    weight : Annotated[float, Field(...,gt=0, description='Enter Patient Weight in kgs')]


    @computed_field
    @property
    def bmi(self)->float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi<18.5:
            return 'Underweight'
        elif self.bmi<25:
            return 'Normal'
        elif self.bmi<30:
            return 'Normal'
        else:
            return 'Obese'

#Model for update
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender : Annotated[Optional[Literal['male','female','others']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

#Json Data Loading
def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
    return data

#Data Saving
def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)

#View
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

#View Specific Record
@app.get('/patient/{patient_id}')
def view_patient(patient_id : str = Path(...,description='Enter your patient Id',example='P001')):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient Not Found')


#View Sorted Record
@app.get('/sort')
def sort_patient(sort_by : str = Query(..., description='Feature based sorting'),order : 
    str=Query('asc',description='Sort in Ascending or Descending order')):
    valid_fields = ['height', 'weight','bmi'] 

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail='Invalid field. Select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order. Select asc or desc.')
    
    data = load_data()

    sort_order = True if order == 'desc' else False
    sorted_data = sorted(data.values(), key=lambda x:x.get(sort_by,0),reverse=sort_order)
    return sorted_data

#Insert New Record
@app.post('/create')
def create_record(patient:Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient record already exists')
    
    data[patient.id] = patient.model_dump(exclude=['id'])

    save_data(data)

    return JSONResponse(status_code=201, content={'message': 'Record Created Successfully!'})

#Edit/Update Record
@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update : PatientUpdate):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient Not Found!')
    exist_patient_info = data[patient_id]

    #converting the pydantic obj into dict
    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        exist_patient_info[key]=value

    exist_patient_info['id']=patient_id
    patient_py_obj = Patient(**exist_patient_info)
    exist_patient_info =  patient_py_obj.model_dump(exclude={'id'})

    #saving the edited data into the json file
    data[patient_id] = exist_patient_info
    save_data(data)
    return JSONResponse(status_code=200, content={'message':'Record Updated!'})

@app.delete('/delete/{patient_id}')
def delete_patient(pateint_id : str):
    data = load_data()

    if pateint_id not in data: 
        raise HTTPException(status_code=404, detail='Patient Not Found!')
    
    del data[pateint_id]
    save_data(data)
    return JSONResponse(status_code=200, content={'message':'Record Deleted!'})