meme_rate = (b - asd['매입가']) / asd['매입가'] * 100
bop_rate = (b - i) / i * 100
# if meme_rate > 5 and bop_rate < -1:


print("보유주O/잔고주X-매매가능수량 : %s | meme_rate : %s" % (asd['매매가능수량'], meme_rate))
if asd['매매가능수량'] > 0:
    if (meme_rate > 5 and bop_rate < -1) or meme_rate < -1:
        order_success = self.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString",
            ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
             sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

        if order_success == 0:
            self.logger.info("[info] 매도 주문 전달 성공")
            print("[info] 매도 주문 전달 성공")
            del self.account_stock_dict[sCode]
        else:
            self.logger.info("[info] 매도주문 전달 실패")
            # print("[info] 매도주문 전달 실패")