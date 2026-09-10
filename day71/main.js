// ============================================================
// 模块职责：协调用户操作、API 请求、浏览器状态和页面渲染
// ============================================================

// ---------- 模块依赖 ----------

import {
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
    getNextTicketStatus,
    replaceTicket
} from "./ticket.js";

import {
    render,
    renderLoadError,
    renderLoading
} from "./render.js";


// ---------- 页面状态和 DOM 引用 ----------

let editingId = null;

const ticketInput =
    document.querySelector("#ticket-input");

const addButton =
    document.querySelector("#add-button");

const ticketList =
    document.querySelector("#ticket-list");

const reloadButton =
    document.querySelector("#reload-button");


// ---------- 创建工单 ----------

async function handleAddTicket() {
    addButton.disabled = true;

    try {
        const title = ticketInput.value;

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

        if (!response.ok) {
            throw new Error(
                `HTTP状态码:${response.status}`
            );
        }

        const createdTicket =
            await response.json();

        const newTickets = [
            ...tickets,
            createdTicket
        ];

        setTickets(newTickets);

        render(
            newTickets,
            editingId
        );

        ticketInput.value = "";
    } catch (error) {
        console.error(
            "创建工单失败:",
            error.name,
            error.message
        );
    } finally {
        addButton.disabled = false;
    }
}


// ---------- 删除工单 ----------

async function handleDeleteAction(
    id,
    deleteButton
) {
    deleteButton.disabled = true;

    try {
        const response =
            await fetch(
                `${TICKETS_API_URL}/${id}`,
                {
                    method: "DELETE"
                }
            );

        if (!response.ok) {
            throw new Error(
                `删除工单失败,HTTP状态码:${response.status}`
            );
        }

        const newTickets =
            deleteTicket(
                tickets,
                id
            );

        setTickets(newTickets);

        if (editingId === id) {
            editingId = null;
        }

        render(
            newTickets,
            editingId
        );
    } catch (error) {
        console.error(
            "删除工单失败:",
            error.name,
            error.message
        );
    } finally {
        deleteButton.disabled = false;
    }
}


// ---------- 保存工单标题 ----------

async function handleSaveAction(
    id,
    saveButton
) {
    saveButton.disabled = true;

    try {
        const editInput =
            document.querySelector(
                `input[data-id="${id}"]`
            );

        const newTitle = editInput.value;

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

        if (!response.ok) {
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
            newTickets,
            editingId
        );
    } catch (error) {
        console.error(
            "修改工单失败:",
            error.name,
            error.message
        );
    } finally {
        saveButton.disabled = false;
    }
}


// ---------- 切换工单状态 ----------

async function handleToggleStatusAction(
    id,
    statusButton
) {
    statusButton.disabled = true;

    try {
        const currentTicket =
            tickets.find(
                function (ticket) {
                    return ticket.id === id;
                }
            );

        if (!currentTicket) {
            throw new Error(
                `找不到工单,ID:${id}`
            );
        }

        const newStatus =
            getNextTicketStatus(
                currentTicket.status
            );

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
                            status: newStatus
                        })
                }
            );

        if (!response.ok) {
            throw new Error(
                `修改工单状态失败,HTTP状态码:${response.status}`
            );
        }

        const updatedTicket =
            await response.json();

        const newTickets =
            replaceTicket(
                tickets,
                updatedTicket
            );

        setTickets(newTickets);

        render(
            newTickets,
            editingId
        );
    } catch (error) {
        console.error(
            "修改工单状态失败:",
            error.name,
            error.message
        );
    } finally {
        statusButton.disabled = false;
    }
}


// ---------- 列表点击事件分发 ----------

async function handleTicketListClick(event) {
    if (event.target.tagName !== "BUTTON") {
        return;
    }

    const clickedButton = event.target;
    const action = clickedButton.dataset.action;
    const id = Number(clickedButton.dataset.id);

    if (action === TICKET_ACTION.EDIT) {
        editingId = id;

        render(
            tickets,
            editingId
        );

        return;
    }

    if (action === TICKET_ACTION.DELETE) {
        await handleDeleteAction(
            id,
            clickedButton
        );

        return;
    }

    if (action === TICKET_ACTION.SAVE) {
        await handleSaveAction(
            id,
            clickedButton
        );

        return;
    }

    if (action === TICKET_ACTION.CANCEL) {
        editingId = null;

        render(
            tickets,
            editingId
        );

        return;
    }

    if (action === TICKET_ACTION.TOGGLE_STATUS) {
        await handleToggleStatusAction(
            id,
            clickedButton
        );
    }
}


// ---------- 从 API 加载工单 ----------

async function loadTicketsFromApi() {
    try {
        reloadButton.disabled = true;
        renderLoading();

        const response =
            await fetch(TICKETS_API_URL);

        if (!response.ok) {
            throw new Error(
                `请求失败,HTTP状态码:${response.status}`
            );
        }

        const loadedTickets =
            await response.json();

        setTickets(loadedTickets);

        render(
            loadedTickets,
            editingId
        );

        return loadedTickets;
    } catch (error) {
        console.error(
            "工单加载失败:",
            error.name,
            error.message
        );

        renderLoadError();
    } finally {
        reloadButton.disabled = false;
    }
}


// ---------- 事件注册和程序启动 ----------

addButton.addEventListener(
    "click",
    handleAddTicket
);

ticketList.addEventListener(
    "click",
    handleTicketListClick
);

reloadButton.addEventListener(
    "click",
    loadTicketsFromApi
);

loadTicketsFromApi();
