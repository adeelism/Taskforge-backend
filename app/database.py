from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings

url = settings.database_url
if url.startswith("sqlite"):
    # in-memory ("sqlite://") needs a single shared connection across threads
    connect_args = {"check_same_thread": False}
    engine = (
        create_engine(url, connect_args=connect_args, poolclass=StaticPool)
        if url in ("sqlite://", "sqlite:///:memory:")
        else create_engine(url, connect_args=connect_args)
    )
else:
    engine = create_engine(url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
