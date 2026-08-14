function createTaskMessage(name, status="未开始") {
    const message=  `任务：${name} - 状态:${status}`;
    return message;
}

 const task1 = createTaskMessage("学习js");
 const task2 = createTaskMessage("写项目","进行中");



console.log(task1);
console.log(task2);
