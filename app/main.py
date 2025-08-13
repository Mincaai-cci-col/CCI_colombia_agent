from fastapi import FastAPI
from app.api import whatsapp

app = FastAPI(title="WhatsApp API")

# Include routers
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])