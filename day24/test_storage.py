import storage


def test_valid_task_data():
    data = {
        "name":"学习python",
        "completed":False,
        "priority":"高"
    }

    result = storage.get_task_data_error(data)
  
    assert result is None



def test_missing_required_field():
    data = {
        "name":"学习python"
    }
    result = storage.get_task_data_error(data)

    assert result == "任务数据缺少必要的字段",(
        f"预期返回缺少字段错误,实际返回:{result!r}"
    )

def test_invalid_name_type():
    data = {
        "name": 123,
        "completed": False,
        "priority": "高"
    }

    result = storage.get_task_data_error(data)


    assert result == "任务名称必须是非空字符串",(
        f"预期返回任务名称错误,实际返回:{result!r}"
        )


def test_invalid_completed_type():
    data = {
        "name":"学习python",
        "completed": "False",
        "priority": "高"
    }

    result = storage.get_task_data_error(data)


    assert result == "任务完成状态必须是布尔值",(
    f"预期返回完成状态错误,实际返回:{result!r}"
)

def test_invalid_priority():
    data = {
        "name":"学习python",
        "completed": False,
        "priority" : "紧急"

    }
    result = storage.get_task_data_error(data)

    assert result == "任务优先级无效",(
        f"预期返回优先级错误,实际返回:{result!r}"
    )

def test_empty_task_name():
    data = {
        "name":" ",
        "completed": False,
        "priority":"高"
    }
    result = storage.get_task_data_error(data)

    assert result == "任务名称必须是非空字符串",(
        f"预期返回空任务名称错误, 实际返回:{result!r}"
    )

def test_non_dict_task_data():
    data = "错误数据"

    result = storage.get_task_data_error(data)

    assert result =="任务列表中存在不是字典的数据",(
        f"预期返回非字典数据错误,实际返回:{result!r}"

    )

def test_missing_optional_priority():
    data = {
        "name": "学习python",
        "completed": False,

    }

    result = storage.get_task_data_error(data)

    assert result is None,(
        f"缺少可选的priority时本应通过,实际返回:{result!r}"

    )

def test_validation_does_not_modify_data():
    data = {
        "name": "学习python",
        "completed":False
    }

    result = storage.get_task_data_error(data)


    assert result is None,(
        f"这份数据本应验证通过,实际返回:{result!r}"

    )
    assert "priority" not in data,(
        f"验证函数不应修改原字典,实际数据:{data!r}"
    )

if __name__ == "__main__":

    test_valid_task_data()
    test_missing_required_field()
    test_invalid_name_type()
    test_invalid_priority()
    test_invalid_completed_type()
    test_empty_task_name()
    test_non_dict_task_data()
    test_missing_optional_priority()
    test_validation_does_not_modify_data()

    print("测试通过")