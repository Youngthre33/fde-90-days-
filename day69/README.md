# Day 69：通过 PATCH 编辑并持久化工单标题

## 今天完成了什么

Day68 的标题编辑只修改浏览器中的数组。当前页面看起来已经改变，但重新加载后会被服务器中的旧数据覆盖。

Day69 将保存标题接入本地 REST API：

```text
PATCH /tickets/:id
```

完成后的流程是：

```text
用户修改标题
→ PATCH 更新服务器
→ 服务器返回修改后的工单
→ 浏览器采用服务器确认的标题
→ 更新 tickets 数组
→ 退出编辑状态
→ 重新渲染页面
```

本 Day 还完成了：

- 保存期间禁用当前保存按钮，避免连续提交同一个请求。
- 使用 `response.ok` 识别 HTTP 失败。
- 使用 `try / catch / finally` 处理网络错误并恢复按钮。
- 保存失败时保留编辑状态和输入内容，服务器恢复后可以直接重试。
- 补回“取消编辑”的事件分支；取消不会发送请求，也不会修改服务器。

## 运行环境

前端由 Live Server 提供：

```text
http://127.0.0.1:5500/day69/index.html
```

本地 API 由 json-server 提供：

```powershell
npx.cmd json-server@0.17.4 --watch day69/db.json --port 3000 --delay 2000
```

工单集合地址：

```text
http://127.0.0.1:3000/tickets
```

端口职责：

| 端口 | 作用 |
|---|---|
| `5500` | 提供 HTML 和 JavaScript 前端页面 |
| `3000` | 接收 GET、POST、PATCH 等 API 请求 |

## 为什么使用 PATCH

编辑标题只需要修改一个字段：

```javascript
{
    title: newTitle
}
```

实际请求地址包含目标工单 ID：

```javascript
`${TICKETS_API_URL}/${id}`
```

如果 `id` 是 `101`，地址就是：

```text
http://127.0.0.1:3000/tickets/101
```

PATCH 只更新请求正文中提供的字段。没有发送的 `id` 和 `status` 会保留。

## PATCH 请求代码

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

            body:
                JSON.stringify({
                    title: newTitle
                })
        }
    );
```

其中：

- `fetch(...)` 返回 Promise。
- `await fetch(...)` 等待 Promise，并得到 Response 对象。
- `JSON.stringify(...)` 返回新的 JSON 字符串，不修改输入框、标题字符串或工单对象。
- 请求正文只包含 `title`。

## 完整成功执行顺序

```text
点击编辑
→ editingId = id
→ render() 创建编辑输入框和保存按钮
→ 用户修改 editInput.value
→ 点击保存
→ saveButton 指向 event.target
→ saveButton.disabled = true
→ newTitle 取得 editInput.value
→ JSON.stringify({ title: newTitle })
→ fetch() 发出 PATCH 并返回 Promise
→ await 得到 Response
→ 检查 response.ok
→ response.json() 返回解析 Promise
→ await 得到 updatedTicket
→ editTicket() 创建 newTickets 新数组
→ setTickets(newTickets) 改变 tickets 的指向
→ editingId = null
→ render() 重建页面列表
→ finally 执行
```

顺序原则：

```text
服务器先确认成功
→ 浏览器状态再更新
→ 页面最后更新
```

因此服务器保存失败时，页面不会假装已经保存成功。

## Response、updatedTicket 和 Promise

```javascript
const response =
    await fetch(...);
```

`fetch()` 返回 Promise，但经过 `await` 后，变量 `response` 指向 Response 对象。

```javascript
const updatedTicket =
    await response.json();
```

`response.json()` 返回另一个 Promise；经过第二次 `await` 后，`updatedTicket` 指向解析得到的新 JavaScript 对象。

`response` 和 `updatedTicket` 不是同一个对象：

```text
response      → HTTP Response 对象
updatedTicket → 响应正文解析出的工单对象
```

## HTTP 错误与网络错误

HTTP 404、500 等响应通常不会让 `fetch()` 自动 rejected。只要服务器返回了响应，`await fetch()` 通常仍能得到 Response，因此需要主动检查：

```javascript
if(!response.ok){

    throw new Error(
        `修改工单失败,HTTP状态码:${response.status}`
    );
}
```

`response.ok` 在状态码 200 到 299 时为 `true`。

HTTP 500 时：

```text
fetch Promise fulfilled
→ response 指向 Response
→ response.ok 为 false
→ new Error(...) 创建 Error 对象
→ throw 抛出对象
→ catch(error) 接住同一个对象
```

此时通常为：

```text
error.name    → "Error"
error.message → 包含 HTTP 状态码 500
```

服务器离线时没有 HTTP 响应：

```text
fetch Promise rejected
→ await 抛出错误
→ response 没有完成赋值
→ response.ok 不执行
→ catch 接住 TypeError
```

Chrome 中常见信息是：

```text
error.name    → "TypeError"
error.message → "Failed to fetch"
```

## catch 与 finally

保存失败时：

```text
跳过 response.json()
→ 不创建 updatedTicket
→ 不执行 editTicket()
→ 不创建 newTickets
→ 不执行 setTickets()
→ editingId 保持原 ID
→ 不执行 render()
→ 输入框 DOM 和输入内容继续存在
→ finally 恢复保存按钮
```

当前 `catch` 没有再次 `throw error`，所以错误被处理后，外层 async 点击回调最终 fulfilled，完成值为 `undefined`。

如果在 `catch` 中再次执行：

```javascript
throw error;
```

则外层 async 函数返回的 Promise 最终 rejected。

## 作用域与按钮引用

```javascript
const saveButton =
    event.target;
