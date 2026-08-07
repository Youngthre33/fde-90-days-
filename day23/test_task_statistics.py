import task_statistics

import task as task_module

def test_empty_task_statistics():
    tasks = []

    result = task_statistics.calculate_task_statistics(tasks)

    assert result["total"] == 0,(
        f"空列表的任务总数应为0,实际结果:{result['total']!r}"
    )
    assert result["completed"] == 0, (
        f"空列表的已完成数量应为0,实际结果:{result['completed']!r}"
    )

    assert result["uncompleted"] == 0, (
        f"空列表的未完成数量应为0, 实际结果:{result['uncompleted']!r}"
    )

    assert result["completion_rate"] == 0, (
        f"空列表的完成率应为0, 实际结果;{result['completion_rate']!r}"
    )


def test_one_uncompleted_task_statistics():
    first_task = task_module.Task("学习python","高")

    tasks = [first_task]


    result = task_statistics.calculate_task_statistics(tasks)

    assert result["total"] == 1,(
        f"任务总数应为1, 实际结果:{result['total']!r}"
    )

    assert result["completed"] == 0,(
        f"已完成数量应为0, 实际结果:{result['completed']!r}"
    )

    assert result["uncompleted"] == 1,(
        f"未完成数量应为1,实际结果:{result['uncompleted']!r}"
    )
    assert result["completion_rate"] == 0,(
        f"完成率应为0,实际结果:{result['completion_rate']!r}"
    )


def test_one_completed_task_statistics():
    first_task = task_module.Task("学习python","高")
    first_task.completed = True


    tasks = [first_task]


    result =  task_statistics.calculate_task_statistics(tasks)


    assert result["total"] == 1,(
        f"任务总数应为1, 实际结果,{result['total']!r}"
    )

    assert result["completed"] == 1,(
        f"已完成数量应为1,实际结果:{result['completed']!r}"
    )

    assert result["completion_rate"] == 100, (
        f"完成率应为100, 实际结果:{result['completion_rate']!r}"
    )


def test_mixed_task_statistics():
    first_task = task_module.Task("学习python","高")
    second_task = task_module.Task("整理笔记","中")
    third_task = task_module.Task("提交代码","高")
    fourth_task = task_module.Task("复习测试","低")


    first_task.completed = True

    second_task.completed = True

    third_task.completed = True

    tasks = [
        first_task,
        second_task,
        third_task,
        fourth_task
    ]
    result = task_statistics.calculate_task_statistics(tasks)

    assert result["total"] ==  4,(
        f"任务总数应为4, 实际结果:{result['total']!r}"

    )

    assert result["completed"] == 3, (
        f"已完成数量应为3, 实际结果:{result['completed']!r}"
    )

    assert result["uncompleted"] ==  1,(
        f"未完成数量应为1,实际结果:{result['uncompleted']!r}"
    )

    assert result["completion_rate"] == 75,(
        f"完成率应为75, 实际结果:{result['completion_rate']!r}"
    )


def  test_statistics_result_is_snapshot():
    first_task = task_module.Task("学习python","高")
    tasks = [first_task]

    first_result = task_statistics.calculate_task_statistics(tasks)


    assert first_result["completed"] == 0, (
        f"任务最初未完成,已完成数量应为0,实际结果:"
        f"{first_result['completed']!r}"

    )

    first_task.completed = True

    assert first_result["completed"] == 0,(
        f"旧统计结果不应自动变化,实际结果:"
        f"{first_result['completed']!r}"

    )

    second_result = task_statistics.calculate_task_statistics(tasks)

    assert second_result["completed"] == 1,(
        f"重新统计后,已完成数量应为1,实际结果:"
        f"{second_result['completed']!r}"
    )

    assert first_result is not second_result,(
        "每次调用统计函数都应该返回一个新的统计字典"
    )

def test_statistics_does_not_modify_tasks():
    first_task = task_module.Task("学习python","高")

    second_task = task_module.Task("整理笔记","中")

    second_task.completed = True

    tasks = [
        first_task,
        second_task
    ]   

    result = task_statistics.calculate_task_statistics(tasks)

    assert result["total"] == 2, (
        f"任务总数应为2, 实际结果:{result['total']!r}"
    )

    assert result["completed"] == 1,(
        f"已完成数量应为1,实际结果:{result['completed']!r}"
    )

    assert len(tasks) ==2,(
        f"统计函数不应改变列表长度, 实际长度:{len(tasks)!r}"
    )



    assert tasks[0] is first_task,(
        "统计函数不应替换或移动第二个任务对象"

    )

    assert first_task.completed is False,(
        "统计函数不应修改第一个任务的完成状态"

    )

    assert second_task.completed is True, (
        "统计函数不应修改第二个任务的完成状态"

    )


def run_all_tests():
    tests = [
        test_statistics_does_not_modify_tasks,
        test_statistics_result_is_snapshot,
        test_mixed_task_statistics,
        test_one_completed_task_statistics,
        test_one_uncompleted_task_statistics,
        test_empty_task_statistics
    ]

    for test_function in tests:
        test_function()
        print(f"{test_function.__name__} 通过")




if __name__ == "__main__" :
    run_all_tests()



    print("统计测试通过")
