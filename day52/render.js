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



        const editButton =
        document.createElement("button");



        const deleteButton =
        document.createElement("button");



        item.textContent =
        `${ticket.title} - ${ticket.status}`;



        editButton.textContent =
        "编辑";



        editButton.dataset.id =
        ticket.id;


        editButton.dataset.action =
        "edit";



        deleteButton.textContent =
        "删除";



        deleteButton.dataset.id =
        ticket.id;


        deleteButton.dataset.action =
        "delete";



        item.append(
            editButton,
            deleteButton
        );


        ticketList.append(item);


    }


}




function render(tickets){

    renderTicketCount(tickets);

    renderTicketList(tickets);

}



export {

    render

};