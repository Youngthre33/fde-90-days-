function addTicket(tickets,title){

    const newTicket = {

        id: Date.now(),

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


function toggleTicketStatus(tickets,id){
    return tickets.map(
        function(ticket){
            
            if(ticket.id === id){
                const newStatus =
                    ticket.status === "open"
                    ?"done"
                    :"open";

                return{
                    ...ticket,
                    status:newStatus
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