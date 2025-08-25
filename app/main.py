from fastapi import FastAPI
from app.api import whatsapp

app = FastAPI(title="WhatsApp API")

# Root endpoint for health check
@app.get("/")
async def root():
    return {
        "message": "CCI Colombia MarIA WhatsApp API is running",
        "status": "healthy",
        "available_endpoints": {
            "chat": "/whatsapp/chat (POST)",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CCI Colombia MarIA API"}

# Include routers
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])