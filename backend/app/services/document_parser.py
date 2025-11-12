import os
import re
from typing import List, Tuple
from PyPDF2 import PdfReader
import ebooklib
from ebooklib import epub

def parse_text_file(file_path: str) -> Tuple[str, List[str]]:
    """解析纯文本文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 简单分页：每500个字符一页
    pages = []
    page_size = 500
    for i in range(0, len(content), page_size):
        pages.append(content[i:i+page_size])
    
    return content, pages

def parse_pdf(file_path: str) -> Tuple[str, List[str]]:
    """解析PDF文件"""
    reader = PdfReader(file_path)
    full_text = ""
    pages = []
    
    for page in reader.pages:
        page_text = page.extract_text()
        full_text += page_text + "\n"
        pages.append(page_text)
    
    return full_text, pages

def parse_epub(file_path: str) -> Tuple[str, List[str]]:
    """解析EPUB文件"""
    book = epub.read_epub(file_path)
    full_text = ""
    pages = []
    
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content().decode('utf-8')
            # 简单提取文本（去除HTML标签）
            text = re.sub(r'<[^>]+>', '', content)
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                full_text += text + "\n"
                pages.append(text)
    
    return full_text, pages

def parse_document(file_path: str, file_type: str) -> Tuple[str, List[str]]:
    """根据文件类型解析文档"""
    if file_type == "text/plain" or file_path.endswith('.txt'):
        return parse_text_file(file_path)
    elif file_type == "application/pdf" or file_path.endswith('.pdf'):
        return parse_pdf(file_path)
    elif file_type == "application/epub+zip" or file_path.endswith('.epub'):
        return parse_epub(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")

