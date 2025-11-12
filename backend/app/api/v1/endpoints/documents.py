from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document, Page
from app.schemas.document import DocumentResponse, DocumentListResponse, PageResponse
from app.api.v1.dependencies import get_current_user
from app.services.document_parser import parse_document

router = APIRouter()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文档"""
    # 检查文件大小
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小超过限制"
        )
    
    # 保存文件
    file_path = os.path.join(settings.UPLOAD_DIR, f"{current_user.id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    
    try:
        # 解析文档
        full_content, pages = parse_document(file_path, file.content_type)
        
        # 创建文档记录
        db_document = Document(
            user_id=current_user.id,
            title=file.filename.rsplit('.', 1)[0],  # 使用文件名（不含扩展名）作为标题
            filename=file.filename,
            file_path=file_path,
            content=full_content,
            total_pages=len(pages)
        )
        db.add(db_document)
        db.flush()
        
        # 创建页面记录
        for page_num, page_content in enumerate(pages, 1):
            db_page = Page(
                document_id=db_document.id,
                page_number=page_num,
                content=page_content
            )
            db.add(db_page)
        
        db.commit()
        db.refresh(db_document)
        
        return db_document
    except Exception as e:
        # 如果解析失败，删除已上传的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文档解析失败: {str(e)}"
        )

@router.get("/", response_model=DocumentListResponse)
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的文档列表"""
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    total = db.query(Document).filter(
        Document.user_id == current_user.id
    ).count()
    
    return {"documents": documents, "total": total}

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文档详情"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    return document

@router.get("/{document_id}/pages/{page_number}", response_model=PageResponse)
async def get_page(
    document_id: int,
    page_number: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文档的某一页"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    page = db.query(Page).filter(
        Page.document_id == document_id,
        Page.page_number == page_number
    ).first()
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="页面不存在"
        )
    
    return page

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除文档"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    # 删除文件
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # 删除数据库记录（级联删除页面）
    db.delete(document)
    db.commit()
    
    return None

