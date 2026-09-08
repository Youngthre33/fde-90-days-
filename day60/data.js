import{
    TICKET_STATUS
} from"./constants.js";



let tickets = [
    {
        id: 1,
        title: "登录失败",
        status: TICKET_STATUS.OPEN
    },
    {
        id: 2,
        title: "修改发票",
        status: TICKET_STATUS.DONE
    }
];



function setTickets(newTickets){

    tickets = newTickets;

}


export {
    tickets,
    setTickets
};