from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_world():
    return {"message": "Check the docs on: localhost/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
