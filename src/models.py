from typing import Optional
from pydantic import BaseModel

class CreateQuiz(BaseModel):
    name: str
    id: Optional[int] = 1