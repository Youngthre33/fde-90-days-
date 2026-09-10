# Day 70：通过 PATCH 持久化工单状态

## 今天解决的问题

Day69 已经把“修改工单标题”接入服务器，但状态按钮仍然只修改浏览器中的 `tickets` 数组：

```text
点击状态按钮
→ 浏览器数组改变
→ render() 更新页面
→ 服务器没有改变
→ 重新加载后恢复服务器中的旧状态
```

Day70 将状态切换接入本地 REST API：

```text
PATCH /tickets/:id
```

完成后的流程是：

```text
用户点击状态按钮
→ 根据按钮 ID 找到当前工单
→ 计算下一个状态
→ PATCH 更新服务器
→ 解析服务器返回的完整工单
→ 用服务器工单替换浏览器数组中的旧工单
→ 保存新数组
→ 重新渲染页面
```

状态现在会保存到 `day70/db.json`，刷新页面后不会恢复为旧值。

## 运行环境

前端由 Live Server 提供：

```text
http://127.0.0.1:5500/day70/index.html
```

本地 API 由 json-server 提供：

```powershell
npx.cmd json-server@0.17.4 --watch day70/db.json --port 3000 --delay 2000
```

工单集合地址：

```text
http://127.0.0.1:3000/tickets
```

`--delay 2000` 故意让响应延迟约两秒，便于观察按钮禁用、异步等待和成功／失败的执行顺序。

## 状态循环规则

```text
open → in_progress → done → open
```

| 数据状态 | 页面状态 | 状态按钮文字 |
|---|---|---|
| `open` | 待处理 | 开始处理 |
| `in_progress` | 处理中 | 完成 |
| `done` | 已完成 | 重新打开 |

## `getNextTicketStatus()`：只计算下一个状态

```javascript
function getNextTicketStatus(
    currentStatus
){
    if(
        currentStatus ===
        TICKET_STATUS.OPEN
    ){
        return TICKET_STATUS.IN_PROGRESS;
    }

    if(
        currentStatus ===
        TICKET_STATUS.IN_PROGRESS
    ){
        return TICKET_STATUS.DONE;
    }

    if(
        currentStatus ===
        TICKET_STATUS.DONE
    ){
        return TICKET_STATUS.OPEN;
    }

    throw new Error(
        `非法工单状态: ${currentStatus}`
    );
}
```

这个函数只接收当前状态字符串，并返回下一个状态字符串：

```javascript
getNextTicketStatus("open");
// "in_progress"
```

它不会修改工单对象或 `tickets` 数组，不会创建新数组、请求服务器或更新页面。遇到非法状态时，它会抛出 Error，避免继续发送无法识别的状态。

## 从按钮 ID 找到当前工单

`render()` 创建按钮时，把工单 ID 保存到按钮的 `data-id`：

```javascript
statusButton.dataset.id =
    ticket.id;
```

点击后，事件处理函数读取并转换这个值：

```javascript
const id =
    Number(
        event.target.dataset.id
    );
```

HTML 的 `data-id` 读取结果是字符串，`Number()` 把例如 `"101"` 转换成数字 `101`，使它可以与数字工单 ID 使用严格相等比较。

随后用 `find()` 查找当前工单：

```javascript
const currentTicket =
    tickets.find(
        function(ticket){
            return ticket.id === id;
        }
    );
```

这里有两层返回值：

- 回调函数返回 `true` 或 `false`，告诉 `find()` 当前元素是否匹配；
- `find()` 返回第一个匹配的原数组元素，完全找不到时返回 `undefined`。

找到时，`currentTicket` 与数组中的目标工单指向同一个对象；`find()` 不创建对象或数组。

找不到时主动抛错，避免读取 `undefined.status`：

```javascript
if(!currentTicket){
    throw new Error(
        `找不到工单,ID:${id}`
    );
}
```

## PATCH 请求

得到当前工单后，先计算要发送的状态：

```javascript
const newStatus =
    getNextTicketStatus(
        currentTicket.status
    );
```

然后发送 PATCH：

```javascript
const response =
    await fetch(
        `${TICKETS_API_URL}/${id}`,
        {
            method: "PATCH",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({
                status: newStatus
            })
        }
    );
```

如果当前工单是 101，状态为 `open`，实际请求相当于：

```http
PATCH /tickets/101
Content-Type: application/json

{"status":"in_progress"}
```

