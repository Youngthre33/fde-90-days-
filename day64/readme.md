# Day64：异步请求与错误处理阶段复盘

## 1. 页面首次加载的执行顺序

“正在加载工单...”最初来自哪里？
来自 index.html 中 <p id="ticket-count"> 的初始文字

为什么没有点击按钮，重新加载按钮也会变灰？

因为 main.js 首次加载时会主动调用 loadMockTickets()，
而这个函数在等待请求前会先执行 reloadButton.disabled = true。


数据回来后，页面如何变成“当前有2个工单”？

先通过 setTickets函数 赋值给tickets 然后再用render渲染

## 2. Promise、Response 和数组


fetch() 直接返回什么？
返回一个表示这次请求结果的 Promise


第一个 await 完成后，response 是什么？
是一个response的对象 对象包含很多信息 包括状态. ok 等等信息



response.json() 直接返回什么？
直接返回的也是一个promise


第二个 await 完成后，loadedTickets 是什么？

JSON 解析完成后得到的数组


## 3. HTTP 404 错误

404 时 response.ok 是什么？

false



为什么代码不会继续执行 response.json()？

因为 response.ok 是 false，进入 if 后执行了 throw，
所以跳过 try 中后面的代码，进入 catch。
response.json() 还没有被调用。



错误是在哪里创建和抛出的？

在 if 代码块中，new Error(...) 创建错误对象，
throw 把这个错误对象抛出。


## 4. JSON 解析错误

损坏的 JSON 为什么可能仍然得到 HTTP 200？

HTTP 200 只表示服务器成功返回了这个文件，
不表示文件中的 JSON 格式一定正确。
JSON 格式要到 response.json() 解析时才能检查。



错误发生在哪一行？
发生在解析 .json()


错误名称是什么？

SyntaxError


## 5. catch 和 finally


catch 的作用是什么？

接住抛出的错误,同时可以通过函数显示出错误的信息和名称等 这样就更好的识别错误


finally 的作用是什么？

finally 用来放成功和失败路径都需要执行的收尾代码。
在当前项目中，我们在里面设置 disabled = false，恢复按钮。

为什么恢复按钮的代码适合写在 finally 中？

因为finally不会因为错误或者判断等语句跳过 会保证最终一定会执行恢复按钮的工作


## 6. 重复异步请求

连续调用三次 loadMockTickets()，会得到几个 Promise？

会得到3个Promise

先发送的请求是否一定先完成？
不一定 要看响应的时间


如果请求 B 先完成、请求 A 后完成，页面最终可能显示哪一个？
最终显示的是数组A


disabled 能阻止什么？不能阻止什么？

disabled = true 能阻止用户通过点击这个按钮再次发起请求，
但不能阻止 JavaScript 代码直接调用 loadMockTickets()。



## 7. 手工测试结果

记录今天完成的页面检查，以及最终结果。

- 初次加载成功，页面显示“当前有2个工单”。
- 显示 JSON 中 ID 101、102 对应的两条工单。
- 重新加载时按钮禁用，加载完成后恢复。
- 添加工单后，数量从2变成3。
- 工单状态可以循环切换。
- 编辑并保存后，标题更新。
- 删除工单后，数量减少。
- 控制台没有影响业务运行的错误。

以上8项手工测试通过。
