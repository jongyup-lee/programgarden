import logging
import pandas as pd

logging.basicConfig(filename='../../logs/log_file_test.txt', level=logging.DEBUG, format="[ %(asctime)s | %(levelname)s ] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger()

def create_df():
    df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
    df.to_csv('./df_test.csv', index=False)
    logger.info("생성된 DataFrame의 shape : {}".format(df.shape))
    return df


logger.info("Dataframe 생성 완료")

        # self.logger.info("[info] 매도 주문 전달 성공")
        #