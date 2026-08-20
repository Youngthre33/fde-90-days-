let tickets = [
    {
        id:1,
        title:"登录失败",
        status:"open"
    },

    {
        id:2,
        title:"修改发票",
        status:"done"
    }
];

function setTickets(newTickets){
    tickets = newTickets;
}



export { tickets,
    setTickets
 };