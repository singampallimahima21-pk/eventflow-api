from fastapi import (
    APIRouter,
    Query,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from sqlalchemy.exc import IntegrityError

from app.schemas.user_schema import (
    UserInput,
    UserBatchInput,
    SignupInput,
    LoginInput
)

from app.services.user_service import (
    process_user_data,
    get_users_paginated
)

from app.core.auth import (
    create_access_token,
    verify_token
)

from app.core.security import (
    hash_password,
    verify_password
)

from app.core.logger import logger

from app.db.database import SessionLocal
from app.models.user_model import User

import pandas as pd
import uuid

router = APIRouter()


# =========================================================
# SIGNUP API
# =========================================================
@router.post("/signup")
def signup(data: SignupInput):
    logger.info(f"Signup request received for email: {data.email}")

    db = SessionLocal()

    try:
        # 🔹 Check if email already exists
        existing_user = db.query(User).filter(
            User.email == data.email
        ).first()

        if existing_user:
            logger.warning(f"Signup failed: Email already registered - {data.email}")
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # 🔹 Hash password
        hashed_pwd = hash_password(data.password)
        logger.info(f"Password hashed for user: {data.email}")

        # 🔹 Create user object
        user = User(
            name=data.name,
            email=data.email,
            age=data.age,
            password=hashed_pwd
        )

        # 🔹 Save to DB
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
            logger.info(f"User saved successfully: {user.id} - {data.email}")
            return {
                "message": "User created successfully",
                "user_id": user.id
            }
        except IntegrityError:
            db.rollback()
            logger.warning(f"Signup failed: Integrity error for email - {data.email}")
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

    except Exception as e:
        db.rollback()
        logger.exception(f"Signup failed for {data.email}: {str(e)}")
        raise
    finally:
        db.close()


# =========================================================
# LOGIN API
# =========================================================
@router.post("/login")
def login(data: LoginInput):
    logger.info(f"Login request received for email: {data.email}")

    db = SessionLocal()

    try:
        # 🔹 Find user
        user = db.query(User).filter(
            User.email == data.email
        ).first()

        if not user:
            logger.warning(f"Login failed: User not found - {data.email}")
            raise HTTPException(
                status_code=400,
                detail="User not found"
            )

        logger.info(f"User found: {data.email}")

        # 🔹 Verify password
        if not verify_password(data.password, user.password):
            logger.warning(f"Login failed: Invalid password for {data.email}")
            raise HTTPException(
                status_code=400,
                detail="Invalid password"
            )

        logger.info(f"Password validation successful for {data.email}")

        # 🔹 Generate JWT token
        token = create_access_token({
            "user_id": user.id,
            "email": user.email
        })

        logger.info(f"JWT generated for user: {user.id}")

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except Exception as e:
        logger.exception(f"Login failed for {data.email}: {str(e)}")
        raise
    finally:
        db.close()

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    logger.info(f"CSV upload request received: {file.filename}")

    try:
        # 🔹 Read CSV
        df = pd.read_csv(file.file)
        total_rows = len(df)
        logger.info(f"CSV file read successfully: {total_rows} rows")

        results = []

        # 🔹 Process row-by-row
        for index, row in df.iterrows():
            logger.info(f"Processing row {index + 1}/{total_rows}")

            user_data = {
                "name": row["name"],
                "email": row["email"],
                "age": int(row["age"])
            }

            result = process_user_data(user_data)

            if result.get("status") == "failed":
                logger.warning(f"Row {index + 1} validation failed: {result.get('errors')}")

            results.append(result)

        logger.info(f"CSV upload completed: {len(results)} records processed")
        return {
            "total_records": len(results),
            "results": results
        }

    except Exception as e:
        logger.exception(f"CSV upload failed: {str(e)}")
        raise

# =========================================================
# SINGLE USER PROCESSING
# =========================================================
@router.post("/process-data")
async def process_user(data: UserInput):
    try:
        # 🔹 Generate request ID
        request_id = str(uuid.uuid4())
        logger.info(f"[{request_id}] Incoming request: {data}")

        # 🔹 Convert schema → dict
        user_dict = data.model_dump()

        # 🔹 Call service layer
        result = process_user_data(user_dict)

        logger.info(f"[{request_id}] Processed result: {result}")

        return {
            "request_id": request_id,
            "result": result
        }

    except Exception as e:
        logger.exception(f"Process user failed: {str(e)}")
        raise


# =========================================================
# BATCH PROCESSING
# =========================================================
@router.post("/process-batch")
async def process_users_batch(data: UserBatchInput):
    logger.info(f"Batch processing request received: {len(data.users)} users")

    results = []

    for user in data.users:
        user_dict = user.model_dump()
        result = process_user_data(user_dict)
        results.append(result)

    logger.info(f"Batch processing completed: {len(results)} users processed")
    return {
        "total_users": len(results),
        "results": results
    }


# =========================================================
# FETCH USERS
# =========================================================
@router.get("/users")
async def fetch_users(
    page: int = Query(1, ge=1),
    size: int = Query(5, ge=1, le=50),
    age: int = Query(None),
    search: str = Query(None),
    sort_by: str = Query(None),
    order: str = Query("asc"),
    user=Depends(verify_token)
):
    logger.info(f"Fetch users request: page={page}, size={size}, age={age}, search={search}, sort_by={sort_by}, order={order}")

    users, total = get_users_paginated(
        page,
        size,
        age,
        search,
        sort_by,
        order
    )

    logger.info(f"Fetch users completed: {len(users)} records returned out of {total}")

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
async def fetch_users(

    page: int = Query(1, ge=1),
    size: int = Query(5, ge=1, le=50),

    age: int = Query(None),
    search: str = Query(None),

    sort_by: str = Query(None),
    order: str = Query("asc"),

    user=Depends(verify_token)

):

    users, total = get_users_paginated(
        page,
        size,
        age,
        search,
        sort_by,
        order
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