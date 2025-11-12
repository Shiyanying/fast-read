import httpx
from typing import Optional
from app.schemas.word import WordDefinition
from app.core.config import settings

async def get_word_definition(word: str) -> Optional[WordDefinition]:
    """获取单词释义"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{settings.DICTIONARY_API_URL}/{word.lower()}"
            response = await client.get(url, timeout=5.0)
            
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
                    
                    return WordDefinition(
                        word=word,
                        phonetic=phonetic,
                        meanings=meanings,
                        source="dictionary-api"
                    )
    except Exception as e:
        print(f"获取单词释义失败: {e}")
    
    # 如果API失败，返回基础信息
    return WordDefinition(
        word=word,
        meanings=[],
        source="fallback"
    )

