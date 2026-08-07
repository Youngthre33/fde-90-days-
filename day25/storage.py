
import json

from task import Task

from pathlib import Path

FILE_NAME = Path(__file__).resolve().parent / "task.json"

def get_task_data_error(data):
    if not isinstance(data,dict):
        return "任务列表中存在不是字典的数据"

    if "name" not in data or "completed" not in data:
        return"任务数据缺少必要的字段"


    if not isinstance(data["name"],str) or data["name"].strip() == "":
        return"任务名称必须是非空字符串"

    if not isinstance(data["completed"],bool):
        return"任务完成状态必须是布尔值"

    priority = data.get("priority","中")

    if priority not in ["高","中","低"]:
        return"任务优先级无效"

    return None




def save_tasks(tasks):
    task_data = []

    for task in tasks :
        task_data.append(task.to_dict())


    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(
            task_data,
            file,
            ensure_ascii=False,
            indent=4
        )


def load_tasks():
    try:
        with open(FILE_NAME,"r",encoding="utf-8") as file:
            task_data = json.load(file)

    except FileNotFoundError :
        print("没有找到任务文件,将从空任务列表开始,")
        return[]
    except json.JSONDecodeError:
        print("任务文件内容损坏,将从空任务列表开始,")

        return[]

    if not isinstance(task_data,list):
        print("任务文件的数据结构错误,将从空任务列表开始,")
        return[]

    
    tasks = []

    for data in task_data:
        error_message = get_task_data_error(data)

        if error_message is not None:
            print(f"{error_message}将从空任务列表开始,")

            return[]

        


        task = Task.from_dict(data)
        tasks.append(task)
        


    return tasks

