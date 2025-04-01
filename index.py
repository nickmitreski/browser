from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Browser Use API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
            </style>
        </head>
        <body>
            <h1>🌐 Browser Use API</h1>
            <p>The API is running! Visit <a href="/docs">API documentation</a> to get started.</p>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "ok"} 