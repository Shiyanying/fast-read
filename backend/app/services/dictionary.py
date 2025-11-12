import httpx
import logging
from typing import Optional
from functools import lru_cache
from datetime import datetime, timedelta
from app.schemas.word import WordDefinition
from app.core.config import settings

logger = logging.getLogger(__name__)

# 简单的内存缓存（生产环境建议使用 Redis）
_word_cache = {}
_cache_expiry = {}

async def get_word_definition(word: str) -> Optional[WordDefinition]:
    """获取单词释义（带缓存）"""
    word_lower = word.lower()
    
    # 检查缓存
    if word_lower in _word_cache:
        expiry = _cache_expiry.get(word_lower)
        if expiry and datetime.now() < expiry:
            logger.debug(f"Cache hit for word: {word_lower}")
            return _word_cache[word_lower]
        else:
            # 缓存过期，清除
            _word_cache.pop(word_lower, None)
            _cache_expiry.pop(word_lower, None)
    
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=2.0)) as client:
            url = f"{settings.DICTIONARY_API_URL}/{word_lower}"
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    entry = data[0]
                    
                    # 提取音标
                    phonetic = entry.get("phonetic", "")
                    if not phonetic and "phonetics" in entry:
                        for ph in entry["phonetics"]:
                            if ph.get("text"):
                                phonetic = ph["text"]
                                break
                    
                    # 提取释义
                    meanings = []
                    if "meanings" in entry:
                        for meaning in entry["meanings"]:
                            part_of_speech = meaning.get("partOfSpeech", "")
                            definitions = []
                            for def_item in meaning.get("definitions", []):
                                definitions.append({
                                    "definition": def_item.get("definition", ""),
                                    "example": def_item.get("example", "")
                                })
                            meanings.append({
                                "partOfSpeech": part_of_speech,
                                "definitions": definitions
                            })
                    
                    result = WordDefinition(
                        word=word_lower,
                        phonetic=phonetic,
                        meanings=meanings
                    )
                    
                    # 缓存结果（24小时）
                    _word_cache[word_lower] = result
                    _cache_expiry[word_lower] = datetime.now() + timedelta(hours=24)
                    
                    logger.debug(f"Cached word definition: {word_lower}")
                    return result
    except Exception as e:
        logger.error(f"获取单词释义失败: {e}")
    
    # 如果API失败，返回基础信息
    return WordDefinition(
        word=word_lower,
        meanings=[],
        source="fallback"
    )

