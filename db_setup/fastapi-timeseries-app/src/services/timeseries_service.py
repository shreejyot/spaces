from sqlalchemy.orm import Session
from models.timeseries import TimeSeries
from schemas.timeseries import TimeSeriesCreate, TimeSeriesUpdate

def create_timeseries(db: Session, timeseries: TimeSeriesCreate):
    db_timeseries = TimeSeries(**timeseries.dict())
    db.add(db_timeseries)
    db.commit()
    db.refresh(db_timeseries)
    return db_timeseries

def get_timeseries(db: Session, timeseries_id: int):
    return db.query(TimeSeries).filter(TimeSeries.id == timeseries_id).first()

def get_all_timeseries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(TimeSeries).offset(skip).limit(limit).all()

def update_timeseries(db: Session, timeseries_id: int, timeseries: TimeSeriesUpdate):
    db_timeseries = db.query(TimeSeries).filter(TimeSeries.id == timeseries_id).first()
    if db_timeseries:
        for key, value in timeseries.dict(exclude_unset=True).items():
            setattr(db_timeseries, key, value)
        db.commit()
        db.refresh(db_timeseries)
    return db_timeseries

def delete_timeseries(db: Session, timeseries_id: int):
    db_timeseries = db.query(TimeSeries).filter(TimeSeries.id == timeseries_id).first()
    if db_timeseries:
        db.delete(db_timeseries)
        db.commit()
    return db_timeseries