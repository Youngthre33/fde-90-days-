from time import sleep

import httpx

url = "https://42.192.114.83/health"
max_attempts = 3

for attempt in range(1, max_attempts + 1):
    print("第", attempt, "次请求")
    try:
        response = httpx.get(url, timeout=5)
        print("状态码：", response.status_code)
        print("响应正文：", response.text)
        break
    except httpx.TimeoutException:
        print("请求超时：本次网络等待超过了设置的限制。")
        if attempt == max_attempts:
            print("已达到最大尝试次数，本次检查失败。")
            break
        print("等待1秒后重试。")
        sleep(1)

print("本次检查结束。")
