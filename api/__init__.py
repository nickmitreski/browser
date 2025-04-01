from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Browser Use API"}

@app.get("/api/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy"}
    )

# This is needed for Vercel
handler = app 