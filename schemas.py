from pydantic import BaseModel
from typing import List, Optional
from fastapi import Form, File, UploadFile


class UserBase(BaseModel):
    username: str
    email: str
    name: str
    hashed_password: str

class User(UserBase):
    id: str
    

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    pass


class UploadImageForm(BaseModel):

    file: UploadFile

    @classmethod
    def as_form(
        cls,
        
        file: UploadFile = File(...)
    ):
        return cls(
           
            file=file
        )