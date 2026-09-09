import{
    TICKET_ACTION,
    TICKETS_API_URL
} from "./constants.js";




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
    render,
    renderLoadError,
    renderLoading
} from "./render.js";


let editingId = null;


const ticketInput =
    document.querySelector("#ticket-input");


const addButton =
    document.querySelector("#add-button");


const ticketList =
    document.querySelector("#ticket-list");

const reloadButton =
    document.querySelector("#reload-button");



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


            if(action === TICKET_ACTION.EDIT){

                editingId = id;


                render(
                    tickets,
                    editingId
                );
            }


            if(action === TICKET_ACTION.DELETE){

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


            if(action === TICKET_ACTION.SAVE){

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

if(action === TICKET_ACTION.TOGGLE_STATUS){

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


async function loadTicketsFromApi(){
    try{


        reloadButton.disabled =
            true;

        renderLoading();

    const response =

        await fetch(TICKETS_API_URL);


    console.log(response);


    if(!response.ok){


        throw new Error(
            `请求失败,HTTP状态码:${response.status}`
        );
    }


    const loadedTickets =
        await response.json();

    console.log(loadedTickets);

    setTickets(loadedTickets);

    render(
        tickets,
        editingId
    );

    console.log("保存后的 tickets: ",tickets);

    return loadedTickets;

    }catch(error){


        console.error(
            "错误名称:",
            error.name
        );

        console.error(
            "捕获到加载错误:",
            error.message
        );





        renderLoadError();
    } finally{
        reloadButton.disabled =
            false;
    }
}
loadTicketsFromApi();




reloadButton.addEventListener(
    "click",

    function(){
        loadTicketsFromApi();
    }
);


