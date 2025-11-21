from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import logging
from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document, Page
from app.models.word import WordClick
from app.schemas.document import DocumentResponse, DocumentListResponse, PageResponse
from app.api.v1.dependencies import get_current_user
from app.services.document_parser import parse_document

logger = logging.getLogger(__name__)

router = APIRouter()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文档（仅支持TXT格式）"""
    # 检查文件类型 - 仅支持TXT
    if not (file.content_type == 'text/plain' or file.filename.endswith('.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持 .txt 格式的文件"
        )
    
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
    
    # 删除文件（即使文件删除失败，也继续删除数据库记录）
    file_path = document.file_path
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"成功删除文件: {file_path}")
        except OSError as e:
            # 文件删除失败（可能是权限问题、文件被占用等），记录日志但继续删除数据库记录
            logger.warning(f"删除文件失败: {file_path}, 错误: {str(e)}")
        except Exception as e:
            # 其他异常，记录日志但继续删除数据库记录
            logger.error(f"删除文件时发生未知错误: {file_path}, 错误: {str(e)}")
    
    # 删除数据库记录（先删除关联记录，再删除文档）
    try:
        # 先删除关联的 WordClick 记录
        word_clicks = db.query(WordClick).filter(
            WordClick.document_id == document_id
        ).all()
        for word_click in word_clicks:
            db.delete(word_click)
        logger.info(f"删除关联的 WordClick 记录: {len(word_clicks)} 条")
        
        # 删除关联的 Page 记录
        pages = db.query(Page).filter(
            Page.document_id == document_id
        ).all()
        for page in pages:
            db.delete(page)
        logger.info(f"删除关联的 Page 记录: {len(pages)} 条")
        
        # 最后删除文档记录
        db.delete(document)
        db.commit()
        logger.info(f"成功删除文档记录: document_id={document_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"删除文档记录失败: document_id={document_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文档失败: {str(e)}"
        )
    
    return None

