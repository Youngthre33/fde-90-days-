# Day 68：通过 POST 创建并持久化工单

## 今天完成的功能

- 将“添加工单”从浏览器本地创建改为 `POST /tickets`。
- 请求时只发送标题和初始状态，由服务器生成工单 ID。
- 使用服务器返回的 `createdTicket` 更新浏览器数组并立即渲染页面。
- 请求期间禁用添加按钮，避免同一个请求尚未结束时重复提交。
- 使用 `try / catch / finally` 处理成功、服务器离线和恢复重试。
- 删除不再使用的本地 `addTicket()` 和临时调试日志。

## 端口与数据流

- `127.0.0.1:5500` 由 Live Server 提供前端页面。
- `127.0.0.1:3000` 由 json-server 提供工单 API。
- 地址栏保持在 5500；页面中的 `fetch()` 在后台请求 3000。

完整创建流程：

```text
输入标题
→ 创建 ticketToCreate
→ JSON.stringify() 生成请求字符串
→ fetch() 发出 POST 并返回 Promise
→ await 得到 Response
→ 检查 response.ok
→ response.json() 返回解析 Promise
→ await 得到 createdTicket
→ 创建 newTickets 新数组
→ setTickets() 改变 tickets 的指向
→ render() 更新页面 DOM
→ 清空输入框
→ finally 恢复按钮
```

## 对象、数组和引用

`ticketToCreate` 是浏览器发送前创建的对象，没有 ID：

```javascript
{
    title: title,
    status: "open"
}
```

`JSON.stringify(ticketToCreate)` 返回新的 JSON 字符串，不修改原对象。服务器收到字符串后创建资源并生成 ID；`response.json()` 又在浏览器中创建 `createdTicket` 新对象。因此 `ticketToCreate` 与 `createdTicket` 不是同一个对象。

页面必须加入服务器返回的 `createdTicket`，因为后续编辑、删除和状态修改需要服务器生成的 ID。

```javascript
const newTickets = [
    ...tickets,
    createdTicket
];
```

这会创建新的外层数组，不会原地修改旧数组；已有工单对象仍然共享引用。`setTickets(newTickets)` 不再创建数组，只让模块中的 `tickets` 重新指向 `newTickets`。

## 服务器、浏览器状态和 DOM

- json-server 把新工单写入 `db.json`。
- `setTickets()` 更新浏览器内存中的工单数组指向。
- `render()` 清空并重建页面列表，不会修改服务器，也不会清空浏览器数组。
- POST 成功但不调用 `setTickets()` 和 `render()` 时，服务器已有新工单，当前页面不会立即显示；之后重新加载会通过 GET 取得并显示它。

## 错误处理与 Promise

- HTTP 500 等响应通常不会让 `fetch()` 的 Promise 自动 rejected，因此需要检查 `response.ok` 并主动 `throw`。
- 服务器离线时，内部 `fetch` Promise rejected，`await` 抛出错误并进入 `catch`。
- `catch` 不再次抛错时，外层 async 点击回调最终 fulfilled，完成值为 `undefined`。
- `finally` 无论成功或失败都会恢复添加按钮。
- 本地 API 返回太快时，按钮可能在浏览器下一次绘制前恢复；用 json-server 的 `--delay 2000` 可以观察禁用状态。

## 实际验证

- POST 创建成功时返回 201，`response.ok` 为 `true`。
- 新工单立即显示，输入框清空，重新加载后仍然存在。
- 服务器离线时列表不增加，输入保留，错误被 `catch` 记录，按钮由 `finally` 恢复。
- 服务器恢复后可以直接重试并成功创建。
- 快速重复点击实验说明 POST 通常没有幂等性，也暴露了空标题仍可提交的问题。

## 当前边界

Day68 只把“创建工单”接入服务器。编辑标题、删除工单和切换状态目前仍然只修改浏览器状态，后续 Day 再逐项接入 API。标题为空时仍能提交，后续会加入输入验证。
