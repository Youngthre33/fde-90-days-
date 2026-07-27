def calculate_quote(work_days, daily_price):
    total_price = work_days * daily_price
    return total_price


""" quote = calculate_quote(5,800)

service_fee = quote *0.1
final_price = quote +service_fee

print(f"基础报价:{quote}元")
print(f"服务费:{service_fee}元")
print(f"最终报价:{final_price}元")
 """


def show_menu():
    print()
    print("请选择操作:")
    print("1.添加任务")
    print("2.查看任务")
    print("3.删除任务")
    print("4.退出程序")





def show_tasks(tasks):
    print()
    print("=" * 30)
    print("当前任务")
    print("=" * 30)

    if len(tasks) == 0:
        print("目前任务空缺")
    else:
        for index,task in enumerate(tasks, start=1):
            print(f"{index}.{task}")

    print("=" * 30)



def add_task(tasks):
    task_name = input("请输入新任务:").strip()

    if task_name == "":
        print("任务内容不能为空")
    else:
        tasks.append(task_name)
        print(f"任务'{task_name}'添加成功,")






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
                print(f"任务'{deleted_task}'已删除")    

            else:
                print("任务编号不存在.")
        else:
            print("请输入有效的数字,")


def main():
    my_tasks = [ ]

    while True:
        show_menu()

        choice = input("请输入操作编号:").strip()

        if choice == "1":
            add_task(my_tasks)

        elif choice == "2":
            delete_task(my_tasks)

        elif choice == "3":
            delete_task(my_tasks)
        elif choice == "4":
            print("程序已退出")
            break

        else:
            print("请输入1到4之间的有效编号,,")


main()

