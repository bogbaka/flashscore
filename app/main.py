from fastapi import FastAPI

app = FastAPI(title="Football LiveScore API")


@app.get("/")
def root():
    return {"message": "Football LiveScore API is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}