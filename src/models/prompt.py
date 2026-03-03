from pydantic import BaseModel, Field

class Prompt(BaseModel):
    prompt: str = Field(alias="prompt")

    class Config:
        populate_by_name = True
