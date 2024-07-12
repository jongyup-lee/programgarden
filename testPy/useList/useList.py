buy_history_list = []

ex = 50

if ex == 100:
    pass
elif ex < 100:
    buy_history_list.append('rk')
else:
    buy_history_list.append('sk')

print(buy_history_list)
buy_history_list.remove('rk')
print(buy_history_list)