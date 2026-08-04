from task import Task
from storage import save_tasks,load_tasks


def show_menu():
    print("\n===== 任务管理器 =====")
    print("1.查看任务")
    print("2.添加任务")
    print("3.完成任务")
    print("4.修改任务")
    print("5.删除任务")
    print("6.退出程序")






def show_tasks(tasks):
    if len(tasks) == 0:
        print("当前没有任务,")
        return


    print("\n==== 任务列表 ====")

    for index, task in enumerate(tasks,start=1):
        if task.completed:
            status = "[ x]"

        else:
            status = "[  ]"

        print(f"{index}.{status} {task.name}")





def add_task(tasks):
    task_name = input("请输入新任务名称:").strip()

    if task_name == "":
        print("任务名称不能为空,")

        return

    new_task = Task(task_name)
    tasks.append(new_task)

    save_tasks(tasks)

    print(f"任务'{task_name}'添加任务成功")



def select_task(tasks,action_text):
    if len(tasks) == 0:
        print(f"当前没有任务可以{action_text},")
        return None

    show_tasks(tasks)

    number_text = input(
        f"请输入要{action_text}的任务编号:"
    ).strip()

    if not number_text.isdigit():
        print("请输入正确的数字编号,")
        return None

    task_number = int(number_text)

    if task_number < 1 or task_number >len(tasks):
        print("任务编号不存在,")
        return  None

    return tasks[task_number -1]





def complete_task(tasks):
   selected_task = select_task(tasks,"完成")

   if selected_task is None:
    return

   if selected_task.completed:
        print(f"任务'{selected_task.name}'已经完成了")

        return

   selected_task.complete()

   save_tasks(tasks)


   print("f任务'{selected_task.name}'已完成,")



 

def rename_task(tasks):
    selected_task = select_task(tasks,"修改")

    if selected_task is None:
        return

    new_name = input("请输入新的任务名称:").strip()

    if new_name == "":
        print("任务名称不能为空,")
        return

    old_name = selected_task.name

    selected_task.rename(new_name)

    save_tasks(tasks)


    print(f"任务'{old_name}'已修改为'{new_name}'")


def delete_task(tasks):
   selected_task = select_task(tasks,"删除")
   if selected_task is None:
    return
   
   tasks.remove(selected_task)
   save_tasks(tasks)

   print(f"任务'{selected_task.name}'已删除")







def main():
    tasks = load_tasks()
    print(f'程序启动成功,已读取{len(tasks)}个任务')

    while True:
        show_menu()

        choice = input("请输入操作编号:").strip()
        
        if choice == "6":
        
            save_tasks(tasks) 
            print("任务已经保存,程序退出,")
            break



        elif choice == "1":
            show_tasks(tasks)

        elif choice =="2":
            add_task(tasks)

        elif choice == "3":
            complete_task(tasks)

        elif choice == "4":
            rename_task(tasks)

        elif choice == "5":
            delete_task(tasks)




        else:
            print("请输入1-6之间的编号才可以滴")

if __name__ =="__main__":
    main()





