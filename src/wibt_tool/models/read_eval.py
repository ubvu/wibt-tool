from pydantic import BaseModel, Field

class ReadEval(BaseModel):
    syntactic_clarity: int
    jargon: int
    information_density: int 
    structural_cohesion: int 

    class Config:
        populate_by_name = True
