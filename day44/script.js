const users = [
    {
        name:"小王",
        profile:{
            age: 28,
            city:"上海"
        }
    },


    {
        name:"小李",
        profile: null
    },
    {
        name: "小张"
    }
];

function showUser(user){
    const name = user.name ?? "匿名用户";
    const age = user.profile?.age?? "未知年龄";
    const city = user.profile?.city?? "未知城市";
    console.log(name);
    console.log(age);
    console.log(city);
}


users.forEach(showUser);