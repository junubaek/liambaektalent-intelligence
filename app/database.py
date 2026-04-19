from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# V8.5 Architecture Default: SQLite locally, easily swappable to Postgres
SQLALCHEMY_DATABASE_URL = "sqlite:///candidates.db"

# To switch to postgres later, simply change the URL:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5432/talent_os"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    # check_same_thread=False is needed only for SQLite
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
