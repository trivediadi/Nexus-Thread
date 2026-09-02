from pydantic import BaseModel
from typing import Literal

class VoteCreateSchema(BaseModel):
    dir:Literal[1,-1,0]

