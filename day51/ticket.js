function addTicket(tickets, title){

    const newTicket = {

        id:tickets.length + 1,

        title:title,

        status:"open"

    };


    return [
        ...tickets,
        newTicket
    ];

}




function deleteTicket(tickets,id){



    return tickets.filter(
        function(ticket){
            return ticket.id !== id;
        }
    );
}


export { addTicket,
    deleteTicket
 };
