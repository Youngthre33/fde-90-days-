

import json


def show_menu():
    print()
    print("请选择操作:")
    print("1.添加任务")
    print("2.查看任务")
    print("3.完成任务")
    print("4.删除任务")
    print("5.退出程序")





def show_tasks(tasks):
    print()
    print("=" * 30)
    print("当前任务")
    print("=" * 30)

    if len(tasks) == 0:
        print("目前任务空缺")
    else:
        for index,task in enumerate(tasks, start=1):
            if task["completed"] :
                status = "[x]"
            else:
                status = "[ ]"

            print(f"{index}.{status} {task['name']}")

    print("=" * 30)

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



def add_task(tasks):
    task_name = input("请输入新任务:").strip()

    if task_name == "":
        print("任务内容不能为空")
    else:
        new_task = {
            "name":task_name,
            "completed":False
        }
        tasks.append(new_task)
        save_tasks(tasks)
        print(f"任务'{task_name}'添加成功,")


def complete_task(tasks):
    if len(tasks) == 0:
           print("目前没有任务可以完成.")

    else:
       show_tasks(tasks)
       number_text = input("请输入要完成的任务编号:").strip()
       
       if number_text.isdigit():
            task_number = int(number_text)

            if 1 <= task_number <= len(tasks):
                selected_task = tasks[task_number -1]
                selected_task["completed"] = True
                save_tasks(tasks)
                print(f"任务'{selected_task['name']}'已完成")
       

            else:
                print("任务编号不存在")

       else:
            print("请输入有效的数字")        
            
def delete_task(tasks):
    if len(tasks) == 0:
        print("目前没有任务可以删除.")
    else:
        show_tasks(tasks)

        task_number = input("请输入要删除的任务编号:").strip()

        if task_number.isdigit():
            task_number = int(task_number)

            if 1 <= task_number <= len(tasks):
                deleted_task = tasks.pop(task_number - 1)
                save_tasks(tasks)
                print(f"任务'{deleted_task['name']}'已删除")    

            else:
                print("任务编号不存在.")
        else:
            print("请输入有效的数字,")


def main():
    my_tasks = load_tasks()

    while True:
        show_menu()

        choice = input("请输入操作编号:").strip()

        if choice == "1":
            add_task(my_tasks)

        elif choice == "2":
            show_tasks(my_tasks)

        elif choice == "3":
            complete_task(my_tasks)

        elif choice == "4":
            delete_task(my_tasks)
        elif choice == "5":
            print("程序已退出")
            break

        else:
            print("请输入1到5之间的有效编号")




""" file = open("test.txt","w",encoding="utf-8")
file.write("学习python")
file.close()
 """
main()