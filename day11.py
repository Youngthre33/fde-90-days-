class Task:
    def __init__(self,name):
        self.name = name
        self.completed = False

    def complete(self):
        self.completed = True
    def rename(self,new_name):
        self.name = new_name

    def to_dict(self):
        return{
            "name":self.name,
            "completed":self.completed
        }
    @classmethod
    def from_dict(cls,data):
        task = cls(data["name"])
        task.completed = data["completed"]
        return task
    

def show_menu():
    print("\n-----任务管理器 -----")
    print("1,添加任务")
    print("2,查看任务")
    print("3.完成任务")
    print("4.删除任务")
    print("5.修改任务")
    print("6.退出程序")


def main():
    tasks =[]


    while True:
        show_menu()

        choice = input("请选择操作:").strip()


        if choice == "1":
            add_task(tasks)

        elif choice == "2":
            show_tasks(tasks)

        elif choice == "3":
            complete_task(tasks)

        elif choice == "4":
            delete_task(tasks)

        elif choice == "5":
            rename_task(tasks)

        elif choice == "6":
            print("程序已退出")

            break



        else:
            print("请输入1-6之间的数字,")



        


    
def add_task(tasks):
    task_name = input("请输入新任务:").strip()


    if task_name == "":
        print("任务内容不能为空,")
        return


    new_task = Task(task_name)
    tasks.append(new_task)


    print(f"任务'{new_task.name}'添加成功,")


def complete_task(tasks):
    if not tasks:
        print("目前任务列表为空")

        return

    show_tasks(tasks)

    number_text = input("请输入要完成的任务编号:").strip()


    if not number_text.isdigit():
        print("请输入有效的数字,")

        return


    task_number = int (number_text)

    if not 1 <= task_number <= len(tasks):
        print("任务编号不存在,")
        return

    selected_task = tasks[task_number - 1]
    selected_task.complete()


    print(f"任务'{selected_task.name}'已完成,")





def show_tasks(tasks):
    if not tasks:
        print("目前没有任务,")
        return


    for index, task in enumerate(tasks,start=1):
        if task.completed:
            status = "[ x]"

        else:
            status = "[ ]"

        print(f"{index}.{status} {task.name}")

def rename_task(tasks):
    if not tasks:
        print("目前没有任务可以修改,")
        return

    show_tasks(tasks)

    number_text = input("请输入要修改的任务编号:").strip()

    if not number_text.isdigit():
        print("请输入有效的数字,")

        return
    task_number = int(number_text)

    if not 1 <= task_number <= len(tasks):
        print("任务编号不存在,")
        return

    new_name = input("请输入新的任务名称:").strip()

    if new_name == "":
        print("任务名称不能为空,")
        return



    selected_task = tasks[task_number - 1]

    selected_task.rename(new_name)

    print(f"任务名称已修改为:{selected_task.name}")




def delete_task(tasks):
    if not tasks:
        print("目前没有任务可以删除,")
        return

    show_tasks(tasks)

    number_text = input("请输入要删除的任务编号:").strip()

    if not number_text.isdigit():
        print("请输入有效的数字,")
        return

    task_number = int(number_text)

    if not 1 <= task_number <= len(tasks):
        print("任务编号不存在,")

        return

    deleted_task = tasks.pop(task_number -1)

    print(f"任务'{deleted_task.name}'已删除,")


    


if __name__ == "__main__":
    main()






