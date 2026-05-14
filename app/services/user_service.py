from app.db.database import SessionLocal
from app.models.user_model import User
from app.core.logger import logger


def process_user_data(data: dict):
    logger.info("Starting user data processing")

    errors = []

    #Safe extraction
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    age = data.get("age")

    #Name validation
    if not name:
        errors.append("Name is missing")
    else:
        name = name.title()

    # Email cleaning + validation
    email = email.lower().replace(" at ", "@").replace(" dot ", ".")

    if "@" not in email:
        errors.append("Invalid email format")

    # Age validation
    if age is None:
        errors.append("Age is missing")
    elif not isinstance(age, int):
        errors.append("Age must be integer")
    elif age < 0 or age > 120:
        errors.append("Age must be between 0 and 120")

    #If validation fails → return errors
    if errors:
        logger.warning(f"Validation failed: {errors}")
        return {
            "status": "failed",
            "error_count": len(errors),
            "errors": errors,
            "input": data
        }

    #SAVE TO DB
    try:
        user_id = save_user_to_db({
            "name": name,
            "email": email,
            "age": age
        })
    except ValueError as e:
        # Handle duplicate email specifically
        error_msg = str(e)
        logger.warning(f"User creation failed: {error_msg}")
        return {
            "status": "failed",
            "error_count": 1,
            "errors": [error_msg],
            "input": data
        }
    except Exception as e:
        # Handle other database errors
        logger.exception(f"Unexpected DB error: {str(e)}")
        return {
            "status": "failed",
            "error_count": 1,
            "errors": ["Database error occurred"],
            "input": data
        }

    logger.info(f"User saved with ID: {user_id}")

    #Success response
    return {
        "status": "success",
        "user_id": user_id,
        "data": {
            "name": name,
            "email": email,
            "age": age
        }
    }


def save_user_to_db(data: dict):
    db = SessionLocal()

    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == data["email"]).first()
        if existing_user:
            logger.warning(f"Duplicate email detected: {data['email']}")
            raise ValueError(f"Email already exists: {data['email']}")

        user = User(
            name=data["name"],
            email=data["email"],
            age=data["age"]
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user.id

    except Exception as e:
        db.rollback()
        logger.exception(f"DB Error: {str(e)}")
        raise

    finally:
        db.close()


def get_all_users():
    db = SessionLocal()

    try:
        users = db.query(User).all()
        return users

    except Exception as e:
        logger.exception(f"Error fetching all users: {str(e)}")
        raise
    finally:
        db.close()
        
def get_users_paginated(
    page: int,
    size: int,
    age: int = None,
    search: str = None,
    sort_by: str = None,
    order: str = "asc"
):
    db = SessionLocal()

    try:
        query = db.query(User)

        #Filtering
        if age is not None:
            query = query.filter(User.age == age)

        #Search
        if search:
            query = query.filter(User.name.ilike(f"%{search}%"))

        #Sorting
        if sort_by:
            column = getattr(User, sort_by, None)

            if column is not None:
                if order == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())

        total = query.count()

        #Pagination
        offset = (page - 1) * size
        users = query.offset(offset).limit(size).all()

        return users, total

    except Exception as e:
        logger.exception(f"Error fetching paginated users: {str(e)}")
        raise
    finally:
        db.close()