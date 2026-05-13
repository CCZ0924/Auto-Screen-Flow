# Action.py
import subprocess
from typing import Optional
import pyautogui
import time


# 安全设置：鼠标移到屏幕左上角会立即停止，防止失控
pyautogui.FAILSAFE = False


def click(x: int, y: int) -> None:
    """
    移动鼠标到指定坐标并执行左键单击。

    Args:
        x: 目标横坐标（像素）
        y: 目标纵坐标（像素）

    """
    pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.click(x, y, button='left')
    time.sleep(0.5)


def press_key(key: str) -> None:
    """
    模拟键盘点按某个键（按下后立即释放）。

    Args:
        key: 要按下的键名，支持单字符如 'a', '1', 'enter', 'tab', 'space' 等。
             更完整的键名列表请参考 pyautogui.KEYBOARD_KEYS。

    """
    pyautogui.keyDown(key)
    time.sleep(0.05)
    pyautogui.keyUp(key)
    time.sleep(0.5)

def run_exe(exe_path: str) -> Optional[subprocess.Popen]:
    """
    通过 PowerShell 启动某个 exe 程序
    :param exe_path: exe 文件的完整路径（含扩展名）
    :return: 返回 Popen 对象，表示启动的进程
    """
    # 使用 Start-Process 启动可执行文件，能正确处理路径中的空格
    command = f"Start-Process -FilePath '{exe_path}' -Verb RunAs"
    # command = f"schtasks.exe /run /tn \"{exe_path}\""

    # 非阻塞启动
    return subprocess.Popen(["powershell", "-Command", command])
    
def do_nothing(duration: float = 0.0) -> None:
    """
    什么都不做（可选暂停指定秒数）
    :param duration: 暂停时长（秒），0 表示几乎不消耗时间
    """
    if duration > 0:
        time.sleep(duration)