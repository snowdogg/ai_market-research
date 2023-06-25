from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Data(BaseModel):
    dick: str

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/process-data")
def process_data(data: Data):
    # You can add logic here to process the data, such as interacting with AI services
    # For this example, it just echoes back the received data
    return {"received_data": data.dick}
