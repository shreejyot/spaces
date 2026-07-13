from pydantic import BaseModel
from typing import List
from datetime import datetime

class TimeSeriesData(BaseModel):
    timestamp: datetime
    value: float

class TimeSeriesCreate(BaseModel):
    data: List[TimeSeriesData]

class TimeSeriesResponse(BaseModel):
    id: int
    data: List[TimeSeriesData]

    class Config:
        orm_mode = True