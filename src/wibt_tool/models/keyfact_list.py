from pydantic import BaseModel, RootModel
from typing import List

class KeyFact(BaseModel):
    fact: str
    reason: str
    category: str

class KeyFactList(RootModel[List[KeyFact]]):
    pass