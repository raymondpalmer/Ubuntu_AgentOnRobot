#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR增强的文档加载器
支持扫描版PDF的文字识别

功能:
- 扫描版PDF的OCR文字识别
- 中英文混合文本识别
- 图片PDF转文本
- 与现有知识库系统集成

作者: Dragon Robot AI System
创建时间: 2024
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import tempfile
import shutil

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
    
    # 尝试导入PDF处理库
    PDF2IMAGE_AVAILABLE = False
    PYMUPDF_AVAILABLE = False
    
    try:
        import pdf2image
        PDF2IMAGE_AVAILABLE = True
    except ImportError:
        pass
    
    try:
        import fitz  # PyMuPDF
        PYMUPDF_AVAILABLE = True
    except ImportError:
        pass
        
except ImportError as e:
    OCR_AVAILABLE = False
    PDF2IMAGE_AVAILABLE = False
    PYMUPDF_AVAILABLE = False
    print(f"⚠️ OCR功能不可用: {e}")

from langchain.schema import Document

logger = logging.getLogger(__name__)

class OCREnhancedLoader:
    """OCR增强的文档加载器"""
    
    def __init__(self, 
                 languages: List[str] = None,
                 dpi: int = 300,
                 confidence_threshold: int = 60):
        """
        初始化OCR加载器
        
        Args:
            languages: OCR识别语言列表，默认['chi_sim', 'eng']
            dpi: PDF转图片的DPI设置
            confidence_threshold: OCR置信度阈值
        """
        self.languages = languages or ['chi_sim', 'eng']
        self.dpi = dpi
        self.confidence_threshold = confidence_threshold
        self.ocr_available = OCR_AVAILABLE
        
        if not self.ocr_available:
            logger.warning("OCR功能不可用，将跳过扫描版PDF处理")
    
    def can_process_with_ocr(self, file_path: Path) -> bool:
        """
        检查文件是否可以用OCR处理
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否可以OCR处理
        """
        if not self.ocr_available:
            return False
        
        return file_path.suffix.lower() == '.pdf'
    
    def extract_text_with_ocr(self, file_path: Path) -> Optional[str]:
        """
        使用OCR从PDF提取文字
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            提取的文字内容，失败返回None
        """
        if not self.ocr_available:
            logger.warning("OCR功能不可用")
            return None
        
        try:
            logger.info(f"开始OCR处理: {file_path.name}")
            
            # 优先使用PyMuPDF
            if PYMUPDF_AVAILABLE:
                return self._extract_with_pymupdf(file_path)
            # 备用pdf2image
            elif PDF2IMAGE_AVAILABLE:
                return self._extract_with_pdf2image(file_path)
            else:
                logger.error("没有可用的PDF转图片库")
                return None
                
        except Exception as e:
            logger.error(f"OCR处理失败: {e}")
            return None
    
    def _extract_with_pymupdf(self, file_path: Path) -> Optional[str]:
        """
        使用PyMuPDF提取PDF图片并OCR
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            提取的文字内容
        """
        try:
            import fitz  # PyMuPDF
            
            logger.info(f"使用PyMuPDF处理: {file_path.name}")
            
            # 打开PDF文档
            pdf_doc = fitz.open(str(file_path))
            all_text = []
            lang_string = '+'.join(self.languages)
            
            # 处理前3页
            max_pages = min(3, len(pdf_doc))
            
            for page_num in range(max_pages):
                logger.info(f"处理第 {page_num + 1} 页...")
                
                page = pdf_doc[page_num]
                
                # 将页面转换为图片
                mat = fitz.Matrix(2.0, 2.0)  # 放大2倍提高清晰度
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # 转换为PIL图片
                from PIL import Image
                import io
                image = Image.open(io.BytesIO(img_data))
                
                # OCR识别
                try:
                    text = pytesseract.image_to_string(
                        image,
                        lang=lang_string,
                        config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟萬億中文英文'
                    )
                    
                    if text.strip():
                        all_text.append(f"=== 第 {page_num + 1} 页 ===\n{text.strip()}")
                        logger.info(f"第 {page_num + 1} 页提取了 {len(text.strip())} 字符")
                        
                except Exception as e:
                    logger.warning(f"第 {page_num + 1} 页OCR失败: {e}")
                    continue
            
            pdf_doc.close()
            
            if all_text:
                full_text = '\n\n'.join(all_text)
                logger.info(f"PyMuPDF OCR成功提取 {len(full_text)} 字符")
                return full_text
            else:
                logger.warning("PyMuPDF OCR未能提取到任何文字")
                return None
                
        except Exception as e:
            logger.error(f"PyMuPDF OCR处理失败: {e}")
            return None
    
    def _extract_with_pdf2image(self, file_path: Path) -> Optional[str]:
        """
        使用pdf2image提取PDF图片并OCR
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            提取的文字内容
        """
        try:
            import pdf2image
            
            logger.info(f"使用pdf2image处理: {file_path.name}")
            
            # 检查是否存在poppler工具
            try:
                # 尝试转换PDF为图片
                images = pdf2image.convert_from_path(
                    file_path,
                    dpi=self.dpi,
                    first_page=1,
                    last_page=3  # 只处理前3页进行测试
                )
            except Exception as e:
                logger.error(f"PDF转图片失败（可能需要安装poppler-utils）: {e}")
                return None
            
            all_text = []
            lang_string = '+'.join(self.languages)
            
            for i, image in enumerate(images):
                logger.info(f"处理第 {i+1} 页...")
                
                # OCR识别
                try:
                    text = pytesseract.image_to_string(
                        image,
                        lang=lang_string,
                        config='--psm 6'  # 统一文本块模式
                    )
                    
                    if text.strip():
                        all_text.append(f"=== 第 {i+1} 页 ===\n{text.strip()}")
                        
                except Exception as e:
                    logger.warning(f"第 {i+1} 页OCR失败: {e}")
                    continue
            
            if all_text:
                full_text = '\n\n'.join(all_text)
                logger.info(f"pdf2image OCR成功提取 {len(full_text)} 字符")
                return full_text
            else:
                logger.warning("pdf2image OCR未能提取到任何文字")
                return None
                
        except Exception as e:
            logger.error(f"pdf2image OCR处理失败: {e}")
            return None
    
    def _fallback_ocr_method(self, file_path: Path) -> Optional[str]:
        """
        备用OCR方法（当pdf2image不可用时）
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            提取的文字内容
        """
        try:
            logger.info("尝试备用OCR方法...")
            
            # 使用PyPDF2先尝试提取
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(str(file_path))
                text_content = []
                
                for page_num, page in enumerate(reader.pages[:3]):  # 前3页
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(f"=== 第 {page_num+1} 页 ===\n{text.strip()}")
                
                if text_content:
                    return '\n\n'.join(text_content)
                    
            except Exception as e:
                logger.warning(f"PyPDF2提取失败: {e}")
            
            # 如果PyPDF2也失败，返回None
            logger.warning("所有文字提取方法都失败")
            return None
            
        except Exception as e:
            logger.error(f"备用OCR方法失败: {e}")
            return None
    
    def load_document_with_ocr(self, file_path: Path) -> List[Document]:
        """
        使用OCR加载文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            Document列表
        """
        try:
            # 先尝试常规方法提取文字
            from langchain_community.document_loaders import PyPDFLoader
            
            regular_loader = PyPDFLoader(str(file_path))
            docs = regular_loader.load()
            
            # 检查是否有有效内容
            has_content = any(doc.page_content.strip() for doc in docs)
            
            if has_content:
                logger.info(f"常规方法成功提取文字: {file_path.name}")
                return docs
            
            # 如果常规方法没有内容，尝试OCR
            logger.info(f"常规方法无内容，尝试OCR: {file_path.name}")
            ocr_text = self.extract_text_with_ocr(file_path)
            
            if ocr_text:
                # 创建Document对象
                doc = Document(
                    page_content=ocr_text,
                    metadata={
                        "source": str(file_path),
                        "extraction_method": "ocr",
                        "languages": '+'.join(self.languages),  # 转换为字符串
                        "filename": file_path.name
                    }
                )
                logger.info(f"OCR成功提取文档: {file_path.name}")
                return [doc]
            else:
                logger.warning(f"OCR也无法提取文字: {file_path.name}")
                return []
                
        except Exception as e:
            logger.error(f"OCR文档加载失败: {e}")
            return []
    
    def get_ocr_info(self) -> Dict[str, Any]:
        """
        获取OCR配置信息
        
        Returns:
            OCR配置字典
        """
        info = {
            "ocr_available": self.ocr_available,
            "pymupdf_available": PYMUPDF_AVAILABLE,
            "pdf2image_available": PDF2IMAGE_AVAILABLE,
            "languages": self.languages,
            "dpi": self.dpi,
            "confidence_threshold": self.confidence_threshold
        }
        
        if self.ocr_available:
            try:
                info["tesseract_version"] = pytesseract.get_tesseract_version()
                info["available_languages"] = pytesseract.get_languages()
            except Exception as e:
                info["tesseract_error"] = str(e)
        
        return info

# 测试OCR功能
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建OCR加载器
    ocr_loader = OCREnhancedLoader()
    
    # 显示OCR信息
    info = ocr_loader.get_ocr_info()
    print("=== OCR配置信息 ===")
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # 如果有测试文件，可以测试
    test_files = [
        "knowledge_base/files/连续上央视！TeleAI 讲了什么？.pdf",
        "knowledge_base/files/ICML 2025  TeleAI 聚焦正激励噪声与多智能体隐私安全.pdf"
    ]
    
    for test_file in test_files:
        file_path = Path(test_file)
        if file_path.exists():
            print(f"\n=== 测试文件: {file_path.name} ===")
            
            if ocr_loader.can_process_with_ocr(file_path):
                docs = ocr_loader.load_document_with_ocr(file_path)
                print(f"提取结果: {len(docs)} 个文档")
                
                if docs:
                    content_preview = docs[0].page_content[:200]
                    print(f"内容预览: {content_preview}...")
            else:
                print("文件不适合OCR处理")