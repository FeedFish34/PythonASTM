import serial
import random
import re
import logging
import sqlite3

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"    # 日志格式化输出
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"                        # 日期格式
fp = logging.FileHandler('Debug.txt', encoding='utf-8')
fs = logging.StreamHandler()
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fp, fs])

def recv(serial):
    while True:
        data = serial.read_all()
        if data == '':
            continue
        else:
            break
        sleep(0.02)
    return data

if __name__ == '__main__':
    serial = serial.Serial('COM2', 9600, timeout=0.5)
    resMsg = ""
    resResult = ""
    if serial.isOpen() :
        print("open success")
    else :
        print("open failed")
    while True:
        data =recv(serial)
        if(data != b''):
            print(str(data))
            result = 'x04' in str(data)
            print(result)
            if(result):
                print("receive : ",data)
                logging.debug("接收：" + data.decode('utf-8'))
                EnqString = chr(int("05"))
                StxString = chr(int("02"))
                EtxString = chr(int("03"))
                EotString = chr(int("04"))
                print(data.decode('utf-8'))
                data = data.decode('utf-8')
                resMsg = re.findall(r'\b\d+\b', data)
                resMsg = str(resMsg).replace("['","").rstrip("']")
                resResult = str(random.randint(0,999));
                print(resMsg)
                sampId = str(resMsg)
                resMsg = EnqString + StxString + str(resMsg) + "-" + resResult + EtxString + EotString
                serial.write(bytearray(resMsg, encoding="utf-8"))  # 数据写回
                logging.debug("发送：" + resMsg)

                cx = sqlite3.connect("C:/Users/Administrator/PycharmProjects/ASTMSerial/LocalData.db")
                cu = cx.cursor()
                cu.execute("insert into ASTMData(SampleId,ResultData) values (?,?)", (sampId,resResult))
                cx.commit()

                resMsg = ""
                resResult = ""
            else:
                resMsg = data.decode('utf-8') + resMsg