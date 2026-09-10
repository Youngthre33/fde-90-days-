import{
    TICKET_STATUS,
    TICKET_ACTION,
    TICKETS_API_URL
} from "./constants.js";




import {
    tickets,
    setTickets
} from "./data.js";


import {
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

    async function(){


        addButton.disabled =
    true;


    try{

        const title =
            ticketInput.value;


        const ticketToCreate = {
            title: title,
            status: TICKET_STATUS.OPEN
        };


        const response =
            await fetch(
                TICKETS_API_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            ticketToCreate
                    
                        )
                }
            );

          


    if(!response.ok){

        throw new Error(
            `HTTP状态码:${response.status}`
        );
    }

    const  createdTicket =
        await response.json();


        



    const  newTickets = [
        ...tickets,
        createdTicket
    ];

    setTickets(newTickets);

    render(tickets,
            editingId
    );

    ticketInput.value = "";

    }
    
    catch(error){
        console.error(
            "创建工单失败:",
            error.name,
            error.message
        );
    

    
    }finally{
        addButton.disabled =
            false;
    }
        

    }
);


ticketList.addEventListener(
    "click",

    async function(event){

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

                const saveButton =
                    event.target;

                saveButton.disabled =
                    true;

                try{

                    const editInput =
                        document.querySelector(
                            `input[data-id="${id}"]`
                        );

                    const newTitle =
                        editInput.value;

                    const response =
                        await fetch(
                            `${TICKETS_API_URL}/${id}`,
                            {
                                method: "PATCH",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify({
                                        title: newTitle
                                    })
                            }
                        );

                    if(!response.ok){

                        throw new Error(
                            `修改工单失败,HTTP状态码:${response.status}`
                        );
                    }

                    const updatedTicket =
                        await response.json();

                    const newTickets =
                        editTicket(
                            tickets,
                            id,
                            updatedTicket.title
                        );

                    setTickets(newTickets);

                    editingId = null;

                    render(
                        tickets,
                        editingId
                    );

                }catch(error){

                    console.error(
                        "修改工单失败:",
                        error.name,
                        error.message
                    );

                }finally{

                    saveButton.disabled =
                        false;
                }
            }


            if(action === TICKET_ACTION.CANCEL){

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


