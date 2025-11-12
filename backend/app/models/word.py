from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class WordClick(Base):
    __tablename__ = "word_clicks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    word = Column(String(100), nullable=False, index=True)
    click_count = Column(Integer, default=1)
    first_clicked_at = Column(DateTime(timezone=True), server_default=func.now())
    last_clicked_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    mastery_status = Column(String(20), default="生词")  # 生词, 熟悉, 已掌握
    
    # 关系
    user = relationship("User", backref="word_clicks")
    document = relationship("Document", back_populates="word_clicks")
    
    # 复合索引
    __table_args__ = (
        Index('idx_user_word', 'user_id', 'word'),
        Index('idx_user_doc_word', 'user_id', 'document_id', 'word'),
    )

