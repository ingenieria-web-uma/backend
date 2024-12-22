from pydantic import BaseModel
from typing import Dict


class TraduccionRequest(BaseModel):
    textos: Dict[str, str]
    target_lang: str