URL 中的 `101` 指定修改哪张工单；请求正文中的 `status` 指定要修改成什么值。

## HTTP 错误与网络错误

收到 HTTP 404、500 等响应时，`fetch()` 的 Promise 通常仍然 fulfilled，因为浏览器确实收到了 HTTP 响应：

```text
await fetch() 得到 Response
→ response.ok 为 false
→ 代码主动 throw
→ catch 捕获 Error
```

因此必须检查：

```javascript
if(!response.ok){
    throw new Error(
        `修改工单状态失败,HTTP状态码:${response.status}`
    );
}
```

服务器关闭或网络中断时，没有 HTTP 响应：

```text
fetch Promise rejected
→ await 抛出 TypeError
→ response 没有完成赋值
→ 直接进入 catch
```

两种错误都不会执行后面的 `replaceTicket()`、`setTickets()` 和 `render()`，因此页面不会在服务器失败时假装修改成功。

## 采用服务器返回的完整工单

服务器成功后返回修改完成的完整工单：

```javascript
const updatedTicket =
    await response.json();
```

`response.json()` 返回 Promise；经过 `await` 后，`updatedTicket` 指向根据响应正文创建的新 JavaScript 对象。

即使属性内容相似：

```javascript
updatedTicket === currentTicket
```

仍然是 `false`，因为它们是两个不同的对象。

使用服务器对象的原因是，真实服务器可能同时添加或修正 `updatedAt`、`version` 等字段。直接采用服务器返回结果，可以避免前端漏掉这些变化。

## `replaceTicket()`：创建包含服务器对象的新数组

```javascript
function replaceTicket(
    tickets,
    updatedTicket
){
    return tickets.map(
        function(ticket){
            if(
                ticket.id ===
                updatedTicket.id
            ){
                return updatedTicket;
            }

            return ticket;
        }
    );
}
```

`map()` 遍历旧数组，并把每次回调函数返回的值放到新数组的对应位置：

- ID 相同时，直接返回服务器的 `updatedTicket`；
- ID 不同时，返回旧数组中的原 `ticket` 对象。

假设 101 是目标工单，102 没有修改：

```javascript
newTickets === tickets
// false：map 创建了新数组

newTickets[0] === updatedTicket
// true：目标位置直接采用服务器对象

newTickets[1] === tickets[1]
// true：未修改对象继续共享引用
```

旧数组和旧目标对象没有被原地修改。

## `setTickets()` 与 `render()`

```javascript
setTickets(newTickets);

render(
    tickets,
    editingId
);
```

`setTickets(newTickets)` 只让模块中的 `tickets` 重新指向 `newTickets`：

```text
执行前：tickets → 旧数组 A
执行后：tickets → 新数组 B
```

它不会创建第三个数组，也不会渲染页面。它没有显式 `return`，所以返回 `undefined`。

`tickets` 是 ES Module 的实时导入绑定，因此 `setTickets()` 重新赋值后，`main.js` 随后读取到的是新数组。

`render()` 读取当前数组并更新 DOM。它不修改服务器，也不负责保存浏览器数组。

## 状态按钮禁用与 `finally`

状态按钮在请求开始前被禁用：

```javascript
const clickedStatusButton =
    event.target;

clickedStatusButton.disabled =
    true;
```

`clickedStatusButton` 与 `event.target` 指向同一个 DOM 按钮对象，没有复制按钮。变量声明在 `try` 外面，因此 `finally` 可以访问：

```javascript
try{
    // 请求和更新
}catch(error){
    console.error(error.message);
}finally{
    clickedStatusButton.disabled = false;
}
```

成功时，`render()` 已经清空旧列表并创建新按钮。`clickedStatusButton` 变量仍然指向已经离开页面的旧按钮；页面显示的是 `render()` 创建的新按钮。

失败时没有执行 `render()`，旧按钮仍然显示在页面中；`finally` 把同一个按钮恢复为可点击，使用户可以重试。

## `render()` 如何处理旧按钮和新按钮

`renderTicketList()` 的第一步是：

```javascript
ticketList.textContent = "";
```

它把旧列表项和旧按钮从页面 DOM 树中移除。随后循环为当前数组重新创建元素：

```javascript
const statusButton =
    document.createElement("button");

item.append(
    editButton,
    statusButton,
    deleteButton
);

ticketList.append(item);
```

旧按钮没有被改造成新按钮。旧按钮和新按钮是两个不同的 DOM 对象：

