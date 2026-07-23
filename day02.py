print("=" * 30)
print("        项目报价计算器")
print("=" * 30)

project_name = input("请输入项目名称:")
customer_name = input("请输入客户名称：")
work_days = int(input("请输入预计工作天数:"))
daily_price = float(input("请输入每天的服务费用:"))
extra_cost = float(input("请输入额外的成本: "))
is_urgent = input("是否为加急项目?,请输入 是 或 否:")


service_cost = work_days * daily_price
urgent_fee = 0

if is_urgent == "是":
    urgent_fee = service_cost *0.2

total_price = service_cost + extra_cost + urgent_fee
average_daily_cost = total_price / work_days

print()
print("=" * 30)
print("     报价结果")
print("=" * 30)
print(f"客户名称：{customer_name}")
print(f"项目名称:{project_name}")
print(f"工作天数:{work_days}天")
print(f"每日费用:{daily_price:.2f}元")
print(f"服务费用:{service_cost:.2f}元")
print(f"额外成本{extra_cost:.2f}元")
print(f"加急费用:{urgent_fee:.2f}元")
print(f"平均每天总成本:{ average_daily_cost:.2f}元")
print("=" * 30)
print(f"项目总报价:{total_price:.2f}元")
print("=" * 30)