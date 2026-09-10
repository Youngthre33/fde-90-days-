import{
    TICKET_STATUS
}from "./constants.js";









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


function getNextTicketStatus(
    currentStatus
){

    if(

        currentStatus ===
        TICKET_STATUS.OPEN
    ){

        return TICKET_STATUS.IN_PROGRESS;
    }

    if(

        currentStatus ===
        TICKET_STATUS.IN_PROGRESS
    ){
        return TICKET_STATUS.DONE;

    }

    if(
        currentStatus ===
        TICKET_STATUS.DONE
    ){


        return TICKET_STATUS.OPEN;
    }

    throw new Error(
        `非法工单状态: ${currentStatus}`
    );

}

function replaceTicket(

    tickets,
    updatedTicket
){

    return tickets.map(
        function(ticket){


            
            if(
                ticket.id ===
                updatedTicket.id
            ){
                return updatedTicket;
            }

            return ticket;


        }
    );
}


export {



    deleteTicket,

    editTicket,
    getNextTicketStatus,
    replaceTicket

};
