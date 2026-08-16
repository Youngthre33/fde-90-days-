const task = {
    name: "学习js",
    completed: false,
    hours: 2,
    priority: "high"
};

const{
    name:taskName,
    completed,
    hours,
    priority = "normal"
} = task;

console.log(taskName);
console.log(completed);
console.log(hours);
console.log(priority);

const values = [10,20,30,40];

const [first, second, ...others] = values;

console.log(first);
console.log(second);
console.log(others);

function showTask({ name, completed}){
    console.log(name);
    console.log(completed);
}

showTask(task);

