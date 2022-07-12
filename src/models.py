from typing import Optional
from pydantic import BaseModel

class CreateQuiz(BaseModel):
    title: str
    id: Optional[int] = 1