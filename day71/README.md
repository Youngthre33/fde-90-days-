# Day 71：通过 DELETE 持久化删除工单

## 今天解决的问题

Day70 以前，点击“删除”只会修改浏览器中的 `tickets` 数组和页面 DOM：

```text
点击删除
→ deleteTicket() 创建新数组
→ setTickets() 更新浏览器状态
→ render() 更新页面
→ 服务器数据没有改变
```

因此页面虽然暂时看不到被删除的工单，但重新加载执行 `GET /tickets` 后，服务器仍会把它返回。

Day71 将删除接入本地 API：

```text
DELETE /tickets/:id
```

新的执行顺序是：

```text
点击删除按钮
→ 禁用当前按钮
→ 向服务器发送 DELETE
→ 等待服务器响应
→ 检查 response.ok
→ 服务器确认成功
→ deleteTicket() 创建浏览器新数组
→ setTickets() 保存新数组
→ render() 更新页面 DOM
→ finally 收尾
```

成功删除会写入 `day71/db.json`。重新加载或刷新页面以后，被删除的工单不会再回来。

## 运行环境

前端页面：

```text
http://127.0.0.1:5500/day71/index.html
```

本地 API：

```text
http://127.0.0.1:3000/tickets
```

启动 json-server：

```powershell
npx.cmd json-server@0.17.4 --watch day71/db.json --port 3000 --delay 2000
```

`--delay 2000` 让响应延迟约两秒，便于观察请求期间按钮是否禁用，以及页面是否等待服务器确认后才更新。

## 整理后的模块职责

Day71 完成功能验证后，对代码做了一次只改善结构的整理。各文件保持单一、明确的职责：

| 文件 | 主要职责 |
|---|---|
| `constants.js` | 集中保存状态、按钮动作和 API 地址 |
| `data.js` | 保存浏览器当前使用的 `tickets` 数组，并提供 `setTickets()` |
| `ticket.js` | 使用 `filter()`、`map()` 等方式计算新数据，不访问服务器和 DOM |
| `render.js` | 把浏览器数据和编辑状态渲染成页面 DOM |
| `main.js` | 接收用户操作、调用 API，并协调数据层和渲染层 |

`main.js` 按下面的阅读顺序组织：

```text
模块依赖
→ 页面状态和 DOM 引用
→ 创建工单
→ 删除工单
→ 保存标题
→ 切换状态
→ 列表点击事件分发
→ 从 API 加载工单
→ 事件注册和程序启动
```

长的异步动作各自放进有名字的函数中。列表点击处理器只负责读取 `action` 和 `id`，再把任务交给相应函数。这样可以直接根据函数名定位功能，同时仍然保留每个 API 请求的完整执行顺序。

## 三层状态

| 层次 | 保存位置 | 删除时由谁修改 |
|---|---|---|
| 服务器数据 | `day71/db.json` | `DELETE /tickets/:id` |
| 浏览器状态 | `tickets` 数组 | `deleteTicket()` 和 `setTickets()` |
| 页面显示 | DOM | `render()` |

假设开始时三层都有 101 和 102。旧的本地删除只改变后两层：

```text
服务器：      [101, 102]
浏览器数组：  [102]
页面：        102
```

重新加载后，服务器会再次返回 101。Day71 成功执行 DELETE 后，三层会保持一致：

```text
服务器：      [102]
浏览器数组：  [102]
页面：        102
```

## 为什么服务器删除后还要修改浏览器数组

DELETE 只负责修改服务器。服务器数据改变以后，浏览器已经加载的数组不会自动改变，页面也不会自动重新渲染。因此仍然需要：

```text
DELETE
→ 修改服务器

deleteTicket() + setTickets()
→ 修改浏览器状态

render()
→ 修改页面 DOM
```

## DELETE 请求

```javascript
const response =
    await fetch(
        `${TICKETS_API_URL}/${id}`,
        {
            method: "DELETE"
        }
    );
```

点击 ID 101 时，实际请求为：

```text
DELETE http://127.0.0.1:3000/tickets/101
```

`/tickets` 表示工单集合，`/tickets/101` 表示 ID 为 101 的单个资源。删除一个具体工单时，URL 必须包含 ID。

## 为什么没有 body 和 Content-Type

PATCH 需要告诉服务器字段要修改成什么，所以要发送 JSON 正文。DELETE 的目标已经由 URL 中的 ID 指定，当前 API 不需要其他参数，因此没有 `body`。

