import sys
import os
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *
class Kiwoom(QAxWidget):

    def __init__(self):
        super().__init__()

        self.realType = RealType()

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
        ################## 변수 모음 끝 ##################


        ################## 함수 실행 ##################
        self.get_ocx_instance()
        self.event_slots()
        self.real_event_slots()

        self.signal_login_commConnect() # 로그인
        self.get_account_info() # 보유 계좌 조회
        self.detail_account_info() # 계좌에 대한 상세 정보 조회
        self.detail_account_mystock() # 보유 주식 조회
        self.not_concluded_account() # 실시간 미체결 종목 조회

        self.read_code() #  120일선 기준 필터링되어 저장된 txt파일에서 self.portfolio_stock_dict로 종목 이관하는 함수
        self.screen_number_setting() # 종목별 스크린번호 관리

        # 데이터를 받아와 조건에 맞는 종목을 선정하여 txt 파일로 저장한다. => 관심종목 추가 => 필요에 따라 수행하는 역할
        # self.calculator_fnc() # 주식 시장별 정보 조회

        ################## 함수 실행 끝 ##################


        ################## 장 시작/종료 및 실시간 정보 수집 시그널 ##################

        # 실시간 등록 - SetRealReg 요청에 대한 응답은 OnReceiveRealData
        print("real_event_slots() - 장시작/종료 실시간 요청")
        self.dynamicCall("SetRealReg(QString, QString, QString, QString", self.screen_start_stop_real, "", self.realType.REALTYPE['장시작시간']['장운영구분'],"0")

        # 종목 코드 등록
        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간']

            self.dynamicCall("SetRealReg(QString, QString, QString, QString", screen_num, code, fids, "1")
            print("실시간 등록 코드 : %s, 스크린번호 : %s, fid 번호 : %s" % (code, screen_num, fids))

        ################## 장 시작/종료 및 실시간 정보 수집 시그널 끝 ##################

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    # 이벤트 집합소
    # 서버에 요청 후 리턴 받는 응답을 한 곳에서 받아 처리
    def event_slots(self):
        #로그인 이벤트 응답 / errorCode.py에 코드별 상태값 정리 참고
        self.OnEventConnect.connect(self.login_slot) # 로그인 EventLoop
        #TR 이벤트 응답
        self.OnReceiveTrData.connect(self.trdata_slot)
        # msg 이벤트 응답
        self.OnReceiveMsg.connect(self.msg_slot)

    # 실시간 요청 컨드롤
    def real_event_slots(self):
        # 장시작/종료 실시간 응답 처리
        self.OnReceiveRealData.connect(self.realdata_slot)
        # 주문에 대한 이벤트 등록
        self.OnReceiveChejanData.connect(self.chejan_slot)

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()") # 키움 로그인을 위한 메서드 이름과 사용 방법 : dynamicCall이라는 메서드를 이용하여 호출

        self.login_event_loop = QEventLoop() # 로그인 EventLoop 설정
        self.login_event_loop.exec_() # 로그인 EventLoop 시작

    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_event_loop.exit() # 로그인 EventLoop 끝
    # 내 정보 가져오기
    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO")

        self.account_num = account_list.split(';')[0]
        print('[info] 계좌번호 : %s' % self.account_num)

    # 예수금 정보 가져오기
    def detail_account_info(self):
        # SetInputValue 서버 전송전 필요 데이터 입력
        # CommRqData 데이터 요청 실행
        print("detail_account_info() => 예수금 요청")    # 키움 예수금 정보 요청하기 위한 메서드 이름과 사용 방법 : dynamicCall이라는 메서드를 이용하여 호출
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "OPW00001", "0", self.screen_my_info)

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()

    def detail_account_mystock(self, sPrevNext="0"): # 계좌 평가 잔고 내역 요청
        print("detail_account_mystock() = > 계좌 평가 잔고 내역 요청")
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "OPW00018", sPrevNext, self.screen_my_info)

        if sPrevNext == "0" or sPrevNext == "":
            #self.detail_account_mystock_event_loop = QEventLoop()
            self.detail_account_info_event_loop.exec_()

    def not_concluded_account(self, sPrevNext="0"): # 미체결 종목 요청
        print("not_concluded_account() => 실시간미체결종목요청")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.dynamicCall("CommRqData(String, String, int, String)", "실시간미체결종목요청", "opt10075", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()


    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext): #
        '''
        TR 요청에 대한 응답 처리
        sScrNo : 스크린번호
        sRQName : 요청명 - 개발자 마음대로
        sTrCode : 요청 ID TR코드
        sRecordName :  사용안함
        sPrevNext : 다음 페이지가 있는지
        return :
        '''
        print("trdata_slot() => TR요청에 대한 응답")

        if sRQName == "예수금상세현황요청":
            print("sRQName :: 예수금상세현황요청")
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")
            print("[info] 예수금 %s" % deposit)

            ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")
            print("[info] 출금가능금액 %s" % ok_deposit)

            ##############################################################
            # 매수 가능 금액 조절 - 몰빵하는 것을 시스템 적으로 조정하는 기능 (차후 조정하면서 매매할 수 있음)
            ##############################################################
            self.use_money = int(deposit) * self.use_money_persent
            self.use_money = self.use_money / 4
            ##############################################################

            self.detail_account_info_event_loop.exit() # 예수금 상세 현황 요청 이벤트 루트 종료

        elif sRQName == "계좌평가잔고내역요청":
            print("sRQName :: 계좌평가잔고내역요청")
            # 총 매입 금액 / 총 수익률
            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)

            print("[info] 총매입금액 : %s" % total_buy_money_result)

            total_progit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")
            total_progit_loss_rate_result = float(total_progit_loss_rate)
            print("[info] 총수익률(%%) : %s" % total_progit_loss_rate_result)

            # 보유 종목 개수
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목번호")
                code = code.strip()[1:]

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매매가능수량")

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt += 1
            print("[info] 계좌에 가지고 있는 종목 : %s " % self.account_stock_dict)
            if sPrevNext == "":
                sPrevNext = "0"
            print("[info] 계좌 보유 종목에 대한 sPrevNext 값 : %s " % sPrevNext)
            print("[info] 계좌 보유 종목 페이별 보유 종목 수 : %s " % cnt)

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()


            #self.detail_account_mystock_event_loop.eixt() # 계좌 평가 잔고 내역 요청 이벤트 루트 종료

        elif sRQName == "실시간미체결종목요청":
            print("sRQName :: 실시간미체결종목요청")
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문상태")
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문구분")
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip("+").lstrip("-")
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dick:
                    pass
                else:
                    self.not_account_stock_dick[order_no] = {}

                nasd = self.not_account_stock_dick[order_no]

                nasd.update({"종목코드": code})
                nasd.update({"종목명": code_nm})
                nasd.update({"주문번호": order_no})
                nasd.update({"주문상태": order_status})
                nasd.update({"주문수량": order_quantity})
                nasd.update({"주문가격": order_price})
                nasd.update({"주문구분": order_gubun})
                nasd.update({"미체결수량": not_quantity})
                nasd.update({"체결량": ok_quantity})

                print("[info] 미체결 종목 : %s " % self.not_account_stock_dick[order_no])

            self.detail_account_info_event_loop.exit()

        elif sRQName == "주식일봉차트조회":
            print("sRQName :: 주식일봉차트조회")
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0,"종목코드")
            code = code.strip()

            # 해당 종목의 거래일 수 조회
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("[info] 종목의 데이터 일 수 %s: " % cnt)

            # 새로운 조건식을 구성하기 위한 요소들
            # 봉수 : cnt

            ########################################################################################################
            # 해당 종목의 모든 거래일 데이터를 받아와서 self.calcul_data에 저장
            ########################################################################################################
            for i in range(cnt):
                data = []
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"저가")

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
            print("주식 일봉 차트 조회 후 생성한 종목 리스트 : %s" %  self.calcul_data)
            ########################################################################################################
            # 해당 종목의 모든 거래일 데이터를 받아와서 self.calcul_data에 저장 끝
            ########################################################################################################

            if sPrevNext == "2":
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else: # sPrevNext가 0 또는 Null일 경우 - 조회된 거래일 데이터 수가 600개 미만일 경우
                pass_success = False #120일 이평선을 그릴만큼의 데이터가 있는지 체크

                ########################################################################################################
                # 120일 기준 검색식 - 관심종목/매매대상/본인스타일의 종목 선별 식
                ########################################################################################################
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                else:
                    #120일 이상 될 경우
                    total_price = 0
                    for value in self.calcul_data[:120]: # 리스트의 첫 번째 요소부터 120번째 요소까지를 포함하는 부분 리스트를 반환
                        total_price += int(value[1])

                    moving_average_price = total_price / 120 # 조회한 당일 기준 120일간의 평균가격 (기준일을 변경하지 않는 한 루프가 끝나는 순간까지 변하지 않음)


                    #오조회 기준일 저가 120일 평균 가격보다 높거나 같고 120일 평균 가격이 당일 고가보다 낮거나 같은지의 여부
                    bottom_price = False
                    check_price = None

                    # 조회 기준일 저가 120일 평균 가격보다 낮거나 같고 120일 평균 가격이 당일 고가보다 낮거나 같음
                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.calcul_data[0][6]):
                        bottom_price = True
                        check_price = int(self.calcul_data[0][6])


                    # 조회한 종목의 모든 거래일에 대한 데이터를 data에 담은 후 해당 종목의
                    # 조회일의 현재가가 120일 이평선보다 밑에 있는지 확인.
                    # 그렇게 확인을 하다가 일봉이 120-일 이평선보다 위에 있으면 계산 진행

                    prev_price = None # 조회한 종목 해당일의 저가
                    print("[info] bottom_price : %s " % bottom_price)
                    if bottom_price == True: # 조회 기준일 저가가 120일 평균 가격보다 낮거나 같고 120일 평균 가격이 당일 고가보다 낮거나 같음
                        print("======================================================================================================")
                        moving_average_price_prev = 0 # 조회한 종목의 조회일 기준 120일 평균 가격 (조회한 당일 이전의 날짜 기준 120일 평균 가격 - 2일전 기준 120평균, 3일전 기준 120 평균, 4일전 120 평균..... )
                        # 루프를 도는 동아 120일 평균 가격은 계속 변함
                        price_top_moving = False # 일 고가가 120일 평균 가격보다 낮거나 같고 조회일 수가 20일 보다 작은지 여부

                        idx = 1
                        while True: # 해당 종목의 당일부터 이전 나날의 120일 평균을 구하고 기준 가격과의 높낮이를 구하여
                            if len(self.calcul_data[idx:]) < 120: # 120일치가 있는지 계속 확인
                                break
                            total_price = 0
                            for value in self.calcul_data[idx:120+idx]:
                                total_price += int(value[1])
                            moving_average_price_prev = total_price / 120

                            # 조회 당일 고가가 120일 평균 가격보다 작거나 같고 조회일수가 20일 보다 작으면
                            if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20:
                                price_top_moving = False
                                break
                            # 조회 당일 저가가 120일 평균 가격 보다 높고 조회일 수가 20일 보다 크면
                            elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20:
                                price_top_moving = True
                                prev_price = int(self.calcul_data[idx][7]) # 해당일의 저가
                                break
                            idx += 1

                        # 해당 부분 이평선이 가장 최근 일자의 이평선 가격보다 낮은지 확인
                        if price_top_moving == True:
                            # 120일 평균선이 조회일 기준 120일 평균보다 크고
                            if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                pass_success = True

                #--------------------------------------------------------------------------------------------------------
                # 120일 기준 검색 조건에 부합하는 종목을 텍스트 파일로 저장함
                # 이후 결과물 어떤 방식으로 출력하고 사용할지 고민해야 함
                #--------------------------------------------------------------------------------------------------------
                print("pass_success : %s" % pass_success)
                if pass_success == True:
                    print("조건부 통과됨")
                    code_nm = self.dynamicCall("GetMasterCodeName(QString)", code) # 종목코드 1개의 종목 한글명을 반환한다.

                    f = open("D:/works/AutoTradePJT/python/progrmaGarden/pythonProject/files/condition_stock.txt", "a", encoding="utf8")
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()

                elif pass_success == False:
                    print("조건부 통과 못함")

                self.calcul_data.clear()
                self.calculator_event_loop.exit()
                ########################################################################################################
                # 120일 기준 검색식 끝
                ########################################################################################################

    def realdata_slot(self, sCode, sRealType, sRealData):
        print("realdata_slot() => 장시작/종료, 실시간 데이터 요청에 대한 응답 - %s " % sRealType)
        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)
            print("sRealType :: 장시작시간 - value : %s " % value)

            if value == '0':
                print("[info] 장시작 전")
            elif value == '3':
                print("[info] 장시작")
            elif value == '2':
                print("[info] 장 종료, 동시호가로 넘어감")
            elif value == '4':
                print("[info] 15시 30분 장종료")

                for code in self.portfolio_stock_dict.key():
                    self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code)

                QTest.qWait(5000)

                print("[info] 장종료 - 기존 데이터 삭제 및 신규 종목 등록 시작")
                self.file_delete()
                self.calculator_fnc()

                sys.exit()

        elif sRealType == "주식체결":  ##################

            print("sRealType :: 주식체결")
            # 체결시간 => HHMMSS
            a = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간'])
            b = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가'])
            b = abs(int(b))  # abs : 절대값
            c = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비'])
            c = abs(int(c))  # abs : 절대값
            d = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['등락율'])
            d = float(d)
            e = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가'])
            e = abs(int(e))
            f = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가'])
            f = abs(int(f))
            g = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['거래량'])
            g = abs(int(g))
            h = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래량'])
            h = abs(int(h))
            i = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['고가'])
            i = abs(int(i))
            j = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['시가'])
            j = abs(int(j))
            k = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['저가'])
            k = abs(int(k))

            if sCode not in self.portfolio_stock_dict:  # 체결된 종목이 나의 관심 종목에 저장되어 있지 않다면
                self.portfolio_stock_dict.update({sCode: {}})  # 추가한다.

            self.portfolio_stock_dict[sCode].update({'체결시간': a})
            self.portfolio_stock_dict[sCode].update({'현재가': b})
            self.portfolio_stock_dict[sCode].update({'전일대비': c})
            self.portfolio_stock_dict[sCode].update({'등락율': d})
            self.portfolio_stock_dict[sCode].update({'(최우선)매도호가': e})
            self.portfolio_stock_dict[sCode].update({'(최우선)매수호가': f})
            self.portfolio_stock_dict[sCode].update({'거래량': g})
            self.portfolio_stock_dict[sCode].update({'누적거래량': h})
            self.portfolio_stock_dict[sCode].update({'고가': i})
            self.portfolio_stock_dict[sCode].update({'시가': j})
            self.portfolio_stock_dict[sCode].update({'저가': k})

            ############################################################################################################
            ### 매매를 위한 조건
            ############################################################################################################
            # 1. 계좌 잔고 평가 내역에 있고 당일 실시간 잔고에 없어야 함  - 61강 2분 15초 이후
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
                print("%s %s" % ("[계좌 잔고 평가 내역에 있고 당일 실시간 잔고에 없음] 신규매도를 한다", sCode))

                asd = self.account_stock_dict[sCode]  # #계좌 평가 잔고 내역 리스트

                # 등락률
                meme_rate = (b - asd['매입가']) / asd['매입가'] * 100

                if asd['매매가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString",
                        ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                         sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                    if order_success == 0:
                        print("[info] 매도 주문 전달 성공")
                        del self.account_stock_dict[sCode]
                    else:
                        print("[info] 매도주문 전달 실패")

            elif sCode in self.jango_dict.keys():
                print("%s %s" % ("[당일 실시간 잔고 계좌에 존재] 신규매도를 한다", sCode))
                jd = self.jango_dict[sCode]
                meme_rate = (b - jd['매입단가']) / jd['매입단가'] * 100

                if jd['주문가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString",
                        ['신규매도', self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2, sCode, jd['주문가능수량'],
                         0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                    if order_success == 0:
                        self.logging.logger.debug("[info] 매도주문 전달 성공")
                    else:
                        self.logging.logger.debug("[info] 매도주문 전달 실패")

            elif d > 2.0 and sCode not in self.jango_dict.keys():
                print("%s %s" % ("[등락율이 2% 상회/실시간 잔고 계좌에 미존재] 신규매수를한다", sCode))
                result = (self.use_money * 0.1) / e
                quantity = int(result)

                order_success = self.dynamicCall(
                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString",
                    ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1, sCode, quantity,
                     e, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                if order_success == 0:
                    print("[info] 매수주문 전달 성공")
                else:
                    print("[info] 매수주문 전달 실패")

            # 미체결 종목
            # 루프 도중 미체결 리스트의 수량이 변경되어 오류가 발생하는 현상을 방지하기 위해 임의의 변수에 할당하여 루프 실행
            not_meme_list = list(self.not_account_stock_dick)
            for order_num in not_meme_list:
                code = self.not_account_stock_dick[order_num]["종목코드"]
                meme_price = self.not_account_stock_dick[order_num]["주문가격"]
                not_quantity = self.not_account_stock_dick[order_num]["미체결수량"]
                order_gubun = self.not_account_stock_dick[order_num]['주문구분']

                # 매수 취소
                if order_gubun == "신규매수" and not_quantity > 0 and e > meme_price:
                    print("%s %s", ("매수취소한다.", sCode))
                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString",
                        ["매수취소", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 3, code, 0, 0,
                         self.realType.SENDTYPE['거래구분']['지정가'], order_num])

                    if order_success == 0:
                        print("[info] 매수 취소 전달 성공")
                    else:
                        print("[info] 매수 취소 전달 실패")


                elif not_quantity == 0:
                    del self.not_account_stock_dick[order_num]



    def chejan_slot(self, sGubun, nItemCnt, sFidLit):
        print("chejan_slot() => 나의 매매 주문 요청에 대한 응답")
        intGubun = int(sGubun)
        if intGubun == 0:
            print("[info] 주문체결")
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()
            origin_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['원주문번호'])
            order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문번호'])
            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문상태'])
            order_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문수량'])
            order_quan = int(order_quan)
            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문가격'])
            order_price = int(order_price)
            not_chegual_qaun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['미체결수량'])
            not_chegual_qaun = int(not_chegual_qaun)
            order_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문구분'])
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
            chegual_time_str = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간'])
            chegual_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가'])
            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price = int(chegual_price)

            chegual_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량'])
            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity = int(chegual_quantity)

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['현재가'])
            current_price = abs(int(current_price))

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            # 새로 들어온  주문이면 주문번호 할당
            if order_number not in self.not_account_stock_dick.keys():
                self.not_account_stock_dick.update({order_number: {}})

            self.not_account_stock_dick[order_number].update({"종목코드": sCode})
            self.not_account_stock_dick[order_number].update({"주문번호": order_number})
            self.not_account_stock_dick[order_number].update({"종목명": stock_name})
            self.not_account_stock_dick[order_number].update({"주문상태": order_status})
            self.not_account_stock_dick[order_number].update({"주문수량": order_quan})
            self.not_account_stock_dick[order_number].update({"주문가격": order_price})
            self.not_account_stock_dick[order_number].update({"미체결수량": not_chegual_qaun})
            self.not_account_stock_dick[order_number].update({"원주문번호": origin_number})
            self.not_account_stock_dick[order_number].update({"주문구분": order_gubun})
            self.not_account_stock_dick[order_number].update({"주문/체결시간": chegual_time_str})
            self.not_account_stock_dick[order_number].update({"체결가": chegual_price})
            self.not_account_stock_dick[order_number].update({"체결량": chegual_quantity})
            self.not_account_stock_dick[order_number].update({"현재가": current_price})
            self.not_account_stock_dick[order_number].update({"(최우선)매도호가": first_sell_price})
            self.not_account_stock_dick[order_number].update({"(최우선)매수호가": first_buy_price})

        elif intGubun == 1:
            print("[info] 잔고")
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()
            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['현재가'])
            current_price = abs(int(current_price))
            stock_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)
            like_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)
            buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))
            total_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['총매입가'])
            total_buy_price = int(total_buy_price)
            meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]
            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))
            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode: {}})

            self.jango_dict[sCode].update({"현재가": current_price})
            self.jango_dict[sCode].update({"종목코드": sCode})
            self.jango_dict[sCode].update({"종목명": stock_name})
            self.jango_dict[sCode].update({"보유수량": stock_quan})
            self.jango_dict[sCode].update({"주문가능수량": like_quan})
            self.jango_dict[sCode].update({"매입단가": buy_price})
            self.jango_dict[sCode].update({"총매입가": total_buy_price})
            self.jango_dict[sCode].update({"매도매수구분": meme_gubun})
            self.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})

            if stock_quan == 0:
                del self.jango_dict[sCode]
                # 해당 종목에 대해 실시간 데이터 수신 대기 상태 해제
                self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[sCode]['스크린번호'], sCode)

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

    def read_code(self):
        if os.path.exists("files/condition_stock.txt"):
            f = open("files/condition_stock.txt", "r", encoding="utf8")

            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split("\t")

                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = int(ls[2].split("\n")[0])
                    stock_price = abs(stock_price)

                    self.portfolio_stock_dict.update({stock_code:{"종목명":stock_name, "현재가":stock_price}})
            f.close()

    def screen_number_setting(self):
        # 각 dict에 겹치는 종목을 필터링한다.
        screen_overwrite = []

        #계좌평가잔고내역에 있는 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #미체결에 있는 종목들
        for order_number in self.not_account_stock_dick.keys():
            code = self.not_account_stock_dick[order_number]['종목코드']
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #포트폴리오에 담겨있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #스크린 번호 할당
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code: {"스크린번호":str(self.screen_real_stock), "주문용스크린번호": str(self.screen_meme_stock)}})

            cnt += 1

    # 송수신 메시지 set
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("msg_slot() => 메시지 요청에 대한 응답 / 스크린 : %s, 요청이름 : %s, tr코드 : %s --- %s" % (sScrNo, sRQName, sTrCode, msg))

    # 파일 삭제
    def file_delete(self):
        if os.path.isfile("files/condition_stock.txt"):
            os.remove("files/condition_stock.txt")

