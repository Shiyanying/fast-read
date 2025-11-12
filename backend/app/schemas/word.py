from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class WordClickBase(BaseModel):
    word: str

class WordClickResponse(WordClickBase):
    id: int
    user_id: int
    document_id: int
    click_count: int
    first_clicked_at: datetime
    last_clicked_at: datetime
    mastery_status: str
    
    class Config:
        from_attributes = True

class WordDefinition(BaseModel):
    word: str
    phonetic: Optional[str] = None
    meanings: List[dict] = []
    source: str = "dictionary-api"

class WordContext(BaseModel):
    word: str
    document_id: int
    document_title: str
    page_number: int
    context: str  # 包含该单词的句子或段落

class WordDetailResponse(WordClickResponse):
    contexts: List[WordContext] = []

class WordListResponse(BaseModel):
    words: List[WordClickResponse]
    total: int

