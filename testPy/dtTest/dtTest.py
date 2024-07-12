from datetime import datetime

now = datetime.now()

print("현재 : ", now)
print("현재 날짜 : ", now.date())
print("현재 시간 : ", now.time())
print("timestamp : ", now.timestamp())
print("년 : ", now.year)
print("월 : ", now.month)
print("일 : ", now.day)
print("시 : ", now.hour)
print("분 : ", now.minute)
print("초 : ", now.second)
print("마이크로초 : ", now.microsecond)
print("요일 : ", now.weekday())
print("문자열 변환 : ", now.strftime('%Y-%m-%d %H:%M:%S'))
print("년 연산 : ", now.year-1)

# Output
# 현재 :  2021-12-22 15:46:26.695840
# 현재 날짜 :  2021-12-22
# 현재 시간 :  15:46:26.695840
# timestamp :  1640155586.69584
# 년 :  2021
# 월 :  12
# 일 :  22
# 시 :  15
# 분 :  46
# 초 :  26
# 마이크로초 :  695840
# 요일 :  2
# 문자열 변환 :  2021-12-22 15:46:26