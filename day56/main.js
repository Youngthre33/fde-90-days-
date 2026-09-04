import {
    tickets,
    setTickets
} from "./data.js";


import {
    addTicket,
    deleteTicket,
    editTicket,
    toggleTicketStatus
} from "./ticket.js";


import {
    render
} from "./render.js";


let editingId = null;


const ticketInput =
    document.querySelector("#ticket-input");


const addButton =
    document.querySelector("#add-button");


const ticketList =
    document.querySelector("#ticket-list");


addButton.addEventListener(
    "click",

    function(){

        const title =
            ticketInput.value;


        const newTickets =
            addTicket(
                tickets,
                title
            );


        setTickets(newTickets);


        render(
            tickets,
            editingId
        );


        ticketInput.value = "";
    }
);


ticketList.addEventListener(
    "click",

    function(event){

        if(event.target.tagName === "BUTTON"){

            const action =
                event.target.dataset.action;


            const id =
                Number(
                    event.target.dataset.id
                );


            if(action === "edit"){

                editingId = id;


                render(
                    tickets,
                    editingId
                );
            }


            if(action === "delete"){

                const newTickets =
                    deleteTicket(
                        tickets,
                        id
                    );


                setTickets(newTickets);


                if(editingId === id){
                    editingId = null;
                }


                render(
                    tickets,
                    editingId
                );
            }


            if(action === "save"){

                const editInput =
                    document.querySelector(
                        `input[data-id="${id}"]`
                    );


                const newTitle =
                    editInput.value;


                const newTickets =
                    editTicket(
                        tickets,
                        id,
                        newTitle
                    );


                setTickets(newTickets);


                editingId = null;


                render(
                    tickets,
                    editingId
                );
            }

if(action === "toggle-status"){

    try{

        const newTickets =
            toggleTicketStatus(
                tickets,
                id
            );


        setTickets(newTickets);


        render(
            tickets,
            editingId
        );

    }catch(error){

        console.error(
            error.message
        );
    }
}


         
        }
    }
);