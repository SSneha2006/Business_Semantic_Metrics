from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User, Workspace
from backend.security import (
    hash_password,
    verify_password,
    create_token,
    decode_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    workspace_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def user_response(user):
    capabilities = [
        "dataset.write", "metric.write", "conflict.view",
        "chat.ask", "conflict.detect", "formula.run",
        "dashboard.write", "admin.users"
    ]

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "capabilities": capabilities,
        "workspace": {
            "id": user.workspace.id,
            "name": user.workspace.name,
            "is_demo": user.workspace.is_demo
        }
    }


def set_auth_cookie(response, user_id):
    token = create_token(user_id)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=28800,
        path="/"
    )


def get_logged_in_user(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(access_token)
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user = db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.post("/register")
def register(data: RegisterRequest, response: Response,
             db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    workspace = Workspace(name=data.workspace_name.strip())
    db.add(workspace)
    db.flush()

    user = User(
        name=data.name.strip(),
        email=data.email,
        password_hash=hash_password(data.password),
        role="workspace_admin",
        workspace_id=workspace.id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    set_auth_cookie(response, user.id)

    return {"user": user_response(user)}


@router.post("/login")
def login(data: LoginRequest, response: Response,
          db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    set_auth_cookie(response, user.id)

    return {"user": user_response(user)}


@router.get("/me")
def me(user: User = Depends(get_logged_in_user)):
    return {"user": user_response(user)}


@router.post("/refresh")
def refresh(response: Response,
            user: User = Depends(get_logged_in_user)):
    set_auth_cookie(response, user.id)
    return {"user": user_response(user)}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"message": "Logged out successfully"}