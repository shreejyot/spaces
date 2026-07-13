from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimeSeries(Base):
    __tablename__ = 'time_series'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    value = Column(Float)
    label = Column(String, index=True)

    def __repr__(self):
        return f"<TimeSeries(id={self.id}, timestamp={self.timestamp}, value={self.value}, label={self.label})>"