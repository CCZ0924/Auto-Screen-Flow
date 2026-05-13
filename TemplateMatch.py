# templatematch.py
import cv2
import numpy as np
from typing import Optional, Tuple


def template_locate(frame: np.ndarray,
                    template_path: str,
                    threshold: float = 0.8,
                    region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
    """
    在帧中查找模板图像，返回匹配区域的中心坐标

    :param frame: 截图图像（BGR 格式）
    :param template_path: 模板图片文件路径
    :param threshold: 匹配阈值（0~1），建议 0.7~0.9
    :param region: 搜索区域 (x, y, w, h)，None 表示全帧
    :return: 匹配中心坐标 (x, y)，未找到返回 None
    """
    # 读取模板（保留彩色）
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        raise FileNotFoundError(f"模板图片不存在: {template_path}")

    # 限定搜索区域
    if region is not None:
        x, y, w, h = region
        search_img = frame[y:y+h, x:x+w]
        offset_x, offset_y = x, y
    else:
        search_img = frame
        offset_x, offset_y = 0, 0

    # 执行匹配
    result = cv2.matchTemplate(search_img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        # 模板的宽高
        t_h, t_w = template.shape[:2]
        # 匹配区域的左上角（相对于 search_img）
        match_x, match_y = max_loc
        # 中心坐标（相对于原帧）
        center_x = offset_x + match_x + t_w // 2
        center_y = offset_y + match_y + t_h // 2
        return (center_x, center_y)

    return None