from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import (
    ProjectModel, ProjectCreate, ProjectResponse, 
    DuplicateCheckRequest, DuplicateCheckResponse
)
from ..services.nlp import get_embedding, serialize_embedding, deserialize_embedding, compute_similarity

router = APIRouter(prefix="/projects", tags=["projects"])

# Threshold for duplicates
SIMILARITY_THRESHOLD = 0.85

@router.get("/", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    """Fetch all projects"""
    return db.query(ProjectModel).all()

@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
def check_duplicate(request: DuplicateCheckRequest, db: Session = Depends(get_db)):
    """
    Checks if a given project title or description is a duplicate independently.
    Returns the maximum similarity score and any matching projects above the threshold.
    """
    new_title_embedding = get_embedding(request.title)
    new_desc_embedding = get_embedding(request.description)

    all_projects = db.query(ProjectModel).all()
    
    from typing import Tuple
    matches: List[Tuple[float, ProjectResponse]] = []
    max_score = 0.0

    for p in all_projects:
        t_score = 0.0
        d_score = 0.0
        
        if p.title_embedding:
            p_title_emb = deserialize_embedding(p.title_embedding)
            t_score = compute_similarity(new_title_embedding, p_title_emb)
            
        if p.description_embedding:
            p_desc_emb = deserialize_embedding(p.description_embedding)
            d_score = compute_similarity(new_desc_embedding, p_desc_emb)
        
        # Take the maximum similarity of either title OR description
        score = max(t_score, d_score)
        
        if score > max_score:
            max_score = score
            
        if score > SIMILARITY_THRESHOLD:
            # Reconstruct response model for the match
            match_response = ProjectResponse.model_validate(p)
            matches.append((score, match_response))
            
    # Sort matches by score descending
    matches.sort(key=lambda x: x[0], reverse=True)
    # Return top 3
    top_matches = [m[1] for m in matches[:3]]
    
    return DuplicateCheckResponse(
        similarity_score=max_score,
        matching_projects=top_matches,
        exact_match_found=(max_score > SIMILARITY_THRESHOLD)
    )

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Registers a new project"""
    if len(project.register_no) < 7:
        raise HTTPException(status_code=400, detail="Register Number must contain more than 6 characters.")

    # Check if register_no already exists
    existing = db.query(ProjectModel).filter(ProjectModel.register_no == project.register_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this Register No already submitted a project.")

    title_emb = get_embedding(project.title)
    desc_emb = get_embedding(project.description)

    db_project = ProjectModel(
        register_no=project.register_no,
        student_name=project.student_name,
        title=project.title,
        description=project.description,
        submission_date=project.submission_date,
        submission_time=project.submission_time,
        title_embedding=serialize_embedding(title_emb),
        description_embedding=serialize_embedding(desc_emb)
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return db_project
