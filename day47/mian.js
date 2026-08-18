import{
    closeTicket
} from "./ticket.js";

import{
    getOpenTicketHours
} from"./statistics.js";

const tickets  = [
    {
        id : 1,
        title : "登录失败",
        status : "open",
        hours: 2
    },
    {
        id : 2,
        title : "修改发票",
        status : "done",
        hours : 4
    },

    {
        id : 3,
        title : "无法付款",
        status: "open",

        hours : 6
    }
];

const beforeHours =  getOpenTicketHours(tickets);

const updatedTickets = closeTicket(tickets,1);

const afterHours =  getOpenTicketHours(updatedTickets);

console.log(beforeHours);
console.log(afterHours);