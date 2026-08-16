const tasks = [
    {name:"学习js", completed:false},
    {name:"写项目",completed: true},
    {name:"复习数组",completed: true },
    {name:"吃饭",completed:false}

];

const firstCompleted = tasks.find(
    task => task.completed === true
);

const firstCompletedIndex = tasks.findIndex(
    task => task.completed === true 
);

const hasIncomplete = tasks.some(
    task => task.completed === false  
);

const allCompleted = tasks.every(
    task => task.completed === true
);

const completedTasks = tasks.filter(
    task => task.completed === true
);

const taskNames = tasks.map(
    task=> task.name
);


tasks.forEach(task=>{
    console.log(`任务:${task.name}`);
});

const completedcount = tasks.reduce(
    (count,task) =>{
        if (task.completed){
            return count +1;
        }
        return count;
    },
    0

);

console.log(completedcount);



console.log(completedTasks);
console.log(taskNames);




console.log(firstCompleted);
console.log(firstCompletedIndex);
console.log(hasIncomplete);
console.log(allCompleted);
