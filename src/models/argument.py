from pydantic import BaseModel
from typing import List

class Argument(BaseModel):
    faithful : bool
    error_type : str
    reference_sentence_numbers : List[int]
    reason : str
