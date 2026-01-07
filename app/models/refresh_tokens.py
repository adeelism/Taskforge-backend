from app.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from datetime import datetime, timezone


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, autoincrement=True, primary_key=True)  # The primary key column automatically enforces index = True. No need to add index here.
    user_id = Column(Integer, ForeignKey(column="users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, index=True, unique=True)
    issued_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