`Content-Type` 用于说明请求正文的格式。当前 DELETE 没有正文，也就不需要声明 JSON 格式：

```javascript
{
    method: "DELETE"
}
```

准确说法是“当前项目的 DELETE API 不需要请求正文”。真实项目仍应遵守具体 API 契约。

## 为什么不调用 response.json()

POST 需要解析服务器生成的完整工单，PATCH 需要解析服务器确认的更新结果。DELETE 成功后，前端已经知道要移除哪个 ID，因此可以直接调用 `deleteTicket(tickets, id)`。

一些服务器会为成功的 DELETE 返回空正文，例如 `204 No Content`。强制执行 `response.json()` 可能让已经成功的服务器删除在解析阶段报错。所以 Day71 只依赖 HTTP 成功状态，不依赖固定响应正文。

## 整理后的删除函数和事件分发

```javascript
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

        if(editingId === id){
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

// handleTicketListClick() 中的删除分发：
if (action === TICKET_ACTION.DELETE) {
    await handleDeleteAction(
        id,
        clickedButton
    );

    return;
}
```

`handleTicketListClick()` 负责确定“用户点击的是删除”，`handleDeleteAction()` 负责执行完整的服务器请求和本地更新。函数拆开后，业务顺序没有改变。

## 为什么必须先检查 response.ok

HTTP 404 或 500 时，`fetch()` 的 Promise 通常仍然 fulfilled，因为服务器正常返回了一份 HTTP 响应。必须主动检查：

```javascript
if(!response.ok){
    throw new Error(
        `删除工单失败,HTTP状态码:${response.status}`
    );
}
```

检查必须位于 `deleteTicket()` 前面：

```text
服务器确认成功
→ 才允许修改浏览器数组和 DOM
```

否则页面可能先消失，随后才发现服务器删除失败，还需要额外编写回滚逻辑。

## deleteTicket() 和 filter()

`deleteTicket()` 使用 `filter()` 创建新数组：

```javascript
function deleteTicket(tickets,id){
    return tickets.filter(
        function(ticket){
            return ticket.id !== id;
        }
    );
}
```

删除 101 时，101 的回调结果为 `false`，不会进入新数组；102 的结果为 `true`，会进入新数组。

```javascript
newTickets === oldTickets
// false

newTickets[0] === ticket102
// true

oldTickets.length
// 2

newTickets.length
// 1
```

`filter()` 创建新的外层数组，但没有复制未删除的工单对象；旧数组也没有被原地修改。

## setTickets() 和 render()

```javascript
setTickets(newTickets);
```

内部执行 `tickets = newTickets`，也就是让 `tickets` 指向 `newTickets`，不是让 `newTickets` 指向 `tickets`。执行后：

```javascript
tickets === newTickets
// true
```

`setTickets()` 不创建第三个数组，也不更新 DOM。它没有显式 `return`，所以返回 `undefined`。

随后 `render(newTickets, editingId)` 直接渲染刚刚得到的新数组。`setTickets(newTickets)` 仍然必须执行，因为它负责更新模块中共享的浏览器状态；`render()` 只更新 DOM，不会给 `tickets` 重新赋值。

## 删除按钮的引用

```javascript
const clickedButton = event.target;

await handleDeleteAction(
    id,
    clickedButton
);
```

`clickedButton` 和 `event.target` 指向同一个旧按钮对象。传入函数后，参数 `deleteButton` 也指向这个对象：

```javascript
deleteButton === clickedButton
// true
```

`deleteButton` 是 `handleDeleteAction()` 的参数，所以整个函数以及其中的 `finally` 都可以访问它。按钮仍然在第一个 `await` 前禁用，可以阻止等待期间重复点击。

成功时会执行 `render()`。局部变量不会自动改变指向：

```text
deleteButton
→ 仍然指向用户点击的旧按钮
→ 旧按钮已经离开页面 DOM
```

成功后的 `finally` 修改的是离开 DOM 的旧按钮。

失败时不会执行 `render()`：

```text
deleteButton
→ 仍然指向用户点击的旧按钮
→ 同一个按钮仍然显示在页面上
```

这时 `finally` 恢复的是页面当前按钮，用户可以再次尝试。

| 情况 | `deleteButton` 指向 | `finally` 恢复谁 |
|---|---|---|
| DELETE 成功并执行 `render()` | 已离开 DOM 的旧按钮 | 旧按钮对象 |
| DELETE 失败，没有执行 `render()` | 页面中仍显示的旧按钮 | 页面当前按钮 |

## HTTP 404 与服务器离线

