// ============================================================
// 模块职责：提供不直接修改原数组的工单数据转换函数
// ============================================================

// ---------- 模块依赖 ----------

import {
    TICKET_STATUS
} from "./constants.js";


// ---------- 删除工单 ----------

function deleteTicket(tickets, id) {
    return tickets.filter(
        function (ticket) {
            return ticket.id !== id;
        }
    );
}


// ---------- 修改工单标题 ----------

function editTicket(
    tickets,
    id,
    newTitle
) {
    return tickets.map(
        function (ticket) {
            if (ticket.id === id) {
                return {
                    ...ticket,
                    title: newTitle
                };
            }

            return ticket;
        }
    );
}


// ---------- 计算下一工单状态 ----------

function getNextTicketStatus(currentStatus) {
    if (currentStatus === TICKET_STATUS.OPEN) {
        return TICKET_STATUS.IN_PROGRESS;
    }

    if (
        currentStatus ===
        TICKET_STATUS.IN_PROGRESS
    ) {
        return TICKET_STATUS.DONE;
    }

    if (currentStatus === TICKET_STATUS.DONE) {
        return TICKET_STATUS.OPEN;
    }

    throw new Error(
        `非法工单状态: ${currentStatus}`
    );
}


// ---------- 用服务器返回对象替换目标工单 ----------

function replaceTicket(
    tickets,
    updatedTicket
) {
    return tickets.map(
        function (ticket) {
            if (ticket.id === updatedTicket.id) {
                return updatedTicket;
            }

            return ticket;
        }
    );
}


// ---------- 模块导出 ----------

export {
    deleteTicket,
    editTicket,
    getNextTicketStatus,
    replaceTicket
};
