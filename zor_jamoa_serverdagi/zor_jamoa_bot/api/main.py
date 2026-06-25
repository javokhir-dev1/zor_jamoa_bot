from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import admin, departments, orders, reports

app = FastAPI(
    title="Zoʻr Jamoa API",
    version="1.0.0",
    description="Ovqat buyurtma tizimi — backend API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Produksiyada Mini App URL bilan cheklang
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router,      prefix="/api/orders",      tags=["orders"])
app.include_router(departments.router, prefix="/api/departments",  tags=["departments"])
app.include_router(reports.router,     prefix="/api/reports",      tags=["reports"])
app.include_router(admin.router,       prefix="/api/admin",        tags=["admin"])


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}
