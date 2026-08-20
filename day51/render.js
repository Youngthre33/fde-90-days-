const ticketList =
    document.querySelector("#ticket-list");


const countText =
    document.querySelector("#ticket-count");



function renderTicketCount(tickets){

    countText.textContent =
        `当前有${tickets.length}个工单`;

}



function renderTicketList(tickets){

    ticketList.textContent = "";


    for(const ticket of tickets){


        const item =
            document.createElement("li");

        const deleteButton =
            document.createElement("button");

        


        item.textContent =
            `${ticket.title} - ${ticket.status}`;

        deleteButton.textContent = 
        "删除";

        deleteButton.dataset.id = 
        ticket.id;

        item.append(deleteButton);


        ticketList.append(item);

    }

}



function render(tickets){

    renderTicketCount(tickets);

    renderTicketList(tickets);

}



export { render };