```

`saveButton` 与 `event.target` 指向同一个 DOM 按钮对象，没有复制或创建第二个按钮。

它声明在 `try` 外，因此 `finally` 可以访问它：

```javascript
const saveButton = event.target;

try{
    // 保存
}catch(error){
    // 处理错误
}finally{
    saveButton.disabled = false;
}
```

`updatedTicket` 和 `newTickets` 只在成功路径使用，所以声明在 `try` 的块级作用域内。

## 数组、对象引用和返回值

`editTicket()` 使用 `map()`：

- 创建新的外层数组。
- 为被编辑的工单创建新对象。
- 未修改的工单对象继续与旧数组共享引用。

当前只把：

```javascript
updatedTicket.title
```

传给 `editTicket()`，没有把整个 `updatedTicket` 对象放入数组。因此，即使内容相同：

```javascript
updatedTicket === newTickets[0]
```

仍然是 `false`。

`setTickets(newTickets)` 只执行：

```javascript
tickets = newTickets;
```

它不会创建第三个数组，也不会修改旧数组。它没有显式 `return`，返回值为 `undefined`。

执行后：

```javascript
tickets === newTickets
```

是 `true`。

## 服务器、浏览器状态与 DOM

| 层次 | 负责代码 | 变化 |
|---|---|---|
| 服务器 | `PATCH /tickets/:id` | 修改 `db.json` 中指定工单的标题 |
| 浏览器状态 | `editTicket()`、`setTickets()` | 创建新数组并更新 `tickets` 指向 |
| 页面 DOM | `render()` | 清空并重建列表，显示新标题 |

只调用 `editTicket()`、`setTickets()` 和 `render()`，重新加载后会恢复服务器旧数据。

只完成 PATCH 而不更新浏览器数组和 DOM，服务器已经改变，但当前页面不会立即跟随改变。

## 取消编辑

主事件处理增加了：

```javascript
if(action === TICKET_ACTION.CANCEL){

    editingId = null;

    render(
        tickets,
        editingId
    );
}
```

取消前的临时标题只存在于输入框 DOM 中，还没有进入服务器和 `tickets` 数组。

`editingId = null` 只改变编辑状态；随后 `render()` 才会移除旧输入框，并根据未改变的 `tickets` 重建列表。取消不会发送 GET 或 PATCH。

## 实际验证

- Network 中确认保存请求为 `PATCH /tickets/101`，状态码 200。
- Request Payload 只包含 `title`。
- Response 保留 `id`、新标题和原有 `status`。
- 保存后页面退出编辑状态并显示新标题。
- 重新加载和完整刷新后，新标题仍存在，证明服务器已持久化。
- 勾选“保留日志”后，可以同时区分保存产生的 PATCH 和重新加载产生的 GET。
- 使用 `--delay 2000` 确认保存等待期间按钮被禁用。
- 服务器离线时，请求进入 `catch`，输入框和输入值保留，按钮由 `finally` 恢复。
- 服务器恢复后可以直接重试，PATCH 成功。
- 取消编辑时，临时输入被放弃，页面恢复数组中的原标题，服务器数据不变。

## 当前边界

Day69 已接入服务器的操作：

```text
GET /tickets
POST /tickets
PATCH /tickets/:id（编辑标题）
```

仍然只修改浏览器状态的操作：

```text
删除工单
切换工单状态
```

它们重新加载后仍会恢复为服务器数据，后续 Day 再分别接入 API。

其他已知边界：

- 创建和编辑标题还没有空值或纯空格验证。
- 保存失败只记录在 Console，页面没有可见错误提示。
- 保存期间只禁用当前保存按钮，其他行操作仍可能形成竞态。
- 未保存时切换到另一张工单编辑，当前 DOM 输入可能丢失。
- 事件委托目前依赖 `event.target.tagName === "BUTTON"`；按钮加入内部图标后需要改用 `closest("button")`。
- 当前 ID 转换为 `Number`，只适用于现有数字 ID。

## Day69 闭环

```text
理解 PATCH 持久化意义
→ 亲手接入 PATCH
→ 运行成功路径
→ 观察 Network 请求与响应
→ 模拟服务器离线并 Debug
→ 恢复服务器后原地重试
→ 解释 Promise、Response、作用域、引用和返回值
→ 完成检测题
→ 修复取消按钮事件分支
→ 静态检查
→ Git commit
→ 必要时 push
```
