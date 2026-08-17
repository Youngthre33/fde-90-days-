const tasks = [
    {
        name: "学习 js",
        completed: false
    },
    {
        name:"写项目",
        completed:true
    }
];

const jsonText= JSON.stringify(tasks);

const loadedTasks = JSON.parse(jsonText);

loadedTasks[0].completed = true ;

console.log(typeof tasks);

console.log(typeof jsonText);

console.log(typeof loadedTasks);


console.log(tasks[0].completed);
console.log(loadedTasks[0].completed);

console.log(tasks === loadedTasks);

console.log(tasks[0] === loadedTasks[0]);



function loadTasks(jsonText) {
    try {
        const tasks = JSON.parse(jsonText);

        if (Array.isArray(tasks)) {
            return tasks;
        }

        return [];
    } catch (error) {
        return [];
    }
}

const a = loadTasks('[{"name":"A"},{"name":"B"}]');
const b = loadTasks('{"name":"A"}');
const c = loadTasks("wrong");

console.log(a);
console.log(b);
console.log(c);

console.log(Array.isArray(a));
console.log(Array.isArray(b));
console.log(Array.isArray(c));