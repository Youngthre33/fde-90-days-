const tasks = ["学习 js", "写项目" ];
tasks.push("吃饭");

const copy = tasks.slice();

copy[0] = "复习js";

const hasProject = tasks.includes("写项目");

for (let i = 0; i < tasks.length; i++){
    console.log(`${i + 1}. ${tasks[i]}`);
    

}

console.log(copy);
console.log(hasProject);