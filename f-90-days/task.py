from storage import save_tasks


def show_tasks(tasks):
    print()
    print("=" * 30)
    print("当前任务")
    print("=" * 30)

    if not tasks:
        print("目前任务空缺")
    else:
        for index,task in enumerate(tasks, start=1):
            if task["completed"] :
                status = "[x]"
            else:
                status = "[ ]"

            print(f"{index}.{status} {task['name']}")

    print("=" * 30)





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
    if not tasks:
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
    if not tasks:
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