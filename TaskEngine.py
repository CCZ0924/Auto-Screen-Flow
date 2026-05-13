# TaskEngine.py
import json
from typing import Dict, Optional, Any


class TaskEngine:
    """
    任务引擎：读取 JSON 任务文件，提供任务查询与流转接口
    JSON 格式示例：
    {
        "Task1": {
            "description": "...",
            "recognition": "OCR/templatematch/start/None",
            "expected": "...",
            "action": "函数调用",
            "next": "Task2/None"
        },
        ...
    }
    """

    def __init__(self, json_path: str):
        """
        初始化任务引擎，加载并校验 JSON 文件
        :param json_path: JSON 文件路径
        """
        self.json_path = json_path
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """加载 JSON 文件并做基本校验"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"任务文件不存在: {self.json_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 格式错误: {e}")

        if not isinstance(data, dict):
            raise ValueError("JSON 顶层结构必须为对象")

        # 校验每个任务是否包含必要字段（至少应有 recognition 和 expected 字段）
        for task_name, task_info in data.items():
            if not isinstance(task_info, dict):
                raise ValueError(f"任务 '{task_name}' 的值必须为对象")
            # 可选：校验 recognition 字段合法性
            allowed_rec = {"OCR", "templatematch", "start", "None"}
            rec = task_info.get("recognition")
            if rec is not None and rec not in allowed_rec:
                print(f"警告：任务 '{task_name}' 的 recognition='{rec}' 可能不被支持")

        self.tasks = data

    def get_task(self, task_name: str) -> Dict[str, Any]:
        """
        获取指定名称的任务字典
        :param task_name: 任务名
        :return: 任务信息字典
        :raises KeyError: 任务不存在
        """
        if task_name not in self.tasks:
            raise KeyError(f"任务 '{task_name}' 不存在")
        return self.tasks[task_name]

    def get_next_task_name(self, task_name: str) -> Optional[str]:
        """
        获取当前任务指定的下一个任务名
        :param task_name: 当前任务名
        :return: 下一个任务名，如果 next 字段为 "None" 或不存在则返回 None
        """
        task = self.get_task(task_name)
        next_task = task.get("next")
        if next_task is None or next_task == "None":
            return None
        return next_task

    def get_all_task_names(self):
        """返回所有任务名称列表（插入顺序）"""
        return list(self.tasks.keys())

    def __repr__(self):
        return f"TaskEngine(tasks={len(self.tasks)}, file='{self.json_path}')"


# 简单测试（仅在直接执行时生效）
if __name__ == "__main__":
    # 创建示例 JSON 文件用于测试
    sample = {
        "Task1": {
            "description": "查找并点击登录按钮",
            "recognition": "templatematch",
            "expected": "images/login.png",
            "action": "click",
            "next": "Task2"
        },
        "Task2": {
            "description": "等待欢迎文字出现",
            "recognition": "OCR",
            "expected": "Welcome",
            "action": "noop",
            "next": "None"
        }
    }
    test_file = "test_tasks.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(sample, f, indent=4)

    engine = TaskEngine(test_file)
    print(engine)
    print("任务列表:", engine.get_all_task_names())
    task1 = engine.get_task("Task1")
    print("Task1 信息:", task1)
    next_name = engine.get_next_task_name("Task1")
    print("Task1 的下一个任务:", next_name)
    print("Task2 的下一个任务:", engine.get_next_task_name("Task2"))