from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DocumentBase(BaseModel):
    title: str

class DocumentCreate(DocumentBase):
    filename: str
    content: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: int
    user_id: int
    filename: str
    total_pages: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PageResponse(BaseModel):
    id: int
    document_id: int
    page_number: int
    content: str
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int

