# Day 67：从真实 API 加载工单

## 我完成的实操

- 把页面的数据来源从静态 mock-tickets.json 改成 json-server 的 GET /tickets。
- 使用 TICKETS_API_URL 集中保存工单 API 地址。
- 增加 renderLoading() 显示请求期间的加载状态。
- 在 HTML 中让重新加载按钮初始禁用。
- 验证服务器正常、服务器离线和服务器恢复三种情况。
a
## 我的理解

### 1. renderLoading() 修改了什么
修改了页面文字和 `ul`，但是不会清空 `tickets` 数组，也不会修改服务器数据，只是页面 DOM 的改动。

作用就是 让列表工单在加载期间可以显示一个加载状态的提示语

### 2. 服务器离线时怎样执行

离线时 `fetch` 的 Promise 失败，`await` 产生错误，代码进入 `catch`，并显示错误类型和加载失败状态。

### 3. 按钮为什么会自动恢复

因为最后有 `finally`，所以无论请求成功还是失败，都会执行 `reloadButton.disabled = false` 恢复按钮。

### 4. setTickets(loadedTickets) 做了什么
`loadedTickets` 指向从服务器响应中解析出的数组 B。传入 `setTickets()` 后，参数 `newTickets` 也指向数组 B；`tickets = newTickets` 让 `tickets` 重新指向同一个数组 B，没有修改原来的数组，也没有在 `setTickets()` 中再创建一个新数组。
