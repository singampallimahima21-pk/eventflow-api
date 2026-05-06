import logging
from app.db.database import SessionLocal
from app.models.user_model import User

logging.basicConfig(level=logging.INFO)


def process_user_data(data: dict):
    logging.info("Starting user data processing")

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
        logging.warning(f"Validation failed: {errors}")
        return {
            "status": "failed",
            "error_count": len(errors),
            "errors": errors,
            "input": data
        }

    #SAVE TO DB
    user_id = save_user_to_db({
        "name": name,
        "email": email,
        "age": age
    })

    logging.info(f"User saved with ID: {user_id}")

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
        logging.error(f"DB Error: {str(e)}")
        raise

    finally:
        db.close()


def get_all_users():
    db = SessionLocal()

    try:
        users = db.query(User).all()
        return users

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

    finally:
        db.close()