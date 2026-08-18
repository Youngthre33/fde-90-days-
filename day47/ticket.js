export function getOpenTickets(ticketList){
    return ticketList.filter(ticket=>{
        return ticket.status === "open";
    });
}

export function closeTicket(ticketList,targetId){
    return ticketList.map(ticket =>{
        if(ticket.id === targetId){
            return {
                ...ticket,
                status:"done"
            };
        }

        return ticket;
    });
    
}