```text
clickedStatusButton → 旧按钮，已经离开 DOM
页面 DOM            → render() 创建的新按钮
```

只要 `clickedStatusButton` 仍然引用旧按钮，旧对象就可以暂时存在于内存中；它已经不在页面树中，所以不会与新按钮同时显示或产生冲突。点击回调结束且没有其他引用后，浏览器可以在之后回收旧对象。

`ticketList` 本身没有被替换，点击监听也注册在这个列表元素上。新按钮的点击会继续冒泡到同一个 `ticketList`，所以重新渲染后不需要逐个重新注册按钮监听。

## 完整成功执行顺序

```text
点击状态按钮
→ event.target 指向当前按钮
→ 从 dataset 取得 action 和数字 id
→ clickedStatusButton 指向被点击按钮
→ clickedStatusButton.disabled = true
→ find() 找到 currentTicket
→ 检查 currentTicket 是否存在
→ getNextTicketStatus() 返回 newStatus
→ JSON.stringify({ status: newStatus })
→ fetch() 返回 Promise
→ await 得到 Response
→ 检查 response.ok
→ response.json() 返回解析 Promise
→ await 得到 updatedTicket
→ replaceTicket() 创建 newTickets
→ setTickets(newTickets) 更新模块状态
→ render() 更新页面 DOM
→ finally 执行
```

顺序原则：

```text
服务器先确认成功
→ 浏览器状态再更新
→ 页面最后更新
```

## 返回值、引用和可变性总结

| 表达式／函数 | 返回值或结果 | 是否修改原数据 |
|---|---|---|
| `find()` 回调 | `true` / `false` | 否 |
| `tickets.find(...)` | 原工单对象或 `undefined` | 否 |
| `getNextTicketStatus(...)` | 状态字符串 | 否 |
| `fetch(...)` | Promise | 否；请求成功后服务器处理 PATCH |
| `await fetch(...)` | Response | 否 |
| `response.json()` | Promise | 否 |
| `await response.json()` | 新解析对象 | 否 |
| `replaceTicket(...)` | 新数组 | 不修改旧数组；目标位置采用服务器对象 |
| `setTickets(...)` | `undefined` | 改变模块变量指向 |
| `render(...)` | `undefined` | 更新 DOM |

## 验证结果

- Network 中确认状态请求使用 `PATCH /tickets/:id`，成功状态码为 200。
- Request Payload 只包含 `status`，Response 返回完整工单。
- 页面在服务器成功后显示下一个状态；重新加载和完整刷新后状态仍然保留。
- 使用 `--delay 2000` 观察到请求等待期间当前状态按钮被禁用，请求结束后页面上的按钮可继续点击。
- 能区分服务器离线时的网络错误与 HTTP 404／500 响应。
- 五个 JavaScript 文件通过 `node --check`。
- 三种合法状态转换和非法状态抛错检查通过。
- `replaceTicket()` 的新数组、目标对象引用、未修改对象引用和旧数组不变检查通过。

## 当前边界

Day70 已接入服务器的操作：

```text
GET /tickets
POST /tickets
PATCH /tickets/:id（编辑标题）
PATCH /tickets/:id（切换状态）
```

仍然只修改浏览器状态的操作：

```text
删除工单
```

删除后重新加载，工单仍会从服务器恢复，后续 Day 再接入 DELETE。

其他已知边界：

- 创建和编辑标题还没有空值或纯空格验证。
- 请求失败只记录在 Console，页面没有可见错误提示。
- 状态请求期间只禁用当前状态按钮，其他行操作仍可能形成并发请求。
- json-server 接受前端发送的状态，没有实现真实业务服务器中的权限和状态流转校验。
- 事件委托目前依赖 `event.target.tagName === "BUTTON"`；按钮加入内部图标后需要改用 `closest("button")`。
- 当前 ID 使用 `Number()` 转换，只适用于现有数字 ID。

## Day70 闭环

```text
理解状态只在浏览器修改时无法持久化
→ 亲手拆分状态计算函数
→ 从按钮 ID 查找当前工单
→ 亲手接入状态 PATCH
→ 使用服务器返回对象更新新数组
→ 运行成功路径并确认刷新后保留
→ 加入按钮禁用和 finally 收尾
→ Debug 拼写、括号、导入导出和重复计算
→ 解释 find、map、引用、作用域、Promise 和错误路径
→ 完成检测题
→ 静态与函数检查
→ Git commit
→ 必要时 push
```
