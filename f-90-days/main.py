from storage import load_tasks
from task import add_task
from task import delete_task
from task import complete_task
from task import show_tasks

def show_menu():
    print()
    print("请选择操作:")
    print("1.添加任务")
    print("2.查看任务")
    print("3.完成任务")
    print("4.删除任务")
    print("5.退出程序")


def main():

    my_tasks = load_tasks()

    while True:
        show_menu()

        choice = input("请输入操作编号:").strip()


        if choice == "1":
            add_task(my_tasks)

        elif choice =="2":
            show_tasks(my_tasks)    

        elif choice =="3":            
           complete_task(my_tasks)

        elif choice == "4":
            delete_task(my_tasks)

        elif choice == "5":
            print("程序已退出")
            break

        else:
            print("请输入有效的数字编号")

if __name__ == "__main__":
 main()

