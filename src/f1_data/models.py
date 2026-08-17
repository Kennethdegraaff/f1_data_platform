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


class Driver(BaseModel):
    id: str
    permanent_number: str | None = None
    code: str | None = None
    first_name: str
    last_name: str
    date_of_birth: date | None = None
    nationality: str | None = None


class Constructor(BaseModel):
    id: str
    name: str
    nationality: str


class Result(BaseModel):
    season: int
    round: int
    race_name: str
    circuit_id: str

    driver_id: str
    constructor_id: str

    number: str
    position: int | None = None
    position_text: str | None = None

    points: float
    grid: int
    laps: int
    status: str

    time_millis: int | None = None
    time: str | None = None

    fastest_lap_rank: int | None = None
    fastest_lap: int | None = None
    fastest_lap_time: str | None = None