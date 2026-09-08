import{
    TICKET_STATUS
}from "./constants.js";





function addTicket(tickets,title){

    const newTicket = {

        id: Date.now(),

        title:title,

        status:TICKET_STATUS.OPEN

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



function editTicket(tickets,id,newTitle){


    return tickets.map(

        function(ticket){


            if(ticket.id === id){


                return {

                    ...ticket,

                    title:newTitle

                };


            }


            return ticket;


        }

    );


}

function toggleTicketStatus(tickets, id){

    return tickets.map(
        function(ticket){

            if(ticket.id === id){

                let newStatus;


if(
    ticket.status === TICKET_STATUS.OPEN
){

    newStatus =
        TICKET_STATUS.IN_PROGRESS;

}else if(
    ticket.status === TICKET_STATUS.IN_PROGRESS
){

    newStatus =
        TICKET_STATUS.DONE;

}else if(
    ticket.status === TICKET_STATUS.DONE
){

    newStatus =
        TICKET_STATUS.OPEN;

}else{

    throw new Error(
        `非法工单状态: ${ticket.status}`
    );
}




                return {
                    ...ticket,
                    status: newStatus
                };
            }


            return ticket;
        }
    );
}



export {

    addTicket,

    deleteTicket,

    editTicket,
    toggleTicketStatus

};