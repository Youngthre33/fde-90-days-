// ============================================================
// 模块职责：把工单数据和页面状态渲染成 DOM
// ============================================================

// ---------- 模块依赖 ----------

import {
    TICKET_STATUS,
    TICKET_ACTION
} from "./constants.js";


// ---------- DOM 引用 ----------

const ticketList =
    document.querySelector("#ticket-list");

const countText =
    document.querySelector("#ticket-count");

// 统计卡片来自同一份工单数据；没有加载成功时使用“—”。
const statTotal = document.querySelector("#stat-total");
const statOpen = document.querySelector("#stat-open");
const statProgress = document.querySelector("#stat-progress");
const statDone = document.querySelector("#stat-done");


// ---------- 工单数量 ----------

function renderTicketCount(tickets) {
    countText.textContent =
        `当前有${tickets.length}个工单`;

    renderTicketStats(tickets);
}

function renderTicketStats(tickets = null) {
    // null 表示工单数据尚未取得；空数组才表示确实没有工单。
    const values = tickets === null ? ["—", "—", "—", "—"] : [
        tickets.length,
        tickets.filter(ticket => ticket.status === TICKET_STATUS.OPEN).length,
        tickets.filter(ticket => ticket.status === TICKET_STATUS.IN_PROGRESS).length,
        tickets.filter(ticket => ticket.status === TICKET_STATUS.DONE).length
    ];

    const elements = [statTotal, statOpen, statProgress, statDone];
    for (let index = 0; index < elements.length; index += 1) {
        // 可选统计卡片不影响原来的工单列表入口。
        if (elements[index]) {
            elements[index].textContent = values[index];
        }
    }
}

// 空列表、加载和失败都显示提示，让列表区域有清楚的状态。
function renderListState(title, description) {
    const item = document.createElement("li");
    item.className = "list-state";

    const titleText = document.createElement("p");
    titleText.className = "list-state__title";
    titleText.textContent = title;

    const descriptionText = document.createElement("p");
    descriptionText.className = "list-state__description";
    descriptionText.textContent = description;

    item.append(titleText, descriptionText);
    ticketList.replaceChildren(item);
}


// ---------- 工单列表 ----------

function renderTicketList(
    tickets,
    editingId
) {
    ticketList.textContent = "";

    if (tickets.length === 0) {
        renderListState("暂无工单", "在上方填写工单标题，添加第一张工单。");
        return;
    }

    for (const ticket of tickets) {
        const item =
            document.createElement("li");
        item.className = "ticket-card";

        const heading = document.createElement("div");
        heading.className = "ticket-card__heading";

        const idText = document.createElement("span");
        idText.className = "ticket-id";
        idText.textContent = `#${ticket.id}`;

        const statusBadge = document.createElement("span");
        statusBadge.className = "status-badge";

        const actions = document.createElement("div");
        actions.className = "ticket-actions";

        const editButton =
            document.createElement("button");
        editButton.type = "button";

        const deleteButton =
            document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "button button--danger";

        const statusButton =
            document.createElement("button");
        statusButton.type = "button";
        statusButton.className = "button button--status";

        let statusText;
        let statusButtonText;
        let statusValue = "unknown";

        if (
            ticket.status === TICKET_STATUS.OPEN
        ) {
            statusText = "待处理";
            statusButtonText = "开始处理";
            statusValue = TICKET_STATUS.OPEN;
        } else if (
            ticket.status === TICKET_STATUS.IN_PROGRESS
        ) {
            statusText = "处理中";
            statusButtonText = "完成";
            statusValue = TICKET_STATUS.IN_PROGRESS;
        } else if (
            ticket.status === TICKET_STATUS.DONE
        ) {
            statusText = "已完成";
            statusButtonText = "重新打开";
            statusValue = TICKET_STATUS.DONE;
        } else {
            statusText = "状态异常";
            statusButtonText = "不可操作";
        }

        statusBadge.textContent = statusText;
        statusBadge.dataset.status = statusValue;
        heading.append(idText, statusBadge);
        item.append(heading);

        const titleText = document.createElement("h3");
        titleText.className = "ticket-title";
        // 工单标题始终按文字显示，避免用户输入被当成 HTML 执行。
        titleText.textContent = ticket.title;
        item.append(titleText);

        if (ticket.id === editingId) {
            const editInput =
                document.createElement("input");

            const cancelButton =
                document.createElement("button");
            cancelButton.type = "button";
            cancelButton.className = "button button--quiet";

            editInput.className = "edit-ticket-input";
            editInput.setAttribute("aria-label", "编辑工单标题");
            editInput.value = ticket.title;
            editInput.dataset.id = ticket.id;
            item.append(editInput);

            editButton.textContent = "保存";
            editButton.className = "button button--primary";
            editButton.dataset.action =
                TICKET_ACTION.SAVE;

            cancelButton.textContent = "取消";
            cancelButton.dataset.id = ticket.id;
            cancelButton.dataset.action =
                TICKET_ACTION.CANCEL;

            actions.append(cancelButton);
        } else {
            editButton.textContent = "编辑";
            editButton.className = "button button--quiet button--edit";
            editButton.dataset.action =
                TICKET_ACTION.EDIT;
        }

        editButton.dataset.id = ticket.id;

        deleteButton.textContent = "删除";
        deleteButton.dataset.id = ticket.id;
        deleteButton.dataset.action =
            TICKET_ACTION.DELETE;

        statusButton.textContent =
            statusButtonText;
        statusButton.dataset.id = ticket.id;
        statusButton.dataset.action =
            TICKET_ACTION.TOGGLE_STATUS;

        statusButton.disabled =
            ticket.id === editingId;

        if (
            ticket.status !== TICKET_STATUS.OPEN &&
            ticket.status !== TICKET_STATUS.IN_PROGRESS &&
            ticket.status !== TICKET_STATUS.DONE
        ) {
            statusButton.disabled = true;
        }


        const adviceButton = document.createElement("button");

        adviceButton.type = "button";
        adviceButton.className = "button button--ai";
        adviceButton.textContent = "生成建议";
        adviceButton.dataset.id = ticket.id;
        adviceButton.dataset.action = TICKET_ACTION.GENERATE_ADVICE;
        adviceButton.disabled = ticket.id === editingId;


        // 按钮直接保存文字，保留 main.js 对 BUTTON 点击目标的判断。
        actions.append(
            editButton,
            statusButton,
            deleteButton,
            adviceButton
        );
        item.append(actions);

        ticketList.append(item);
    }
}


// ---------- 加载和错误状态 ----------

function renderLoading() {
    countText.textContent =
        "正在加载工单...";

    renderTicketStats();
    renderListState("正在加载工单", "正在获取最新工单，请稍候。");
}

function renderLoadError() {
    countText.textContent =
        "工单加载失败，请稍后重试";

    renderTicketStats();
    renderListState("暂时无法加载工单", "请检查访问凭据和后端服务，然后点击“重新加载”。");
}


// ---------- 页面总渲染入口 ----------

function render(
    tickets,
    editingId
) {
    renderTicketCount(tickets);

    renderTicketList(
        tickets,
        editingId
    );
}


// ---------- 模块导出 ----------

export {
    render,
    renderLoadError,
    renderLoading
};
