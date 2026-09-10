// ============================================================
// 模块职责：集中保存工单状态、用户动作和 API 地址
// ============================================================

// ---------- 工单状态 ----------

const TICKET_STATUS = {
    OPEN: "open",
    IN_PROGRESS: "in_progress",
    DONE: "done"
};


// ---------- 用户动作 ----------

const TICKET_ACTION = {
    EDIT: "edit",
    DELETE: "delete",
    SAVE: "save",
    CANCEL: "cancel",
    TOGGLE_STATUS: "toggle-status"
};


// ---------- API 地址 ----------

const TICKETS_API_URL =
    "http://127.0.0.1:3000/tickets";


// ---------- 模块导出 ----------

export {
    TICKET_STATUS,
    TICKET_ACTION,
    TICKETS_API_URL
};
