from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from .database import Base

# SQLAlchemy Models
class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    register_no = Column(String, index=True)
    student_name = Column(String)
    title = Column(String)
    description = Column(Text)
    submission_date = Column(String)
    submission_time = Column(String)
    title_embedding = Column(Text)       # JSON string of floats
    description_embedding = Column(Text) # JSON string of floats

# Pydantic Schemas
class ProjectBase(BaseModel):
    register_no: str
    student_name: str
    title: str
    description: str
    submission_date: str
    submission_time: str

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int

    model_config = {"from_attributes": True}

class DuplicateCheckRequest(BaseModel):
    title: str
    description: str

class DuplicateCheckResponse(BaseModel):
    similarity_score: float
    matching_projects: List[ProjectResponse]
    exact_match_found: bool
