# 读取非默认文本所使用的包以及函数
import fitz
import zipfile
import xml.etree.ElementTree as ET


def read_pdf_limited_with_fitz(path, limit=None):#读取pdf
    doc = fitz.open(path)
    parts = []
    total = 0
    for page in doc:
        text = page.get_text("text")
        remaining = limit - total if limit else None
        if remaining is not None and remaining <= 0:
            break
        if remaining is not None and len(text) > remaining:
            parts.append(text[:remaining])
            break
        parts.append(text)
        total += len(text)
    doc.close()
    result = "\n".join(parts)
    return result[:limit] if limit else result  # ← 统一截断


def read_docx_text_from_xml(path, limit=None):#读取docx
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(path) as docx_zip:
        with docx_zip.open('word/document.xml') as xml_file:
            context = ET.iterparse(xml_file, events=('start', 'end'))
            _, root = next(context)  # 获取根元素

            text_parts = []
            total_len = 0

            for event, elem in context:
                if event == 'end' and elem.tag.endswith('}t'):
                    if elem.text:
                        text_parts.append(elem.text)
                        total_len += len(elem.text)
                        if limit and total_len >= limit:
                            break
                    elem.clear()

            full_text = ''.join(text_parts)
            return full_text[:limit] if limit else full_text
