const ticketList =
    document.querySelector("#ticket-list");

const countText =
    document.querySelector("#ticket-count");


function renderTicketCount(tickets){

    countText.textContent =
        `当前有${tickets.length}个工单`;
}


function renderTicketList(
    tickets,
    editingId
){

    ticketList.textContent = "";




    for(const ticket of tickets){

        const item =
            document.createElement("li");


        const editButton =
            document.createElement("button");


        const deleteButton =
            document.createElement("button");


        const statusButton =
            document.createElement("button");



        if(ticket.id === editingId){

            const editInput =
                document.createElement("input");

            const cancelButton =
                document.createElement("button");

            



            editInput.value =
                ticket.title;


            editInput.dataset.id =
                ticket.id;


            item.append(editInput);


            editButton.textContent =
                "保存";


            editButton.dataset.action =
                "save";


            cancelButton.textContent =
                "取消";

            cancelButton.dataset.id = 
                ticket.id;

            cancelButton.dataset.action = 
                "cancel";

            item.append(
                cancelButton
            );



        }else{

            const titleText =
                document.createElement("span");


            titleText.textContent =
                `${ticket.title} - ${ticket.status}`;


            item.append(titleText);


            editButton.textContent =
                "编辑";


            editButton.dataset.action =
                "edit";
        }


        editButton.dataset.id =
            ticket.id;


        deleteButton.textContent =
            "删除";


        deleteButton.dataset.id =
            ticket.id;


        deleteButton.dataset.action =
            "delete";

        
        statusButton.textContent =
            ticket.status === "open"
                ?"完成"
                :"重新打开";

        statusButton.dataset.id =
            ticket.id;


        statusButton.dataset.action =
            "toggle-status";

        statusButton.disabled =
            ticket.id === editingId;


        item.append(
            editButton,
            statusButton,
            deleteButton
        );


        ticketList.append(item);
    }
}


function render(
    tickets,
    editingId
){

    renderTicketCount(tickets);


    renderTicketList(
        tickets,
        editingId
    );
}


export {
    render
};