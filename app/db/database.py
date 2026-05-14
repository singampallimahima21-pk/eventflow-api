from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def init_db():
    # Check if table exists and has correct schema
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
        table_exists = result.fetchone() is not None

        recreate_table = False
        if table_exists:
            # Check if password column is nullable
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = {row[1]: row for row in result}
            if "password" in columns and columns["password"][3] == 1:  # notnull = 1 means NOT nullable
                # Password column exists but is not nullable, need to recreate table
                recreate_table = True

    if recreate_table:
        # Drop table
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE users"))
        # Recreate table
        Base.metadata.create_all(bind=engine)

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Clean up duplicates (only if table exists)
    with engine.begin() as conn:
        try:
            duplicates = conn.execute(text(
                "SELECT email FROM users GROUP BY email HAVING COUNT(*) > 1"
            )).fetchall()

            for email_row in duplicates:
                email = email_row[0]
                conn.execute(text(
                    "DELETE FROM users WHERE email = :email AND id NOT IN (SELECT MIN(id) FROM users WHERE email = :email)",
                ), {"email": email})

            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email ON users(email)"))
        except Exception:
            # Table might not exist yet, skip cleanup
            pass

init_db()