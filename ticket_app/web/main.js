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

// 页面共用的生成标志：true 表示已有一次生成正在处理，其他生成点击先返回。
let generatingAdvice = false;

// 复制只使用最终成功的文字；预览和错误提示不放进这个变量。
let finalAdviceText = "";
let copyingAdvice = false;
// 每开始一次生成就加一，用来识别复制期间是否已经换了一轮建议。
let adviceGeneration = 0;

// 找到网页的访问凭据输入框；请求时读取用户填写的值。
const tokenInput =
    document.querySelector("#token-input");


const ticketInput =
    document.querySelector("#ticket-input");

const addButton =
    document.querySelector("#add-button");

const ticketList =
    document.querySelector("#ticket-list");

const reloadButton =
    document.querySelector("#reload-button");

const actionMessage =
    document.querySelector("#action-message");

// 找到“AI 处理建议”下方的文字区域，预览、完成结果和错误提示都显示在这里。
const adviceOutput =
    document.querySelector("#advice-output");

const copyAdviceButton =
    document.querySelector("#copy-advice-button");

const copyAdviceMessage =
    document.querySelector("#copy-advice-message");

// 新外观沿用原来的功能元素；这几个引用只负责表单与可见状态。
const accessForm = document.querySelector("#access-form");
const createTicketForm = document.querySelector("#create-ticket-form");
const advicePanel = document.querySelector("#advice-panel");
const adviceState = document.querySelector("#advice-state");

function setAdviceViewState(state, text) {
    advicePanel.dataset.state = state;
    adviceState.textContent = text;
}


function getAuthHeaders() {
    // 按后端约定把凭据放进 Authorization 请求头，AI 请求也沿用这一个入口。
    return {
        Authorization: "Bearer " + tokenInput.value.trim()
    };
}


// ---------- 创建工单 ----------


