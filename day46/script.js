const tickets = [
    {
        id: 1,
        title: "登录失败",
        status: "open",
        hours: 2
    },
    {
        id: 2,
        title: "无法付款",
        status: "open",
        hours: 5
    },
    {
        id: 3,
        title: "修改发票",
        status: "done",
        hours: 3
    }
];

function getOpenTickets(ticketList) {
    return ticketList.filter(ticket => {
        return ticket.status === "open";
    });
}

function getTotalHours(ticketList) {
    return ticketList.reduce((total, ticket) => {
        return total + ticket.hours;
    }, 0);
}

function getOpenTicketHours(ticketList) {
    const openTickets = getOpenTickets(ticketList);

    return getTotalHours(openTickets);
}

function closeTicket(ticketList, targetId) {
    return ticketList.map(ticket => {
        if (ticket.id === targetId) {
            return {
                ...ticket,
                status: "done"
            };
        }

        return ticket;
    });
}

const beforeHours = getOpenTicketHours(tickets);

const updatedTickets = closeTicket(tickets, 2);

const afterHours = getOpenTicketHours(updatedTickets);

console.log(beforeHours);
console.log(afterHours);

console.log(tickets[1].status);
console.log(updatedTickets[1].status);

console.log(tickets === updatedTickets);
console.log(tickets[0] === updatedTickets[0]);
console.log(tickets[1] === updatedTickets[1]);