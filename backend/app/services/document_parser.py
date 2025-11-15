import os
import re
import logging
from typing import List, Tuple, Optional
from PyPDF2 import PdfReader
import ebooklib
from ebooklib import epub

# OCR相关导入（可选）
try:
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("OCR libraries not available. Image PDF support will be limited.")

logger = logging.getLogger(__name__)

def parse_text_file(file_path: str) -> Tuple[str, List[str]]:
    """解析纯文本文件，支持Markdown格式（加粗、斜体）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 处理Markdown格式：将Markdown转换为HTML
    # 加粗：**text** 或 __text__ -> <strong>text</strong>
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'__(.+?)__', r'<strong>\1</strong>', content)
    
    # 斜体：*text* 或 _text_ -> <em>text</em>
    # 注意：需要避免与加粗冲突，先处理加粗再处理斜体
    content = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', content)
    content = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<em>\1</em>', content)
    
    # 简单分页：每500个字符一页
    pages = []
    page_size = 500
    for i in range(0, len(content), page_size):
        pages.append(content[i:i+page_size])
    
    return content, pages

def parse_pdf(file_path: str) -> Tuple[str, List[str]]:
    """解析PDF文件，支持文本PDF和图片PDF（OCR）"""
    reader = PdfReader(file_path)
    full_text = ""
    pages = []
    total_pages = len(reader.pages)
    
    # 首先尝试提取文本
    text_pages = []
    for page in reader.pages:
        page_text = page.extract_text()
        text_pages.append(page_text)
        if page_text:
            full_text += page_text + "\n"
            pages.append(page_text)
    
    # 检查是否大部分页面都没有文本（可能是图片PDF）
    empty_pages = sum(1 for text in text_pages if not text or len(text.strip()) < 10)
    is_image_pdf = empty_pages > total_pages * 0.5  # 如果超过50%的页面没有文本，认为是图片PDF
    
    # 如果是图片PDF且OCR可用，使用OCR识别
    if is_image_pdf and OCR_AVAILABLE:
        logger.info(f"Detected image PDF, using OCR for {total_pages} pages")
        try:
            # 将PDF转换为图片
            images = convert_from_path(file_path, dpi=300)
            
            # 重新处理所有页面
            full_text = ""
            pages = []
            
            for i, image in enumerate(images):
                # 使用OCR识别文本
                try:
                    # 配置OCR语言（英文）
                    ocr_text = pytesseract.image_to_string(image, lang='eng')
                    
                    # 清理OCR结果
                    ocr_text = ocr_text.strip()
                    
                    if ocr_text:
                        full_text += ocr_text + "\n"
                        pages.append(ocr_text)
                        logger.info(f"OCR extracted {len(ocr_text)} characters from page {i+1}")
                    else:
                        # 如果OCR没有提取到文本，使用原文本（如果有）或空字符串
                        pages.append(text_pages[i] if i < len(text_pages) else "")
                except Exception as e:
                    logger.warning(f"OCR failed for page {i+1}: {str(e)}")
                    # OCR失败时使用原文本
                    pages.append(text_pages[i] if i < len(text_pages) else "")
            
            logger.info(f"OCR completed. Extracted text from {len([p for p in pages if p])} pages")
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            # OCR失败时使用原文本
            if not pages:
                pages = text_pages
                full_text = "\n".join(text_pages)
    elif is_image_pdf and not OCR_AVAILABLE:
        logger.warning("Image PDF detected but OCR is not available. Install Tesseract OCR for full support.")
        # 如果没有OCR，至少返回空页面结构
        if not pages:
            pages = [""] * total_pages
    
    # 确保至少有一些内容
    if not pages:
        pages = [""] * total_pages
    
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

