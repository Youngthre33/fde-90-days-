const taskName = "写项目";
const isCompleted = true;

const hasPermission = false;

console.log(`任务: ${taskName}`);

if (hasPermission || !isCompleted){
    console.log("A");

} else {
    console.log("B");

}

console.log("C");