const TICKET_STATUS = {
    OPEN: "open",
    IN_PROGRESS: "in_progress",
    DONE: "done"
};


const TICKET_ACTION = {
    EDIT: "edit",
    DELETE: "delete",
    SAVE: "save",
    CANCEL: "cancel",
    TOGGLE_STATUS: "toggle-status"
};

const TICKETS_API_URL =
    "http://127.0.01:3000/tickets";



export {
    TICKET_STATUS,
    TICKET_ACTION,
    TICKETS_API_URL
};