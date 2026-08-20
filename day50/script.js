let tickets = [
    {
        id: 1,
        title: "登录失败",
        status: "open"
    },

    {
        id: 2,
        title: "修改发票",
        status: "done"
    }
];


// 获取页面元素

const ticketInput =
    document.querySelector("#ticket-input");


const addButton =
    document.querySelector("#add-button");


const ticketList =
    document.querySelector("#ticket-list");


const countText =
    document.querySelector("#ticket-count");


// 显示数量

function renderTicketCount(){

    countText.textContent =
        `当前有${tickets.length}个工单`;

}


// 显示列表

function renderTicketList(){

    // 清空旧页面

    ticketList.textContent = "";


    // 根据最新 tickets 创建页面

    for(const ticket of tickets){


        const item =
            document.createElement("li");


        const deleteButton =
            document.createElement("button");


        item.textContent =
            `${ticket.title} - ${ticket.status}`;


        deleteButton.textContent =
            "删除";


        // 保存当前工单id

        deleteButton.dataset.id =
            ticket.id;


        // 给当前按钮绑定点击事件

        deleteButton.addEventListener(
            "click",
            function(event){


                const id =
                    Number(event.target.dataset.id);



                tickets =
                    tickets.filter(
                        function(ticket){


                            return ticket.id !== id;


                        }
                    );



                render();


            }
        );



        item.append(deleteButton);


        ticketList.append(item);


    }

}



// 总渲染

function render(){

    renderTicketCount();

    renderTicketList();

}



// 添加工单

addButton.addEventListener(
    "click",
    function(){


        const title =
            ticketInput.value;



        const newTicket = {

            id: tickets.length + 1,

            title: title,

            status: "open"

        };



        tickets = [

            ...tickets,

            newTicket

        ];



        render();


        ticketInput.value = "";


    }
);



// 页面第一次打开

render();