async function handleAddTicket() {
    addButton.disabled = true;
    actionMessage.textContent = "正在添加工单...";

    try {
        const title = ticketInput.value;

        const ticketToCreate = {
            title: title

        };

        const response =
            await fetch(
                TICKETS_API_URL,
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json",
                        ...getAuthHeaders()
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
        actionMessage.textContent = "工单已添加";
    } catch (error) {
        actionMessage.textContent = `添加工单失败：${error.message}`;
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
    actionMessage.textContent = "正在删除工单...";

    try {
        const response =
            await fetch(
                `${TICKETS_API_URL}/${id}`,
                {
                    method: "DELETE",
                    headers: getAuthHeaders()
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
        actionMessage.textContent = "工单已删除";
    } catch (error) {
        actionMessage.textContent = `删除工单失败：${error.message}`;
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

    actionMessage.textContent = "正在保存工单标题...";

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
                            "application/json",
                        ...getAuthHeaders()
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
            replaceTicket(
                tickets,
                updatedTicket
            );

        setTickets(newTickets);
        editingId = null;

        render(
            newTickets,
            editingId
        );

        actionMessage.textContent = "工单标题已更新";
    } catch (error) {
        actionMessage.textContent =
            "暂时无法确认保存结果，请重新加载工单核对";
        console.error(
            "标题保存流程出现异常:",
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
    actionMessage.textContent = "正在更新工单状态...";

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
                            "application/json",
                        ...getAuthHeaders()
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
        actionMessage.textContent = "工单状态已更新";

    } catch (error) {
        actionMessage.textContent = "更新失败,请稍后重试";
        console.error(
            "修改工单状态失败:",
            error.name,
            error.message
        );
    } finally {
        statusButton.disabled = false;
    }
}


// D：把当前收到的建议显示到页面
function renderTicketAdvice(id, advice, finished) {
    // D1：预览可能还没有全部字段；先准备空文字，收到摘要后再填进去。
    let summary = "";
    let nextSteps = "";
    let missingInfo = "";
    let stateText = "生成中";

    if (typeof advice.summary === "string") {
        summary = advice.summary;
    }

    // D2：建议步骤应是列表；只留下文字项，再用换行拼成可直接显示的文字。
    if (Array.isArray(advice.next_steps)) {
        nextSteps = advice.next_steps
            .filter(item => typeof item === "string")
            .join("\n");
    }

    // D3：待补充信息也是列表，和上面的建议步骤分开整理。
    if (Array.isArray(advice.missing_info)) {
        missingInfo = advice.missing_info
            .filter(item => typeof item === "string")
            .join("\n");
    }

    // D4：只有后端的 done 消息才传入 true；预览期间仍显示“生成中”。
    if (finished) {
        stateText = "生成完成";
    }

    // 分成三块便于阅读；仍用 textContent 填文字，模型内容不作为 HTML 执行。
    adviceOutput.textContent = "";
    adviceOutput.classList.add("has-sections");
    const ticketLine = document.createElement("p");
    ticketLine.className = "advice-ticket-line";
    ticketLine.textContent = `工单 #${id}（${stateText}）`;
    adviceOutput.append(ticketLine, document.createTextNode("\n\n"));

    const sections = [
        ["【工单摘要】", summary],
        ["【建议下一步】", nextSteps],
        ["【待补充信息】", missingInfo]
    ];
    sections.forEach(function ([title, content], index) {
        const section = document.createElement("section");
        section.className = "advice-section";
        const heading = document.createElement("h3");
        heading.textContent = title;
        const body = document.createElement("p");
        body.textContent = content;
        section.append(heading, document.createTextNode("\n"), body);
        adviceOutput.append(section);
        // 显式保留分隔换行，复制时得到的仍是原来那份完整三栏文字。
        if (index < sections.length - 1) {
            adviceOutput.append(document.createTextNode("\n\n"));
        }
    });
    setAdviceViewState(finished ? "done" : "generating", stateText);
}


// D5：复制已确认完成的建议；失败只改复制提示，不覆盖建议正文。
async function handleCopyAdvice() {
    if (copyingAdvice || !finalAdviceText) {
        return;
    }

    // 记住这次点击要复制的文字和生成轮次，等待期间也不改成另一份内容。
    const textToCopy = finalAdviceText;
    const generationAtCopy = adviceGeneration;
    copyingAdvice = true;
    copyAdviceButton.disabled = true;
    copyAdviceMessage.textContent = "正在复制...";

    try {
        // 浏览器把文字放进剪贴板；成功后才显示“已复制”。
        await navigator.clipboard.writeText(textToCopy);
        if (generationAtCopy === adviceGeneration) {
            copyAdviceMessage.textContent = "已复制完整建议，可以粘贴到其他地方。";
        }
    } catch {
        if (generationAtCopy === adviceGeneration) {
            copyAdviceMessage.textContent = "复制失败，请重试，或选中建议文字手动复制。";
        }
    } finally {
        copyingAdvice = false;
        // 如果期间开始了新生成，finalAdviceText 已被清空，按钮仍然禁用。
        copyAdviceButton.disabled = !finalAdviceText;
    }
}


// E：请求新接口，逐段读取消息
async function handleAdviceAction(id, adviceButton) {
    // 已有生成正在进行时，本次点击不再发请求。
    if (generatingAdvice) {
        return;
    }
    // 分别锁住程序的生成入口和本次按钮，等成功或失败后由 E5 恢复。
    generatingAdvice = true;
    adviceButton.disabled = true;
    // 新一轮开始，上一份结果不再作为当前可复制的建议。
    adviceGeneration += 1;
    finalAdviceText = "";
    copyAdviceButton.disabled = true;
    copyAdviceMessage.textContent = "正在生成，完成后可复制完整建议。";
    adviceOutput.classList.remove("has-sections");
    setAdviceViewState("generating", "生成中");
    adviceOutput.textContent = `正在为工单 #${id} 生成建议...`;
    // 先记为“还没有读取工具”；若请求提前失败，E5 就跳过读取工具的清理。
    let reader = null;

    try {
        // E1：请求这张工单的流式建议，并带上访问凭据；等待的是响应，不是完整建议。
        const response = await fetch(`${TICKETS_API_URL}/${id}/advice/stream`, {
            method: "POST",
            headers: getAuthHeaders()
        });
        // HTTP 失败先报错；即使 HTTP 成功，后续正文仍可能包含生成失败消息。
        if (!response.ok) {
            throw new Error(`生成建议失败，HTTP状态码：${response.status}`);
        }
        if (!response.body) {
            throw new Error("没有收到可读取的响应内容");
        }
        // 给这一次响应取得读取工具；循环中的多次 read 都用同一个 reader。
        reader = response.body.getReader();
        // 同一个 decoder 保留尚未凑齐的汉字字节；buffer 保存已解码但尚未处理的文字。
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        // E2：收到新内容就接起来，取出完整的行
        while (true) {
            // 浏览器返回 { value: 本次字节, done: 是否已经读尽并结束 }；暂时没数据就等待。
            const result = await reader.read();
            // 后端的 done 消息会在 E3 提前 return；走到这里仍读完，表示没收到完整成功结果。
            if (result.done) {
                throw new Error("AI建议未完整生成，请重试");
            }
            // 把本次字节读成文字并接到旧 buffer 后；stream:true 留住尚未读完整的字符字节。
            buffer += decoder.decode(result.value, { stream: true });
            // 后端每条消息用换行结尾；split 得到字符串数组，本身不检查 JSON 是否正确。
            const lines = buffer.split("\n");
            // pop 取走并返回最后一段交给 buffer；其余完整行留在 lines 中处理。
            buffer = lines.pop();

            // E3：逐行识别预览、完成或失败
            for (const line of lines) {
                // 空白行跳过当前这一项；不会因此结束外层读取循环。
                if (!line.trim()) {
                    continue;
                }
                // 把一行 JSON 文字读成可取字段的值；格式错误会直接进入外面的 E4。
                const message = JSON.parse(line);
                // 先排除 null 等空值及基本类型，才能继续按约定检查消息字段。
                if (!message || typeof message !== "object") {
                    throw new Error("收到无法识别的AI消息");
                }
                // 后端明确报错时，优先显示它给的文字；没给文字时用默认提示。
                if (message.type === "error") {
                    throw new Error(
                        typeof message.message === "string"
                            ? message.message
                            : "AI建议生成失败，请重试"
                    );
                }
                // 除了上面已处理的 error，只接收预览 preview 或最终成功 done。
                if (message.type !== "preview" && message.type !== "done") {
                    throw new Error("收到无法识别的AI消息");
                }
                // 取出建议内容；整份建议要按字段名读取，内部 next_steps 等仍可以是列表。
                const advice = message.data;
                if (!advice || typeof advice !== "object" || Array.isArray(advice)) {
                    throw new Error("AI建议数据格式不正确，请重试");
                }

                // finished 是我们自己的判断结果，不是 reader.read() 返回的 result.done。
                const finished = message.type === "done";
                // D 更新页面后回到这里；预览继续读，最终结果则结束本次函数。
                renderTicketAdvice(id, advice, finished);
                if (finished) {
                    // 只有 done 才保存可复制内容；保留工单编号、三栏标题和换行。
                    finalAdviceText = adviceOutput.textContent;
                    copyAdviceButton.disabled = copyingAdvice;
                    copyAdviceMessage.textContent = "生成完成，可以复制完整建议。";
                    // return 退出整个 handleAdviceAction，但离开前仍会执行 E5 的 finally。
                    return;
                }
            }
        }
    } catch (error) {
        // E4：接住上面请求、读取或消息检查的错误，用提示替换旧预览。
        finalAdviceText = "";
        copyAdviceButton.disabled = true;
        copyAdviceMessage.textContent = "本次生成未完成，暂时不能复制。";
        adviceOutput.classList.remove("has-sections");
        setAdviceViewState("error", "生成失败");
        adviceOutput.textContent = error.message;
    } finally {
        // E5：成功 return 或失败 catch 后都会到这里；恢复生成入口和本次按钮。
        generatingAdvice = false;
        adviceButton.disabled = false;
        // 有读取工具才清理；这里已经离开读取循环，不会释放后再回去 read。
        if (reader) {
            try {
                // 不再要这次响应的未读内容；正常 done 已带完整建议，不会截断已显示的答案。
                await reader.cancel();
            } catch {
                // 取消可能失败；这一次清理错误不覆盖已经显示的成功结果或失败提示。
            }
            // 另一个动作：解除这个 reader 对响应流的独占读取权；不会把 reader 变量变成 null。
            reader.releaseLock();
        }
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

    // “生成建议”的点击入口：把这张工单编号和实际点到的按钮交给 E。
    if (action === TICKET_ACTION.GENERATE_ADVICE) {
        await handleAdviceAction(id, clickedButton);
        return;
    }

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
    if (tokenInput.value.trim() === "") {
        actionMessage.textContent =
            "请先输入访问凭据，再点击“重新加载”。";
        return;
    }

    actionMessage.textContent = "";


    try {
        reloadButton.disabled = true;
        renderLoading();

        const response =
            await fetch(TICKETS_API_URL, {
                headers: getAuthHeaders()
            });

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

copyAdviceButton.addEventListener(
    "click",
    handleCopyAdvice
);

// 表单提交同时支持按钮点击和输入框里的回车，仍调用原来的业务函数。
createTicketForm.addEventListener("submit", function (event) {
    event.preventDefault();
    handleAddTicket();
});

ticketList.addEventListener(
    "click",
    handleTicketListClick
);

accessForm.addEventListener("submit", function (event) {
    event.preventDefault();
    loadTicketsFromApi();
});

const navigationLinks = document.querySelectorAll(".nav-link");
navigationLinks.forEach(function (link) {
    link.addEventListener("click", function () {
        navigationLinks.forEach(function (item) {
            item.classList.remove("is-active");
            item.removeAttribute("aria-current");
        });
        link.classList.add("is-active");
        link.setAttribute("aria-current", "location");
    });
});

loadTicketsFromApi();
