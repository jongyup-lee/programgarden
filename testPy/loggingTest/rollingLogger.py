import logging
from logging.handlers import TimedRotatingFileHandler
import os
import datetime

# 로그 디렉토리 설정
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 로거 생성
logger = logging.getLogger("example_logger")
logger.setLevel(logging.DEBUG)

# 현재 날짜를 파일명에 추가
today = datetime.date.today().strftime("%Y-%m-%d")
filename = os.path.join(log_dir, f'example_{today}.log')

# TimedRotatingFileHandler를 사용하여 일별 로그 파일 설정
handler = TimedRotatingFileHandler(filename=filename, when='midnight', interval=1, backupCount=5)
handler.setLevel(logging.DEBUG)

# 로그 기록 포맷 설정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 핸들러를 로거에 추가
logger.addHandler(handler)

# 로그 메시지 기록
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')
