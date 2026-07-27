def show_tasks(tasks):
    print()
    print("当前任务:")


    for index, task in enumerate(tasks,start=1):
        if task["completed"] == True:
            status = "[X]"
        else:
            status = "[ ]"

        print(f"{index},{status} {task['name']}")

def complete_task(tasks):
    show_tasks(tasks)

    number_text = input("请输入要完成的任务编号:").strip()

    if number_text.isdigit():
        task_number = int(number_text)

        if 1<= task_number <= len(tasks):
            selected_task = tasks[task_number - 1]
            selected_task["completed"] = True

            print(f"任务'{selected_task['name']}'已完成.")

        else:
            print("任务编号不存在.")

    else:
        print("请输入有效的数字")



task1 = {
    "name":"学习python",
    "completed":False

}

task2 = {
    "name":"提交Github",
    "completed": True

}
tasks = [task1,task2]

complete_task(tasks)
show_tasks(tasks)

""" task_name = input("请输入新任务:").strip()

new_task = {
    "name":task_name,
    "completed":False
}
tasks.append(new_task) """



