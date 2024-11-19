from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class Version(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    idUsuario: PydanticObjectId
    idEntrada: PydanticObjectId
    contenido: str
    fechaEdicion: datetime = Field(default_factory=datetime.now)
