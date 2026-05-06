from fastapi import APIRouter
from app.schemas.user_schema import UserInput, UserBatchInput
from app.services.user_service import process_user_data, get_users_paginated
from fastapi import Query
from fastapi import Depends
from app.core.auth import create_access_token, verify_token

import uuid
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)

@router.post("/login")
def login():
    # dummy user (for now)
    user_data = {"username": "mahima"}

    token = create_access_token(user_data)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/process-data")
async def process_user(data: UserInput):
    try:
        #Generate request ID (for tracing)
        request_id = str(uuid.uuid4())

        logging.info(f"[{request_id}] Incoming request: {data}")

        #Convert schema → dict
        user_dict = data.model_dump()

        #Call service layer
        result = process_user_data(user_dict)

        logging.info(f"[{request_id}] Processed result: {result}")

        #Return structured response
        return {
            "request_id": request_id,
            "result": result
        }

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")

        return {
            "status": "failed",
            "error": str(e)
        }


@router.post("/process-batch")
async def process_users_batch(data: UserBatchInput):
    results = []

    for user in data.users:
        user_dict = user.dict()
        result = process_user_data(user_dict)
        results.append(result)

    return {
        "total_users": len(results),
        "results": results
    }

    
@router.get("/users")
async def fetch_users(
    page: int = Query(1, ge=1),
    size: int = Query(5, ge=1, le=50),
    age: int = Query(None),
    search: str = Query(None),
    sort_by: str = Query(None),
    order: str = Query("asc"),
    user=Depends(verify_token)   # 🔥 ADD THIS LINE
):
    users, total = get_users_paginated(
        page, size, age, search, sort_by, order
    )

    return {
        "page": page,
        "size": size,
        "total_records": total,
        "filters": {
            "age": age,
            "search": search
        },
        "sorting": {
            "sort_by": sort_by,
            "order": order
        },
        "data": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "age": user.age
            }
            for user in users
        ]
    }