from sqlalchemy import Column, Integer, String, Enum as SqlEnum

from app.core.database import Base
from app.users.roles import UserRole

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)