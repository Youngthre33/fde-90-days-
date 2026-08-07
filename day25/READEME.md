# Python 任务管理器

这是我在学习python 过程中完成的一个命令行任务管理器项目.
这个项目用于练习Python 基础语法, 函数, 类与对象, 模块拆分, JSON 文件存储, 异常处理, 自动化测试以及代码重构.

## 功能

- 查看任务
- 添加任务
- 完成任务
- 修改任务名称
- 删除任务
- 搜索任务
- 筛选已完成和未完成任务
- 按优先级排序
- 修改任务优先级
- 查看任务统计
- 自动保存和读取任务数据


## 运行方法

确保电脑已经安装 Python,

在项目目录中运行:

```bash
python main.py
```

## 项目结构

```text
day25/
├── main.py
├── task.py
├── storage.py
├── task_statistics.py
├── task.json
├── test_storage.py
└── test_task_statistics.py
```
- `main.py`：负责用户交互、菜单和程序总体调度
- `task.py`：定义 Task 类以及任务自身行为
- `storage.py`：负责 JSON 数据保存、读取和验证
- `task_statistics.py`：负责任务统计计算
- `test_storage.py`：测试存储数据验证逻辑
- `test_task_statistics.py`：测试任务统计逻辑
- `task.json`：保存任务数据

## 测试

运行存储测试：

```bash
python test_storage.py
```

运行统计测试：

```bash
python test_task_statistics.py
```