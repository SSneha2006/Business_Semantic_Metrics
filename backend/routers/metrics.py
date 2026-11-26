
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database import get_db
from backend.models.metric import Metric
from backend.models.user import User

router = APIRouter(prefix="/metrics", tags=["Semantic Metrics"])


# Request model
class MetricCreate(BaseModel):
    name: str
    description: Optional[str] = None
    formula: str
    data_type: str = "NUMBER"
    aggregation: str = "SUM"
    department: str
    workspace_id: int = 1
    created_by: int = 1


class MetricUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    formula: Optional[str] = None
    data_type: Optional[str] = None
    aggregation: Optional[str] = None
    department: Optional[str] = None


# Create metric
@router.post("/")
def create_metric(
    metric_data: MetricCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == metric_data.created_by,
        User.workspace_id == metric_data.workspace_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User or workspace not found.")

    existing = db.query(Metric).filter(
        Metric.name == metric_data.name,
        Metric.workspace_id == metric_data.workspace_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Metric already exists.")

    metric = Metric(**metric_data.model_dump())

    db.add(metric)
    db.commit()
    db.refresh(metric)

    return {
        "message": "Metric created successfully",
        "metric": {
            "id": metric.id,
            "name": metric.name,
            "description": metric.description,
            "formula": metric.formula,
            "data_type": metric.data_type,
            "aggregation": metric.aggregation,
            "department": metric.department,
            "workspace_id": metric.workspace_id
        }
    }


# Get all metrics
@router.get("/")
def get_metrics(
    workspace_id: int = 1,
    db: Session = Depends(get_db)
):
    metrics = db.query(Metric).filter(
        Metric.workspace_id == workspace_id
    ).order_by(Metric.created_at.desc()).all()

    return [
        {
            "id": metric.id,
            "name": metric.name,
            "description": metric.description,
            "formula": metric.formula,
            "data_type": metric.data_type,
            "aggregation": metric.aggregation,
            "department": metric.department,
            "workspace_id": metric.workspace_id
        }
        for metric in metrics
    ]


# Update metric
@router.put("/{metric_id}")
def update_metric(
    metric_id: int,
    metric_data: MetricUpdate,
    workspace_id: int = 1,
    db: Session = Depends(get_db)
):
    metric = db.query(Metric).filter(
        Metric.id == metric_id,
        Metric.workspace_id == workspace_id
    ).first()

    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found.")

    updates = metric_data.model_dump(exclude_unset=True)

    if "name" in updates:
        duplicate = db.query(Metric).filter(
            Metric.name == updates["name"],
            Metric.workspace_id == workspace_id,
            Metric.id != metric_id
        ).first()

        if duplicate:
            raise HTTPException(status_code=400, detail="Metric name already exists.")

    for key, value in updates.items():
        setattr(metric, key, value)

    db.commit()
    db.refresh(metric)

    return {
        "message": "Metric updated successfully",
        "id": metric.id,
        "name": metric.name
    }


# Delete metric
@router.delete("/{metric_id}")
def delete_metric(
    metric_id: int,
    workspace_id: int = 1,
    db: Session = Depends(get_db)
):
    metric = db.query(Metric).filter(
        Metric.id == metric_id,
        Metric.workspace_id == workspace_id
    ).first()

    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found.")

    db.delete(metric)
    db.commit()

    return {"message": "Metric deleted successfully"}
