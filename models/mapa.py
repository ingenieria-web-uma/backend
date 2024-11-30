from pydantic import BaseModel, field_validator, model_validator
from typing import List


class MapInfo(BaseModel):
    lat: float
    lon: float
    zoom: int

    @field_validator("zoom", mode="before")
    def validate_zoom(cls, value):
        if not isinstance(value, int):
            raise TypeError("El nivel de zoom debe ser un número entero.")
        return value

    @model_validator(mode="before")
    def validate_lat_lon(cls, values):
        lat = values.get("lat")
        lon = values.get("lon")
        if lat is None or lon is None:
            raise ValueError("Ambos campos 'lat' y 'lon' son obligatorios.")
        return values


class MapListResponse(BaseModel):
    mapas: List[MapInfo]

    @field_validator("mapas", mode="before")
    def validate_map_list(cls, value):
        if not isinstance(value, list):
            raise TypeError("El campo 'mapas' debe ser una lista.")
        for item in value:
            if not isinstance(item, MapInfo):
                raise TypeError(
                    "Cada elemento en 'mapas' debe ser una instancia válida de MapInfo."
                )
        return value
