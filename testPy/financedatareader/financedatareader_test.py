from openpyxl import Workbook
import os


class ExcelManager:
    def __init__(self):
        self.buy_history_list = []
        self.add_buy_history_list = []
        self.partial_sale_list = []

    def save_to_excel(self, data_list, file_name):
        # 디렉토리 생성
        directory = 'historyXlsx'
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 엑셀 파일 경로
        file_path = os.path.join(directory, file_name + '.xlsx')

        # 새로운 Workbook 생성
        workbook = Workbook()

        # 첫 번째 시트 선택
        sheet = workbook.active

        # 컬럼명 설정
        sheet['A1'] = 'Index'
        sheet['B1'] = file_name

        # 데이터 추가
        for index, data in enumerate(data_list):
            print('index:%s'%index)
            sheet[f'A{index + 2}'] = index
            sheet[f'B{index + 2}'] = data

        # 변경 사항을 저장
        workbook.save(file_path)

        print(f"{file_name}.xlsx에 데이터가 성공적으로 저장되었습니다.")

    def save_all_to_excel(self):
        self.save_to_excel(self.buy_history_list, 'buyHistory')
        self.save_to_excel(self.add_buy_history_list, 'addBuyHistory')
        self.save_to_excel(self.partial_sale_list, 'partialSalelist')


# 테스트를 위한 예시 데이터
manager = ExcelManager()
manager.buy_history_list = ['000240', '000241', '000242']
manager.add_buy_history_list = ['000243', '000244', '000245']
manager.partial_sale_list = ['000246', '000247', '000248']

# 모든 데이터를 엑셀에 저장
manager.save_all_to_excel()
