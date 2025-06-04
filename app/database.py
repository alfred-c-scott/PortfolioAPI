# installed
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# local
from .config import settings

SQLALCHEMY_DATABASE_URL = "postgresql://{u}:{pw}@{h}:{p}/{db}".format(
    u=settings.db_username,
    pw=settings.db_password,
    h=settings.db_hostname,
    p=settings.db_port,
    db=settings.db_name
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
