import {
    tickets,
    setTickets
}
from "./data.js";


import {

    addTicket,

    deleteTicket,

    editTicket

}
from "./ticket.js";



import {
    render
}
from "./render.js";




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



        render(tickets);



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
            Number(event.target.dataset.id);



            if(action === "delete"){



                const newTickets =
                deleteTicket(
                    tickets,
                    id
                );


                setTickets(newTickets);


                render(tickets);



            }



            if(action === "edit"){


                const newTitle =
                prompt(
                    "请输入新的标题"
                );



                const newTickets =
                editTicket(
                    tickets,
                    id,
                    newTitle
                );



                setTickets(newTickets);


                render(tickets);


            }


        }


    }


);





render(tickets);