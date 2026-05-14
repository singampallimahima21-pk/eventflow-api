from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from app.routes import user_routes
from app.db.database import init_db
from app.models import user_model
from app.services.user_service import save_user_to_db
from app.core.exceptions import http_exception_handler, generic_exception_handler
from app.core.logger import logger

init_db()

app = FastAPI()
app.include_router(user_routes.router, prefix="/api")

# Register exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

@app.get("/")
def health_check():
    logger.info("Health check endpoint called")
    return {"message": "Pipeline is running"}

def process_user_data(data: dict):
    # existing logic...
    if errors:
        return {
            "status": "failed",
            "errors": errors
        }

    #Save to DB
    user_id = save_user_to_db(data)

    return {
        "status": "success",
        "user_id": user_id,
        "data": data
    }
