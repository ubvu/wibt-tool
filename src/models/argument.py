from pydantic import BaseModel
from typing import List

class Argument(BaseModel):
    faithful : bool
    error_type : str
    reference_sentences : List[int]
    reason : str
