print("=" *34)
print("     个人任务管理器")
print("=" *33)
tasks = []
while True:
    print()
    print("请选择操作:")
    print("1.添加任务")
    print("2.查看任务")
    print("3.删除任务")
    print("4.退出程序")

    choice = input("请输入选项:").strip()


    if choice == "1":
        task_name = input("请输入新任务:").strip()

        if task_name == "":
            print("任务内容不能为空.")
        else:
            tasks.append(task_name)
            print(f"任务'{task_name}'添加成功, ")

    elif choice == "2":
        print()
        print("=" *30)
        print("      当前任务")
        print("="*30)

        if len(tasks) == 0:
            print("目前没有任务,")
        else:
            for index, task in enumerate(tasks, start=1):
                print(f"{index}. {task}")


        print("="* 30)

    elif choice == "3":
        if len(tasks) == 0:
            print("目前没有可以删除的任务,")
        else:
            print("当前任务:")


            for index, task in enumerate(tasks,start=1):
                print(f"{index},{task}")


            number_text = input("请输入要删除的任务编号:").strip()

            if number_text.isdigit():
                task_number = int(number_text)

                if 1 <= task_number <= len(tasks):
                    deleted_task = tasks.pop(task_number - 1)
                    print(f"任务'{deleted_task}'已删除")
                else:     
                    print("没有这个任务编号.")
            else:
                print("请输入正确的数字,")        

    elif choice == "4":  
        print("任务管理器已退出,")       

        break


    else:
        print("选项错误,请输入1,2,3或者4")

