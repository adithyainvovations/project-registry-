import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import pandas as pd
import io

from ..database import get_db
from ..models import ProjectModel, ProjectCreate, ProjectResponse
from ..services.nlp import get_embedding, serialize_embedding
from ..cache import invalidate_cache
from pydantic import BaseModel

load_dotenv()
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_jwt_key_here")
ALGORITHM = "HS256"

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != ADMIN_USER:
            raise HTTPException(status_code=401, detail="Invalid token subject")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload.get("sub")

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(creds: LoginRequest):
    if creds.username != ADMIN_USER or creds.password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    expire = datetime.utcnow() + timedelta(hours=24)
    token = jwt.encode({"sub": ADMIN_USER, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token}


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db.delete(project)
    db.commit()
    invalidate_cache("projects_list")
    return None

@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, updated_project: ProjectCreate, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields
    project.register_no = updated_project.register_no
    project.student_name = updated_project.student_name
    
    # If title/description changed, re-compute embedding
    if project.title != updated_project.title:
        project.title = updated_project.title
        project.title_embedding = serialize_embedding(get_embedding(project.title))
        
    if project.description != updated_project.description:
        project.description = updated_project.description
        project.description_embedding = serialize_embedding(get_embedding(project.description))

    db.commit()
    db.refresh(project)
    invalidate_cache("projects_list")
    return project

@router.get("/export")
def export_projects(db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    """Exports all projects as a CSV file"""
    projects = db.query(ProjectModel).all()
    
    data = []
    for p in projects:
        data.append({
            "ID": p.id,
            "Register No": p.register_no,
            "Student Name": p.student_name,
            "Title": p.title,
            "Description": p.description,
            "Submission Date": p.submission_date,
            "Submission Time": p.submission_time
        })
        
    df = pd.DataFrame(data)
    
    # Write to a string buffer
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    response = Response(content=stream.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=projects_export.csv"
    return response
