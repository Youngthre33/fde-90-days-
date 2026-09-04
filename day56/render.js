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






        let statusText;
        let statusButtonText;


if(ticket.status === "open"){

    statusText =
        "待处理";

    statusButtonText =
        "开始处理";

}else if(
    ticket.status === "in_progress"
){

    statusText =
        "处理中";

    statusButtonText =
        "完成";

}else if(
    ticket.status === "done"
){

    statusText =
        "已完成";

    statusButtonText =
        "重新打开";

}else{

    statusText =
        "状态异常";

    statusButtonText =
        "不可操作";
}




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
                `${ticket.title} - ${statusText}`;


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
            statusButtonText;

            

        statusButton.dataset.id =
            ticket.id;


        statusButton.dataset.action =
            "toggle-status";



        statusButton.disabled =
            ticket.id === editingId;

            if(
                ticket.status !== "open"&&
                ticket.status !== "in_progress"&&
                ticket.status !== "done"
            ){

                statusButton.disabled =
                    true;
            }



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