from fastapi import FastAPI

app= FastAPI()

app.get("/")
def root_reader():
    return {"response": "Healthy"}