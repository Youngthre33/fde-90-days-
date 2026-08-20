import { tickets,setTickets } from "./data.js";

import { render } from "./render.js";

import { addTicket,
    deleteTicket
 } from "./ticket.js";


render(tickets);



const ticketInput =
    document.querySelector("#ticket-input");


const addButton =
    document.querySelector("#add-button");


const ticketList =
document.querySelector("#ticket-lsit");


ticketList.addEventListener(
    "click",
    function(event){
        if(event.target.tagName === "BUTTON"){


            const id = 
                Number(event.target.dataset.id);


            const newTickets =
            deleteTicket(
                tickets,
                id
            );
            setTickets(newTickets);

            render(tickets);
        }
    }
);



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

        render(tickets);


        ticketInput.value = "";


    }
);