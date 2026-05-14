from pydantic import BaseModel
from typing import List, Optional

class SignupInput(BaseModel):
    name: str
    email: str
    password: str
    age: Optional[int] = None

class LoginInput(BaseModel):
    email: str
    password: str

class UserInput(BaseModel):
    name: str
    email: str
    age: int

class UserBatchInput(BaseModel):
    users: List[UserInput]