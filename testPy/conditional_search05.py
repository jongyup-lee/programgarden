# 05.주가비교 : [일]1봉전 종가 < 0봉전 종가
# 1봉 전의 종가와 0봉 전의 종가를 가져오는 함수
def check_condition(closing_prices):
    if len(closing_prices) < 2:
        print("봉의 개수가 부족합니다.")
        return

    one_candle_ago = closing_prices[-2]  # 1봉 전의 종가
    zero_candle_ago = closing_prices[-1]  # 0봉 전의 종가

    if one_candle_ago < zero_candle_ago:
        print("1봉 전 종가가 0봉 전 종가보다 낮습니다.")
    else:
        print("1봉 전 종가가 0봉 전 종가보다 높거나 같습니다.")


# 함수 호출
closing_prices = [1000, 1050, 1020, 990, 980, 1005, 1010]
check_condition(closing_prices)