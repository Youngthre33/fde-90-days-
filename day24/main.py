import task as task_module
import storage 
import task_statistics 

PRIORITY_ORDER = {
    "高":1,
    "中":2,
    "低":3
}

PRIORITY_CHOICE_MAP = {
    "1":"高",
    "2":"中",
    "3":"低"
}






###展示菜单函数
def show_menu():
    print("\n===== 任务管理器 =====")
    print("1.查看任务")
    print("2.添加任务")
    print("3.完成任务")
    print("4.修改任务")
    print("5.删除任务")
    print("6.搜索任务")
    print("7.查看未完成的任务")
    print("8.查看已完成的任务")
    print("9.按优先级查看任务")
    print("10.修改任务优先级")
    print("11.查看任务统计")
    print("12.保存并退出")






##任务列表函数###
def show_tasks(tasks):
    if not tasks:
        print("当前没有任务,")
        return


    print("\n==== 任务列表 ====")

    for index, task in enumerate(tasks,start=1):
        if task.completed:
            status = "[x]"

        else:
            status = "[ ]"

        print(f"{index}.{status}[{task.priority}] {task.name}")

###统计计算函数




###统计函数
def show_task_statistics(tasks):
    statistics = task_statistics.calculate_task_statistics(tasks)

    print("\n ===== 任务统计 =====")
    print(f"任务总数:{statistics['total']}")
    print(f"已完成任务:{statistics['completed']}")
    print(f"未完成任务:{statistics['uncompleted']}")
    print(f"任务完成率:{statistics['completion_rate']:.1f}%")




###辅助函数  
def get_priority_value(task):
    return PRIORITY_ORDER.get(task.priority,2)



### 排序函数
def show_tasks_by_priority(tasks):
    if not tasks:
        print("当前没有任务可以排序,")
        return


    sorted_tasks = sorted(tasks, key=get_priority_value)


    print("\n===== 按优先级排序 =====")

    show_tasks(sorted_tasks)




def show_priority_options():
    print("1.高")
    print("2.中")
    print("3.低")


def get_priority_choice(prompt_text):
    show_priority_options()

    priority_choice = input(prompt_text).strip()

    return PRIORITY_CHOICE_MAP.get(priority_choice)




###搜索函数
def search_tasks(tasks):
    if not tasks :
        print("当前没有任务可以搜索,")
        return

    keyword = input("请输入搜索关键词:").strip()

    if not keyword:
        print("搜索关键词不能为空,")
        return


    matched_tasks =  []

    for task in tasks:
        if keyword in task.name:
            matched_tasks.append(task)


    if not matched_tasks:
        print(f"没有找到包含'{keyword}'的任务")
        return

    print(f"共找到{len(matched_tasks)}个任务:")

    show_tasks(matched_tasks)






###筛选函数
def filter_tasks(tasks,completed_status,status_text):
    filtered_tasks = []

    for task in tasks :
        if task.completed ==  completed_status:
            filtered_tasks.append(task)

    if not filtered_tasks:
        print(f"当前没有{status_text}任务,")
        return

    print(f"共找到{len(filtered_tasks)}个{status_text}任务:")

    show_tasks(filtered_tasks)


def show_uncompleted_tasks(tasks):
    filter_tasks(tasks,False,"未完成")




def show_completed_tasks(tasks):
    filter_tasks(tasks,True,"已完成")



###添加任务函数
def add_task(tasks):
    task_name = input("请输入新任务名称:").strip()

    if task_name == "":
        print("任务名称不能为空,")

        return

    print("请选择任务优先级:")
    priority = get_priority_choice("请输入优先级的编号:")



    if priority is None:
        print("优先级输入错误,将使用默认优先级'中'")
        priority = "中"


    new_task = task_module.Task(task_name,priority)

    
    tasks.append(new_task)

    storage.save_tasks(tasks)

    print(f"任务'{task_name}'添加任务成功,优先级为'{priority}'")


###选择编号函数
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




###完成函数
def complete_task(tasks):
   selected_task = select_task(tasks,"完成")

   if selected_task is None:
    return

   if selected_task.completed:
        print(f"任务'{selected_task.name}'已经完成了")

        return

   selected_task.complete()

   storage.save_tasks(tasks)


   print(f"任务'{selected_task.name}'已完成,")



 
### 修改任务函数
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

    storage.save_tasks(tasks)


    print(f"任务'{old_name}'已修改为'{new_name}'")




###删除函数
def delete_task(tasks):
   selected_task = select_task(tasks,"删除")
   if selected_task is None:
    return
   
   tasks.remove(selected_task)
   storage.save_tasks(tasks)

   print(f"任务'{selected_task.name}'已删除")



###修改优先级函数


def change_task_priority(tasks):
    selected_task = select_task(tasks,"修改优先级")

    if selected_task is None:
        return

    print(f"当前优先级:{selected_task.priority}")
    new_priority = get_priority_choice(
        "请选择新的优先级(1/2/3):"
    )
   


    if new_priority is None :
        print("优先级选择无效,")

        return
    
    selected_task.change_priority(new_priority)
    storage.save_tasks(tasks)


    print(f"任务'{selected_task.name}'的优先级"
          f"已经修改为'{selected_task.priority}'")



MENU_ACTIONS = {
    "1": show_tasks,
    "2": add_task,
    "3": complete_task,
    "4": rename_task,
    "5": delete_task,
    "6": search_tasks,
    "7": show_uncompleted_tasks,
    "8": show_uncompleted_tasks,
    "9":show_tasks_by_priority,
    "10":change_task_priority,
    "11":show_task_statistics
}






####主菜单
def main():
    tasks = storage.load_tasks()
    print(f'程序启动成功,已读取{len(tasks)}个任务')

    while True:
        show_menu()

        choice = input("请输入操作编号:").strip()
    

        if choice == "12":
        
            storage.save_tasks(tasks) 
            print("任务已经保存,程序退出,")
            break




        action = MENU_ACTIONS.get(choice)

        if action is None:
            print("请输入1-12之间的编号才可以滴")
            continue


        action(tasks)



if __name__ =="__main__":
    main()





