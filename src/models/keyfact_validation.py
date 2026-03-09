from pydantic import BaseModel
from typing import Dict

class KeyFactValidation(BaseModel):
    response: bool
    reason: str
