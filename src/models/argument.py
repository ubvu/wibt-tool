from pydantic import BaseModel


class Argument(BaseModel):
    faithful : bool
    error_type : str
    reference_sentences : str
    reason : str
