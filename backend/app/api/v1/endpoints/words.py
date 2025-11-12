from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from app.core.database import get_db
from app.models.word import WordClick
from app.models.document import Document, Page
from app.schemas.word import (
    WordDefinition, WordClickResponse, WordDetailResponse,
    WordListResponse, WordContext
)
from app.api.v1.dependencies import get_current_user
from app.services.dictionary import get_word_definition
from datetime import datetime

router = APIRouter()

@router.get("/lookup", response_model=WordDefinition)
async def lookup_word(
    word: str,
    document_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查询单词释义并记录点击"""
    # 验证文档属于当前用户
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    # 获取单词释义
    definition = await get_word_definition(word)
    
    # 记录或更新点击
    word_click = db.query(WordClick).filter(
        WordClick.user_id == current_user.id,
        WordClick.document_id == document_id,
        WordClick.word == word.lower()
    ).first()
    
    if word_click:
        word_click.click_count += 1
        word_click.last_clicked_at = datetime.utcnow()
    else:
        word_click = WordClick(
            user_id=current_user.id,
            document_id=document_id,
            word=word.lower(),
            click_count=1
        )
        db.add(word_click)
    
    db.commit()
    
    return definition

@router.get("/", response_model=WordListResponse)
async def get_word_list(
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "last_clicked_at",  # click_count, last_clicked_at, word
    order: str = "desc",  # asc, desc
    mastery_status: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取生词列表"""
    query = db.query(WordClick).filter(WordClick.user_id == current_user.id)
    
    # 按掌握状态筛选
    if mastery_status:
        query = query.filter(WordClick.mastery_status == mastery_status)
    
    # 排序
    if sort_by == "click_count":
        order_func = desc(WordClick.click_count) if order == "desc" else WordClick.click_count
    elif sort_by == "word":
        order_func = WordClick.word if order == "asc" else desc(WordClick.word)
    else:  # last_clicked_at
        order_func = desc(WordClick.last_clicked_at) if order == "desc" else WordClick.last_clicked_at
    
    query = query.order_by(order_func)
    
    total = query.count()
    words = query.offset(skip).limit(limit).all()
    
    return {"words": words, "total": total}

@router.get("/{word}", response_model=WordDetailResponse)
async def get_word_detail(
    word: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单词详情，包括所有出现过的上下文"""
    # 获取该用户对该单词的所有点击记录
    word_clicks = db.query(WordClick).filter(
        WordClick.user_id == current_user.id,
        WordClick.word == word.lower()
    ).all()
    
    if not word_clicks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="单词不存在"
        )
    
    # 合并所有记录（按文档分组）
    word_dict = {}
    for wc in word_clicks:
        if wc.document_id not in word_dict:
            word_dict[wc.document_id] = {
                "click_count": 0,
                "first_clicked_at": wc.first_clicked_at,
                "last_clicked_at": wc.last_clicked_at,
                "mastery_status": wc.mastery_status
            }
        word_dict[wc.document_id]["click_count"] += wc.click_count
    
    # 获取所有上下文
    contexts = []
    for doc_id, info in word_dict.items():
        document = db.query(Document).filter(Document.id == doc_id).first()
        if document:
            # 在所有页面中查找包含该单词的句子
            pages = db.query(Page).filter(Page.document_id == doc_id).all()
            for page in pages:
                sentences = page.content.split('.')
                for sentence in sentences:
                    if word.lower() in sentence.lower():
                        contexts.append(WordContext(
                            word=word,
                            document_id=doc_id,
                            document_title=document.title,
                            page_number=page.page_number,
                            context=sentence.strip()
                        ))
                        break  # 每页只取一个上下文
    
    # 使用最新的点击记录作为主记录
    main_click = max(word_clicks, key=lambda x: x.last_clicked_at)
    
    return WordDetailResponse(
        id=main_click.id,
        user_id=main_click.user_id,
        document_id=main_click.document_id,
        word=main_click.word,
        click_count=sum(wc.click_count for wc in word_clicks),
        first_clicked_at=min(wc.first_clicked_at for wc in word_clicks),
        last_clicked_at=max(wc.last_clicked_at for wc in word_clicks),
        mastery_status=main_click.mastery_status,
        contexts=contexts
    )

@router.patch("/{word}/status", response_model=WordClickResponse)
async def update_word_status(
    word: str,
    mastery_status: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新单词的掌握状态"""
    word_clicks = db.query(WordClick).filter(
        WordClick.user_id == current_user.id,
        WordClick.word == word.lower()
    ).all()
    
    if not word_clicks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="单词不存在"
        )
    
    # 更新所有相关记录的掌握状态
    for wc in word_clicks:
        wc.mastery_status = mastery_status
    
    db.commit()
    db.refresh(word_clicks[0])
    
    return word_clicks[0]

