import websockets
import json
import asyncio
import time
import yaml
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

#AES256 Decode
def aes_cbc_base64_dec(key, iv, cipher_text):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    return bytes.decode(unpad(cipher.decrypt(b64decode(cipher_text)),AES.block_size))


def stocksigningnotice(data, key, iv):
    menulist = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|주문조건|주식단축종목코드|체결수량|체결단가|주식체결시간|거부여부|체결여부|접수여부|지점번호|주문수량|계좌명|체결종목명|신용구분|신용대출일자|체결종목명40|주문가격"
    menustr1 = menulist.split('|')

    # AES256 처리 단계
    aes_dec_str = aes_cbc_base64_dec(key, iv, data)
    pValue = aes_dec_str.split('^')

    i = 0
    for menu in menustr1:
        print("%s  [%s]" % (menu, pValue[i]))
        i += 1

async def connect():
    # 웹 소켓에 접속.( 주석은 koreainvest test server for websocket)
    ## 시세데이터를 받기위한 데이터를 미리 할당해서 사용한다.
    with open('info.yml', encoding='UTF-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    
    g_appkey = data['APP_KEY']
    g_appsceret = data['APP_SECRET']
    
    stockcode = '005930'    # 테스트용 임시 종목 설정, 삼성전자
    htsid = '@1956198'    # 체결통보용 htsid 입력
    custtype = 'P'      # customer type, 개인:'P' 법인 'B'
    url = 'ws://ops.koreainvestment.com:31000'
    async with websockets.connect(url, ping_interval=None) as websocket:

        """" 주석처리는 더블쿼트 3개로 처리
        """
        while True:
            print("1.주식호가, 2.주식호가해제, 3.주식체결, 4.주식체결해제, 5.주식체결통보(고객), 6.주식체결통보해제(고객), 7.주식체결통보(모의), 8.주식체결통보해제(모의)")
            print("Input Command :")
            cmd = input()

            # 입력값 체크 step
            if cmd < '0' or cmd > '9':
                print("> Wrong Input Data", cmd)
                continue
            elif cmd == '0':
                print("Exit!!")
                break

            # 입력값에 따라 전송 데이터셋 구분 처리
            if cmd == '1':  # 주식호가 등록
                tr_id = 'H0STASP0'
                tr_type = '1'
            elif cmd == '2':  # 주식호가 등록해제
                tr_id = 'H0STASP0'
                tr_type = '2'
            elif cmd == '3':  # 주식체결 등록
                tr_id = 'H0STCNT0'
                tr_type = '1'
            elif cmd == '4':  # 주식체결 등록해제
                tr_id = 'H0STCNT0'
                tr_type = '2'
            elif cmd == '5':  # 주식체결통보 등록(고객용)
                tr_id = 'H0STCNI0' # 고객체결통보
                tr_type = '1'
            elif cmd == '6':  # 주식체결통보 등록해제(고객용)
                tr_id = 'H0STCNI0' # 고객체결통보
                tr_type = '2'
            elif cmd == '7':  # 주식체결통보 등록(모의)
                tr_id = 'H0STCNI9'  #테스트용 직원체결통보
                tr_type = '1'
            elif cmd == '8':  # 주식체결통보 등록해제(모의)
                tr_id = 'H0STCNI9'  # 테스트용 직원체결통보
                tr_type = '2'
            else:
                senddata = 'wrong inert data'

            # send json, 체결통보는 tr_key 입력항목이 상이하므로 분리를 한다.
            if cmd == '5' or cmd == '6' or cmd == '7' or cmd == '8':
                senddata = '{"header":{"appkey":"' + g_appkey + '","appsecret":"' + g_appsceret + '","personalseckey":"' + '","custtype":"'+custtype+'","tr_type":"' + tr_type + '","content-type":"utf-8"},"body":{"input":{"tr_id":"' + tr_id + '","tr_key":"' + htsid + '"}}}'
            else :
                senddata = '{"header":{"appkey":"' + g_appkey + '","appsecret":"' + g_appsceret + '","personalseckey":"' +  '","custtype":"'+custtype+'","tr_type":"' + tr_type + '","content-type":"utf-8"},"body":{"input":{"tr_id":"' + tr_id + '","tr_key":"' + stockcode + '"}}}'

            print('Input Command is :', senddata)

            await websocket.send(senddata)
            # 무한히 데이터가 오기만 기다린다.
            while True:
                data = await websocket.recv()
                print("Recev Command is :", data)
                if data[0] == '0' or data[0] == '1':  # 실시간 데이터일 경우
                    trid = jsonObject["header"]["tr_id"]

                    if data[0] == '0':
                        recvstr = data.split('|')  # 수신데이터가 실데이터 이전은 '|'로 나뉘어져있어 split
                        trid0 = recvstr[1]
                        if trid0 == "H0STASP0":  # 주식호가tr 일경우의 처리 단계
                            print("#### 주식호가 ####")
                           # stockhoka(recvstr[3])
                            time.sleep(1)

                        elif trid0 == "H0STCNT0":  # 주식체결 데이터 처리
                            print("#### 주식체결 ####")
                            data_cnt = int(recvstr[2])	# 체결데이터 개수
                           # stockspurchase(data_cnt, recvstr[3])

                    elif data[0] == '1':
                        recvstr = data.split('|')  # 수신데이터가 실데이터 이전은 '|'로 나뉘어져있어 split
                        trid0 = recvstr[1]
                        if trid0 == "H0STCNI0" or trid0 == "H0STCNI9":  # 주실체결 통보 처리
                            print("#### 주식체결통보 ####")
                            stocksigningnotice(recvstr[3], aes_key, aes_iv)
                            await websocket.send(senddata)

                    # clearConsole()
                    # break;
                else:
                    jsonObject = json.loads(data)
                    trid = jsonObject["header"]["tr_id"]

                    if trid != "PINGPONG":
                        rt_cd = jsonObject["body"]["rt_cd"]
                        if rt_cd == '1':    # 에러일 경우 처리
                            print("### ERROR RETURN CODE [ %s ] MSG [ %s ]" % (rt_cd, jsonObject["body"]["msg1"]))
                            break
                        elif rt_cd == '0':  # 정상일 경우 처리
                            print("### RETURN CODE [ %s ] MSG [ %s ]" % (rt_cd, jsonObject["body"]["msg1"]))
                            # 체결통보 처리를 위한 AES256 KEY, IV 처리 단계
                            if trid == "H0STCNI0" or trid == "H0STCNI9":
                                aes_key = jsonObject["body"]["output"]["key"]
                                aes_iv = jsonObject["body"]["output"]["iv"]
                                print("### TRID [%s] KEY[%s] IV[%s]" % (trid, aes_key, aes_iv))

                    elif trid == "PINGPONG":
                        print("### RECV [PINGPONG] [%s]" % (data))
                        await websocket.send(data)
                        print("### SEND [PINGPONG] [%s]" % (data))

asyncio.run(connect())