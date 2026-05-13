# OCR.py
import cv2
import numpy as np
import pytesseract
from typing import Optional, Tuple

# 如果 tesseract 未在系统 PATH 中，请在此指定路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def ocr_locate(frame: np.ndarray,
               expected: str,
               region: Optional[Tuple[int, int, int, int]] = None,
               lang: str = 'chi_sim') -> Optional[Tuple[int, int]]:
    """
    在给定帧中识别期望文本，返回其中心坐标

    :param frame: 截图图像（BGR 格式或灰度均可）
    :param expected: 期望出现的文字（大小写不敏感）
    :param region: 搜索区域 (x, y, w, h)，相对于帧左上角；若为 None 则全帧搜索
    :param lang: 识别语言，默认英文，中文可传 'chi_sim'
    :return: 匹配文字的中心坐标 (x, y)，未找到则返回 None
    """
    if not expected:
        return None

    # 截取区域
    if region is not None:
        x, y, w, h = region
        roi = frame[y:y+h, x:x+w]
        offset_x, offset_y = x, y
    else:
        roi = frame
        offset_x, offset_y = 0, 0

    # 预处理：转灰度、二值化，提高识别率
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 使用 image_to_data 获取每个词的位置信息
    data = pytesseract.image_to_data(binary, lang=lang, output_type=pytesseract.Output.DICT)

    # 遍历所有识别出的文字
    for i in range(len(data['text'])):
        word = data['text'][i].strip()
        if expected.lower() in word.lower():
            # 提取边界框
            x_word = data['left'][i]
            y_word = data['top'][i]
            w_word = data['width'][i]
            h_word = data['height'][i]

            # 计算中心点（相对于原帧）
            center_x = offset_x + x_word + w_word // 2
            center_y = offset_y + y_word + h_word // 2
            return (center_x, center_y)

    return None