from pydantic import BaseModel


class Judgement(BaseModel):
    faithful : bool
    error_type : str
    reason : str
