import sys
import os
import pandas as pd
import numpy as np
# FinanceDataReader를 fdr이라는 별칭으로 사용 선언
import FinanceDataReader as fdr

from datetime import datetime
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *
from PyQt5.QtWidgets import *

app = QApplication(sys.argv)
app.exec_()
class MakeTxtFile(QAxWidget):

    def __init__(self):
        super().__init__()

        ################## 변수 모음 ##################
        self.login_event_loop = None # 이벤트 루프 : 로그인
        self.detail_account_info_event_loop = QEventLoop() # 이벤트 루프 : 예수금 상세 정보 요청
        self.calculator_event_loop = QEventLoop()

        self.account_num = None # 보유 계좌번호
        self.use_money = 0
        self.use_money_persent = 0.5

        # 스크린 번호
        self.screen_my_info = "2000"
        self.screen_calculation_stock = "4000"
        self.screen_real_stock = "5000" # 종목별 할당할 스크린 번호
        self.screen_meme_stock = "6000" # 종목별 할당할 주문용 스크린 번호
        self.screen_start_stop_real = "1000" # 개장, 폐장 여부에 대한 실시간 확인용 스크린 번호

        self.calcul_data = [] #종목별 일봉 데이터 저장 리스트
        self.account_stock_dict = {} # 보유하고 있는 종목 저장 딕셔너리
        self.not_account_stock_dick = {} # 미체결 주문 종목들의 집합
        self.portfolio_stock_dict = {} # 120일선 기준 필터링되어 txt파일에서 불러와 관심종목으로 저장할 딕셔너리
        self.jango_dict = {} # 당일 실시간 계좌 잔고 현황

        # sideBell의 조건검색을 위한 변수모음
        self.gValueList = [] # 1번, 평균거래량을 구하기 위한 거래량 축적 리스트
        self.cci_low_data = {} # 종목별 cci를 구하기 위한 딕셔너리
        self.gCurrentList = [] # 2번, 5번 종가를 활용하기 위한 종가 리스트
        self.gCurrent = None # 3번 종가의 범의 확인을 위한 종가
        self.gStrength = None # 4번 체결강도
        self.gCapitalization = None # 6번 시가총액
        self.duringDays = 100
        self.gPass_success = False
        self.moving20_average_price = None
        ################## 변수 모음 끝 ##################


        ################## 함수 실행 ##################
        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect() # 로그인
        self.screen_number_setting() # 종목별 스크린번호 관리

        # 임시 실행 : 데이터를 받아와 조건에 맞는 종목을 선정하여 txt 파일로 저장한다. => 관심종목 추가 => 필요에 따라 수행하는 역할
        # self.file_delete()
        self.calculator_fnc() # 주식 시장별 정보 조회 후 txt파일로 로컬에 저장

        ################## 함수 실행 끝 ##################

    def signal_login_commConnect(self):

        self.dynamicCall("CommConnect()") # 키움 로그인을 위한 메서드 이름과 사용 방법 : dynamicCall이라는 메서드를 이용하여 호출

        self.login_event_loop = QEventLoop() # 로그인 EventLoop 설정
        self.login_event_loop.exec_() # 로그인 EventLoop 시작

    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_event_loop.exit() # 로그인 EventLoop 끝

    def event_slots(self):
        # 로그인 이벤트 응답 / errorCode.py에 코드별 상태값 정리 참고
        self.OnEventConnect.connect(self.login_slot)  # 로그인 EventLoop
        # TR 이벤트 응답
        self.OnReceiveTrData.connect(self.trdata_slot)

        ################## 장 시작/종료 및 실시간 정보 수집 시그널 끝 ##################
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext): #
        if sRQName == "주식일봉차트조회":
            print("[trdata_slot] sRQName :: 주식일봉차트조회")
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("[info] %s 종목" % code)

            # 해당 종목의 거래일 수 조회
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            ########################################################################################################
            # 해당 종목의 모든 거래일 데이터를 받아와서 self.calcul_data에 저장
            ########################################################################################################
            for i in range(cnt):
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())

                # print("조회한 종목 %s일의 일 데이터(data) 리스트 내용 : %s" % (i, self.calcul_data))
                # ['', '316', '376190', '119', '20190326', '310', '323', '310', '']
                #     현재가 ,  거래량  ,거래대금,    일자   ,  시가,   고가,   저가
                # 0일부터 총 조회 일수까지 루프
            ########################################################################################################
            # 해당 종목의 모든 거래일 데이터를 받아와서 self.calcul_data에 저장 끝
            ########################################################################################################

            if sPrevNext == "2":
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else:  # sPrevNext가 0 또는 Null일 경우 - 조회된 거래일 데이터 수가 600개 미만일 경우
                print("[info] 종목의 데이터 일 수 %s: " % cnt)
                pass_success = False  # 120일 이평선을 그릴만큼의 데이터가 있는지 체크

                ########################################################################################################
                # 120일 기준 검색식 - 관심종목/매매대상/본인스타일의 종목 선별 식
                #
                # 2024년 02월 13일 프로그램 동산에서 강의한 pass_success 이 True가 되는 조건식을 통으로 주석처리 합니다.
                #
                ########################################################################################################
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                    self.gPass_success = False
                else:
                    for value in self.calcul_data[:60]:
                        self.gValueList.append(value[2])

                    flag_conditional_search01 = self.conditional_search01(self.gValueList)
                    print("-------------------------------------01. %s" % flag_conditional_search01)

                    # 02. 기간내 등락봉수 : [일]0봉전 100봉이내 1봉 상승 발생 : 종가리스트 필요
                    for value in self.calcul_data[:100]:
                        self.gCurrentList.append(value[1])

                    flag_conditional_search02 = self.conditional_search02(self.gCurrentList)
                    print("-------------------------------------02. %s" % flag_conditional_search02)

                    # 03. 0일전 종가가 1000이상 50000 이하
                    flag_conditional_search03 = self.conditional_search03(self.calcul_data[cnt][1])
                    print("-------------------------------------03. %s" % flag_conditional_search03)

                    # 04. 체결강도 100.0이상 1000.0이하 => 이 조건은 매수 조건에서 구현
                    # 05.주가비교 : [일]1봉전 종가 < 0봉전 종가
                    flag_conditional_search05 = self.conditional_search05(self.calcul_data[cnt][1],
                                                                          self.calcul_data[cnt - 1][1])
                    print("-------------------------------------05. %s" % flag_conditional_search05)
                    print("-------------------------------------semi-final. %s" % self.gPass_success)
                    # 06. 시가총액“ 현재가기준 100십억원 이상 =>  이 조건은 매수 조건에서 구현

                    if flag_conditional_search01 == True and flag_conditional_search02 == True and flag_conditional_search03 == True and flag_conditional_search05 == True:
                        self.gPass_success = True
                        print("-------------------------------------final. %s" % self.gPass_success)
                    else:
                        self.gPass_success = False

                # if pass_success == True:
                if self.gPass_success == True:
                    print("조건부 통과됨")
                    ########################################################################################################
                    # 해당 종목의 모든 거래일 데이터를 받아와서 self.calcul_data에 저장
                    ########################################################################################################
                    code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)  # 종목코드 1개의 종목 한글명을 반환한다.

                    f = open("files/condition_stock.txt", "a", encoding="utf8")
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()
                    self.gPass_success = False

                elif pass_success == False:
                    print("조건부 통과 못함")

                self.calcul_data.clear()
                self.calculator_event_loop.exit()
                ########################################################################################################
                # 120일 기준 검색식 끝
                #
                # 2024년 02월 13일 프로그램 동산에서 강의한 pass_success 이 True가 되는 조건식을 통으로 주석처리 합니다. - 끝
                #
                ########################################################################################################

    # 종목코드 가져오는 함수
    def get_code_list_by_market(self, market_code):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1]

        return code_list

    def calculator_fnc(self):
        code_list = self.get_code_list_by_market("10")

        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock) # self.screen_calculation_stock : 스크린번호
            # DisconnectRealData : 해당하는 스크린 번호에 대한 실시간 데이터 받기를 해제한다.

            self.day_kiwoom_db(code=code)

    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        QTest.qWait(3600) # 정보 요청을 3.6초 딜레이를 준다

        self.dynamicCall("SetInputValue(QString, QString", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInpuValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)
        self.calculator_event_loop.exec_()

    ############################################################################################################
    # 조건 검색
    ############################################################################################################
    # 1. [일]0봉전 5봉 평균거래량이 10000이상 999999999이하
    # 입력데이터 : 거래량(list)
    # 리턴데이터 : boolean
    def conditional_search01(self, data):
        rtn_flag = False
        # 오늘을 포함하여 5일간의 거래량 데이터 추출
        if len(data) > 5:
            recent_volume = data[-5:]
            # 평균 거래량 계산
            total = 0
            for value in recent_volume[:len(recent_volume)]:
                total += int(value)


            avg_volume = total / len(recent_volume)
            if avg_volume > 10000 and avg_volume <999999999:
                rtn_flag = True

        return rtn_flag

    # 2. 기간내 등락봉수 : [일]0봉전 100봉이내 1봉 상승 발생
    # 입력데이터 : 종가(list)
    # 리턴데이터 : boolean
    def conditional_search02(self, data):
        tmp_stock = []
        rtn_flag = False
        if len(data) > 100:
            for i in range(len(data) - self.duringDays, len(data) - 1):  # 최근 n일 동안의 데이터에 대해서만 반복
                if data[i] > data[i - 1]:  # 현재 시점에서 직전 봉의 가격과 비교하여 상승한 경우
                    tmp_stock.append((i, data[i]))
            if len(tmp_stock) > 0:
                rtn_flag = True

        return rtn_flag

    # 3. 주가범위: 0일전 종가가 1000이상 50000 이하
    # 입력데이터 : 종가(int)
    # 리턴데이터 : boolean
    def conditional_search03(self, data):
        rtn_flag = False
        if 1000 <= int(data) <= 50000:
            rtn_flag = True

        return rtn_flag


    # 4. 체결강도 100.0이상 1000.0이하
    def conditional_search04(self, data):
        rtn_flag = False
        if 100 <= data >= 1000:
            rtn_flag = True

        return rtn_flag


    # 5. 주가비교 : [일]1봉전 종가 < 0봉전 종가
    def conditional_search05(self, data0, data1):
        rtn_flag = False

        if data1 < data0:
            rtn_flag = True

        return rtn_flag

    # 6. 시가총액“ 현재가기준 100십억원 이상
    def conditional_search06(self, data):
        rtn_flag = False
        if 1000000000000 <= data:
            rtn_flag = True

        return rtn_flag

    # 7. 총부채증감율 : 최근결산기의 전년대비 증감률 200% 이하
    def conditional_search07(self):
        pass

    # 8. 유보율 : 최근결산 500% 이상
    def conditional_search08(self):
        pass

if __name__ == "__main__":
    MakeTxtFile()