| 情况 | `fetch` Promise | 能否得到 `response` | 是否检查 `response.ok` |
|---|---|---:|---:|
| HTTP 404 | fulfilled | 能 | 能，结果为 `false` |
| HTTP 500 | fulfilled | 能 | 能，结果为 `false` |
| 服务器关闭或网络中断 | rejected | 不能 | 不能 |

HTTP 404：

```text
服务器返回 404
→ await 得到 Response
→ response.ok 为 false
→ 主动 throw Error
→ 跳过本地删除和 render
→ catch
→ finally
```

服务器关闭：

```text
fetch Promise rejected
→ await fetch() 抛错
→ response 没有完成赋值
→ response.ok 不执行
→ 跳过本地删除和 render
→ catch
→ finally
```

## 404 实验中的三层状态

Day71 实际进行了下面的测试：

```text
页面先显示临时工单
→ 手动直接从服务器删除该工单
→ 不重新加载页面
→ 再点击页面删除按钮
→ 第二次 DELETE 返回 404
```

第二次请求前：

```text
服务器：      已经没有临时工单
浏览器数组：  仍然有临时工单
页面 DOM：    仍然显示临时工单
```

应用收到 404 后跳过本地删除。随后重新 `GET /tickets`，浏览器数组和页面同步到服务器状态，临时工单最终消失。

## DELETE 的幂等性

```text
第一次 DELETE：存在 → 不存在
第二次 DELETE：不存在 → 仍然不存在
```

两次操作结束后，资源最终都是“不存在”，所以 DELETE 具有幂等性。幂等性不要求响应状态码相同：第一次可以返回成功的 2xx，第二次可以返回 404。

## 实际验证结果

### 成功路径

- 页面发出 `DELETE /tickets/:id`。
- 请求等待期间，当前删除按钮被禁用。
- 服务器返回成功的 2xx 后，目标工单才从页面消失。
- 重新加载和完整刷新后，目标工单没有恢复。

### 服务器离线

- 页面先正常加载工单，然后关闭 json-server。
- 点击删除后，`fetch` Promise rejected。
- 没有得到本次请求的 `response`。
- 浏览器数组和页面没有提前删除工单。
- `finally` 恢复了当前删除按钮。

### HTTP 404

- 先从服务器手动删除临时工单，页面暂时保留旧数据。
- 再点击页面删除按钮，第二次 DELETE 返回 404。
- `fetch` Promise fulfilled，`response.ok` 为 `false`。
- 本地删除和 `render()` 被跳过。
- 重新加载后页面与服务器重新同步，临时工单消失。

### 静态与数据检查

- Day71 五个 JavaScript 文件全部通过 `node --check`。
- `git diff --check` 通过。
- `deleteTicket()` 的新数组、目标排除、未删除对象引用和旧数组不变检查通过。
- `day71/db.json` 和 `mock-tickets.json` 可以正常解析。
- `day71/db.json` 与实时 API 都恢复为 ID 101、102。
- `broken-tickets.json` 继续作为故意损坏的解析错误夹具保留。

## 当前已经接入服务器的操作

```text
GET /tickets
POST /tickets
PATCH /tickets/:id（修改标题）
PATCH /tickets/:id（切换状态）
DELETE /tickets/:id（删除工单）
```

工单系统目前已经完成加载、创建、编辑标题、切换状态和删除的服务器持久化主链路。

## 当前边界

- 创建和编辑标题还没有空值或纯空格验证。
- 请求失败只记录在 Console，页面没有可见错误提示。
- 删除请求期间只禁用当前删除按钮，其他操作仍可并发。
- 当前删除是永久删除，没有确认弹窗、撤销或软删除。
- 当前事件委托依赖 `event.target.tagName === "BUTTON"`；按钮内加入图标后需要考虑 `closest("button")`。
- 当前把 DOM 中的 ID 转为 `Number`，适用于现有数字 ID。
- json-server 没有真实业务系统中的登录、权限、审计和删除规则。
- 当前采用服务器优先删除，没有实现乐观删除和失败回滚。
- 如果服务器已经删除成功，但之后的浏览器代码意外失败，页面可能暂时过期；重新 GET 可以恢复同步。

## Day71 完整主线

```text
DELETE 修改服务器
→ deleteTicket()/filter() 创建浏览器新数组
→ setTickets() 让 tickets 指向新数组
→ render() 更新 DOM
```

服务器成功时才允许后两层变化；HTTP 错误和网络错误都会跳过本地删除，并通过 `finally` 恢复按钮。
