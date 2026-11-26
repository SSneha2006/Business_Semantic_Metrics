import uuid
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.dataset import Dataset
from backend.models.user import User

router = APIRouter(prefix="/datasets", tags=["Datasets"])

STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage" / "datasets"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    workspace_id: int = 1,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only CSV, XLSX and XLS files are supported."
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="The file is empty.")

    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Maximum file size is 20 MB."
        )

    user = db.query(User).filter(
        User.id == user_id,
        User.workspace_id == workspace_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User or workspace not found.")

    stored_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = STORAGE_DIR / stored_filename

    try:
        file_path.write_bytes(content)

        if extension == ".csv":
            dataframe = pd.read_csv(file_path)
        else:
            dataframe = pd.read_excel(file_path)

        dataset = Dataset(
            filename=file.filename or stored_filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            rows=len(dataframe),
            columns=len(dataframe.columns),
            file_size=len(content),
            workspace_id=workspace_id,
            uploaded_by=user_id
        )

        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        return {
            "message": "Dataset uploaded successfully",
            "dataset": {
                "id": dataset.id,
                "filename": dataset.filename,
                "rows": dataset.rows,
                "columns": dataset.columns,
                "file_size": dataset.file_size
            }
        }

    except Exception as error:
        db.rollback()
        if file_path.exists():
            file_path.unlink()
        if isinstance(error, HTTPException):
            raise error
        raise HTTPException(status_code=400, detail="Unable to process this dataset.")


@router.get("/")
def get_datasets(
    workspace_id: int = 1,
    db: Session = Depends(get_db)
):
    datasets = db.query(Dataset).filter(
        Dataset.workspace_id == workspace_id
    ).order_by(Dataset.created_at.desc()).all()

    return [
        {
            "id": item.id,
            "filename": item.filename,
            "rows": item.rows,
            "columns": item.columns,
            "file_size": item.file_size,
            "created_at": item.created_at
        }
        for item in datasets
    ]


@router.get("/{dataset_id}/preview")
def preview_dataset(
    dataset_id: int,
    workspace_id: int = 1,
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.workspace_id == workspace_id
    ).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    try:
        path = Path(dataset.file_path)

        if path.suffix.lower() == ".csv":
            dataframe = pd.read_csv(path, nrows=6)
        else:
            dataframe = pd.read_excel(path, nrows=6)

        return {
            "filename": dataset.filename,
            "columns": dataframe.columns.tolist(),
            "preview": dataframe.fillna("").astype(str).values.tolist()
        }

    except Exception:
        raise HTTPException(status_code=400, detail="Unable to preview this dataset.")


@router.delete("/{dataset_id}")
def delete_dataset(
    dataset_id: int,
    workspace_id: int = 1,
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.workspace_id == workspace_id
    ).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    path = Path(dataset.file_path)

    if path.exists():
        path.unlink()

    db.delete(dataset)
    db.commit()

    return {"message": "Dataset deleted successfully"}