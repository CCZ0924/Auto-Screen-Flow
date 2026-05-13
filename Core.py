# Core.py
import re
import time
from typing import Optional

from Capture import capture_screen
from OCR import ocr_locate
from TemplateMatch import template_locate
from Action import click, press_key, run_exe, do_nothing
from TaskEngine import TaskEngine


def _parse_action_arg(action_str: str) -> str:
    """
    从 'press_key(enter)' 或 'run(C:\\app.exe)' 中提取括号内的参数
    若无括号或为 'None' 则返回空字符串
    """
    if action_str == "None" or action_str is None:
        return ""
    match = re.search(r"\((.*)\)", action_str)
    if match:
        return match.group(1).strip()
    return ""


def _execute_recognition(recognition: str, expected: str, frame):
    """
    执行识别步骤，返回坐标 (x,y) 或 None
    """
    if recognition == "OCR":
        return ocr_locate(frame, expected)
    elif recognition == "templatematch":
        return template_locate(frame, expected)
    else:
        # runexe 或 None 不需要识别
        return None


def _execute_action(action: str, coords, retry_on_click_fail: bool = True, max_retries: int = 3):
    """
    执行动作，coords 为 (x,y) 或 None
    """
    action_type = action.split('(')[0].strip()

    if action_type == "click":
        if coords is not None:
            x, y = coords
            click(x, y)
            return True
        else:
            print("警告：click 动作缺少有效坐标，已跳过")
            return False

    elif action_type == "press_key":
        key = _parse_action_arg(action)
        if key:
            press_key(key)
        else:
            print(f"警告：无法解析按键名称，action='{action}'")
        return True

    elif action_type == "run":
        exe_path = _parse_action_arg(action)
        if exe_path:
            run_exe(exe_path)
        else:
            print(f"警告：无法解析 exe 路径，action='{action}'")
        return True

    elif action == "None" or action_type == "None":
        do_nothing()
        return True

    else:
        print(f"警告：未知动作类型 '{action}'，已忽略")
        return False


def run_workflow(json_path: str, start_task: Optional[str] = None,
                 recognition_timeout: float = 50.0, retry_interval: float = 1.0) -> None:
    """
    执行整个自动化流程
    :param json_path: 任务 JSON 文件路径
    :param start_task: 起始任务名，默认使用 JSON 中的第一个任务
    :param recognition_timeout: 识别重试最大时间（秒）
    :param retry_interval: 识别重试间隔（秒）
    """
    engine = TaskEngine(json_path)

    # 确定起始任务
    if start_task is None:
        # 默认取任务列表第一个
        all_tasks = engine.get_all_task_names()
        if not all_tasks:
            print("任务列表为空")
            return
        current_task_name = all_tasks[0]
    else:
        current_task_name = start_task

    print(f"开始执行流程，起始任务: {current_task_name}")

    while current_task_name:
        task = engine.get_task(current_task_name)
        description = task.get("description", "None")
        recognition = task.get("recognition", "None")
        expected = task.get("expected", "")
        action = task.get("action", "None")
        recog_delay = task.get("recog_delay", 0.0)
        after_delay = task.get("after_delay", 0.0)
        action_repeat = task.get("action_repeat", 1)
        print(f"\n--- 执行任务: {current_task_name} ---")
        print(f"描述: {description}")
        print(f"识别方式: {recognition}, 期望: {expected}, 动作: {action}")

        # 执行识别（需要时可能会多次截图重试）
        coords = None
        if recognition in ("OCR", "templatematch"):
            start_time = time.time()
            while time.time() - start_time < recognition_timeout:
                frame = capture_screen()
                coords = _execute_recognition(recognition, expected, frame)
                if coords is not None:
                    print(f"识别成功，坐标: {coords}")
                    if recog_delay > 0:
                        time.sleep(recog_delay)
                    break
                time.sleep(retry_interval)
            else:
                print(f"识别超时，未找到目标: {expected}")
        elif recognition == "runexe":
            # 无识别，直接执行后续动作
            pass
        elif recognition == "None":
            pass
        else:
            print(f"未知识别方式: {recognition}")

        # 执行动作
        if action != "None":
            for _ in range(action_repeat):
                _execute_action(action, coords)
                time.sleep(2)  # 每次动作后稍作停顿

        # 延迟执行后续动作
        if after_delay > 0:
            time.sleep(after_delay)

        # 获取下一个任务
        next_task_name = engine.get_next_task_name(current_task_name)
        if next_task_name:
            print(f"转到下一任务: {next_task_name}")
        else:
            print("流程结束")
        current_task_name = next_task_name


# 测试入口（需配合有效的 JSON 文件）
if __name__ == "__main__":
    run_workflow("Task.json")  # 你的任务文件