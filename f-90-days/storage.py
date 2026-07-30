import json

def save_tasks(tasks):
    with open ("tasks.json","w",encoding="utf-8") as file:
        json.dump(tasks,file, indent=4,
                  ensure_ascii=False)

def load_tasks():
    tasks = []
    try:

        with open("tasks.json","r",encoding="utf-8") as file:
            tasks = json.load(file)

       
    except FileNotFoundError:
        print("暂时没有任务记录，将创建新的任务列表")
    
    except json.JSONDecodeError:
        print("暂时没有任务记录,将创建新的任务列表")

    return tasks
