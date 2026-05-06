from pydantic import BaseModel
from typing import List

class UserInput(BaseModel):
    name: str
    email: str
    age: int

class UserBatchInput(BaseModel):
    users: List[UserInput]