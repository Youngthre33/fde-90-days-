
import json

from task import Task

from pathlib import Path

FILE_NAME = Path(__file__).resolve().parent / "task.json"


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
        return[]


    tasks = []

    for data in task_data:
        task = Task.from_dict(data)
        tasks.append(task)


    return tasks

