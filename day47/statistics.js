import { getOpenTickets } from "./ticket.js";

export function getTotalHours(ticketList) {
    return ticketList.reduce((total,ticket) =>{
        return total +ticket.hours;
    },0);
}


export function getOpenTicketHours(ticketList){
    const openTickets = getOpenTickets(ticketList);

    return getTotalHours(openTickets);
}

