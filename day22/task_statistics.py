


def calculate_task_statistics(tasks):
    total_count = len(tasks)
    completed_count = 0

    for task in tasks:
        if task.completed:
            completed_count += 1


    uncompleted_count =  total_count - completed_count


    if total_count == 0:
        completion_rate = 0


    else:
        completion_rate = completed_count / total_count * 100


    return{
        "total":total_count,
        "completed": completed_count,
        "uncompleted":uncompleted_count,
        "completion_rate":completion_rate
    }


