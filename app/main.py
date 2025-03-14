from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from app.core.config import settings
from app.api.routes import bookings_router, nlp_router
app = FastAPI(title=settings.PROJECT_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(
    bookings_router,
    prefix=f"{settings.API_V1_STR}/bookings",
    tags=["bookings"])
app.include_router(nlp_router, prefix=f"{settings.API_V1_STR}/nlp", tags=["nlp"])


@app.get("/")
def read_root():
    return FileResponse("app/static/index.html")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
