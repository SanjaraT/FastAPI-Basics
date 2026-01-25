from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def hello():
    return {'message':'Hello World'}

@app.get("/about")
def hello():
    return {'message':'I am Sanjara and learning FastAPI'}