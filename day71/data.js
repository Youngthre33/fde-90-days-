// ============================================================
// 模块职责：保存浏览器当前使用的工单数组
// ============================================================

// ---------- 模块依赖 ----------

import {
    TICKET_STATUS
} from "./constants.js";


// ---------- 浏览器中的工单状态 ----------

// 这是启动前的本地示例数据。
// 页面加载完成后，会被 API 返回的工单数组替换。
let tickets = [
    {
        id: 1,
        title: "登录失败",
        status: TICKET_STATUS.OPEN
    },
    {
        id: 2,
        title: "修改发票",
        status: TICKET_STATUS.DONE
    }
];


// ---------- 更新浏览器工单状态 ----------

function setTickets(newTickets) {
    tickets = newTickets;
}


// ---------- 模块导出 ----------

export {
    tickets,
    setTickets
};
