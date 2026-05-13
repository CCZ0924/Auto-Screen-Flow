# Capture.py
import numpy as np
import mss


def capture_screen(monitor_index: int = 2) -> np.ndarray:
    """
    截取指定显示器的屏幕，返回 BGR 格式的帧
    :param monitor_index: 显示器索引，1 表示主显示器（mss 中 1=主显示器, 2=副显示器...）
    :return: numpy 数组，形状为 (height, width, 3)，格式 BGR
    """
    with mss.mss() as sct:
        # 获取指定显示器信息
        monitor = sct.monitors[monitor_index]
        # 截取屏幕，得到 BGRA 格式的 numpy 数组
        img_bgra = np.array(sct.grab(monitor))
        # 去掉 alpha 通道，得到 BGR
        img_bgr = img_bgra[:, :, :3]
        return img_bgr


# 简单测试
if __name__ == "__main__":
    import cv2
    frame = capture_screen()
    print(f"捕获到帧，形状: {frame.shape}, 数据类型: {frame.dtype}")
    # 可选：显示几秒后关闭
    cv2.imshow("Capture Test", frame)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()