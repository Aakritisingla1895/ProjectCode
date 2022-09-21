from sqlalchemy import String, Column, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True, index=True,nullable=False)
    email = Column(String, unique=True, index=True,nullable=False)
    name = Column(String, index=True)
    username = Column(String, unique=True, index=True,nullable=False)
    hashed_password = Column(String,nullable=False)

   # items = relationship("Task", back_populates="user")

