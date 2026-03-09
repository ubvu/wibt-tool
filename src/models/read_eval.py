from pydantic import BaseModel, Field

class ReadEval(BaseModel):
    syntactic_clarity: int = Field(alias="Syntactic clarity")
    jargon: int = Field(alias="Jargon")
    information_density: int = Field(alias="Information density")
    structural_cohesion: int = Field(alias="Structural cohesion")

    class Config:
        populate_by_name = True
