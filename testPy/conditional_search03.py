
# 0일전 종가가 1000이상 50000 이하
def check_closing_price(closing_price):
    """
    종가가 1000 이상이고 50000 이하인지를 확인하는 함수

    :param closing_price: 종가
    :return: 조건을 만족하는지 여부 (True 또는 False)
    """
    if 1000 <= closing_price <= 50000:
        return True
    else:
        return False

# 함수 테스트(매개변수 : 하루 전 종가)
if check_closing_price(closing_price_today):
    print("조건을 만족하는 주식입니다.")
else:
    print("조건을 만족하는 주식이 아닙니다.")
