from fastapi import APIRouter, HTTPException
from src.schemas.timeseries import TimeSeriesCreate, TimeSeriesRead
from src.services.timeseries_service import TimeSeriesService

router = APIRouter()
service = TimeSeriesService()

@router.post("/timeseries/", response_model=TimeSeriesRead)
async def create_timeseries(timeseries: TimeSeriesCreate):
    return await service.create_timeseries(timeseries)

@router.get("/timeseries/{timeseries_id}", response_model=TimeSeriesRead)
async def read_timeseries(timeseries_id: int):
    timeseries = await service.get_timeseries(timeseries_id)
    if not timeseries:
        raise HTTPException(status_code=404, detail="Time series not found")
    return timeseries

@router.put("/timeseries/{timeseries_id}", response_model=TimeSeriesRead)
async def update_timeseries(timeseries_id: int, timeseries: TimeSeriesCreate):
    updated_timeseries = await service.update_timeseries(timeseries_id, timeseries)
    if not updated_timeseries:
        raise HTTPException(status_code=404, detail="Time series not found")
    return updated_timeseries

@router.delete("/timeseries/{timeseries_id}")
async def delete_timeseries(timeseries_id: int):
    success = await service.delete_timeseries(timeseries_id)
    if not success:
        raise HTTPException(status_code=404, detail="Time series not found")
    return {"detail": "Time series deleted successfully"}