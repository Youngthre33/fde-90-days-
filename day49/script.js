let tickets = [
    {
        id:1,
        title: "登录失败",
        status: "open"
    },

    {
        id :2,
        title:"修改发票",
        status:"done"
    }

   
];





const countText = 
    document.querySelector("#ticket-count");

const ticketList = 
    document.querySelector("#ticket-list");







function renderTicketCount(ticketData){

countText.textContent = `当前有${tickets.length}个工单`;
}



function renderTicketList(ticketData){
    ticketList.textContent = " ";

    for(const ticket of ticketData){
        const item = 
        document.createElement("li");
        const title =
        document.createElement("span");
        const status =
        document.createElement("span");
    
        title.textContent = ticket.title;

        status.textContent = 
        ` - ${ticket.status}`;

        item.append(title);
        item.append(status);

        ticketList.append(item);
    
    }
}


function render(ticketData){
    renderTicketCount(ticketData);
    renderTicketList(ticketData);
}


render(tickets);


tickets = [
    ...tickets,
    {
        id: 3,
        title: "无法付款",
        status:"open"
    }
];

render(tickets);







