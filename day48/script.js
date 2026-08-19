function addTicket(ticketList, id, title){
    const newTicket = {
        id : id,
        title : title,
        status : "open"

    };

    return [
        ...ticketList,
        newTicket
    ];


}

function updateTicketStatus(ticketList, targetID, newStatus){
    return ticketList.map(ticket =>{
        if(ticket.id === targetID) {
            return{
                ...ticket,
                status:newStatus
            };
        }
        return ticket;
    });
}

function deleteTicket(ticketList,targetID){
    return ticketList.filter(ticket =>{
        return ticket.id !== targetID;
    });
}



let tickets = [
    {
        id: 1,
        titel : "登录失败",
        status: "open"
    },
    {
        id: 2,
        title: "修改发票",
        status:"open"
    }
];

tickets = addTicket(
    tickets,
    3,
    "无法付款"
);

tickets = updateTicketStatus(
    tickets,
    2,
    "done"
);

tickets = deleteTicket(
    tickets,
    1
);


console.log(tickets);
console.log(tickets.length);
console.log(tickets[0].id);
console.log(tickets[0].status);
console.log(tickets[1].id);
console.log(tickets[1].status);