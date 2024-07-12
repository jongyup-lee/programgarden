import sys
import os
import pandas as pd
import numpy as np

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *

class Kiwoom(QAxWidget):

    def __init__(self):
        super().__init__()

        ################## 변수 모음 ##################
        self.login_event_loop = None                        # 이벤트 루프 : 로그인
        self.detail_account_info_event_loop = QEventLoop()  # 이벤트 루프 : 예수금 상세 정보 요청
        self.calculator_event_loop = QEventLoop()           # 이벤트 루프 : 주식일봉차트조회요청 후 리턴되는 값으로 총 거래일 등의 정보를 활용하는 이벤트 루프
