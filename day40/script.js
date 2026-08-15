const task =[

{
    name:"学习 js",
    completed:false
},
{
    name:"写项目",
    completed:true
},
{
    name:"复习对象",
    completed:false
}
];

function showTask(task){
    if(task.completed){
        return `已完成:${task.name}`;
    }
    return'未完成:${task.name}';

}
for (const task of tasks) {
    console.log(showTask(task));
}