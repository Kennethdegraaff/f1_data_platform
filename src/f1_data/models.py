from datetime import date

from pydantic import BaseModel


class Circuit(BaseModel):
    id: str
    name: str
    city: str
    country: str
    latitude: float
    longitude: float


class Race(BaseModel):
    season: int
    round: int
    name: str
    date: date
    circuit: Circuit