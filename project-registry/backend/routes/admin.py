from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
import pandas as pd
import io

from ..database import get_db
from ..models import ProjectModel, ProjectCreate, ProjectResponse
from ..services.nlp import get_embedding, serialize_embedding

router = APIRouter(prefix="/admin", tags=["admin"])

@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db.delete(project)
    db.commit()
    return None

@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, updated_project: ProjectCreate, db: Session = Depends(get_db)):
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
    return project

@router.get("/export")
def export_projects(db: Session = Depends(get_db)):
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
