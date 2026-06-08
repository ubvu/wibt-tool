from pydantic import BaseModel
from typing import Dict

class KeyFactContainment(BaseModel):
    contained: bool
    reason: str
