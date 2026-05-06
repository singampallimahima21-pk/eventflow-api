from email import errors

from fastapi import FastAPI
from app.routes import user_routes

from app.db.database import engine, Base
from app.models import user_model
from app.services.user_service import save_user_to_db

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user_routes.router, prefix="/api")

@app.get("/")
def health_check():
    print("THIS FILE IS RUNNING")
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
