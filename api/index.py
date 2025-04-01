from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Browser Use API"}

@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 