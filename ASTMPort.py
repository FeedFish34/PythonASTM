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
List = []


def do_checksum(source_string):
    """  Verify the packet integritity """
    sum = 0
    max_count = 3
    count = 0
    while count < max_count:
        val = ord(source_string[count + 1]) * 256 + ord(source_string[count])
        sum = sum + val
        sum = sum & 0xffffffff
        count = count + 2
    if max_count < len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    print(answer)
    return answer


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
            print(str(resMsg))
            result = 'x04' in str(data)
            print(result)
            if(result):
                print("receive : ",data)
                logging.debug("接收数据：" + data.decode('utf-8'))
                EnqString = chr(int("05"))
                StxString = chr(int("02"))
                EtxString = chr(int("03"))
                EotString = chr(int("04"))
                print(data.decode('utf-8'))
                data = data.decode('utf-8')
                resMsg = data + resMsg
                resMsg = re.findall(r'\b\d+\b', resMsg.replace(resMsg.split(chr(int("03")))[1],""))
                resMsg = str(resMsg).replace("['","").rstrip("']")
                resResult = str(random.randint(0,999));
                print("处理之后的样本号"+resMsg)
                sampId = str(resMsg)
                List.append(EnqString)
                List.append(StxString + str(resMsg) + EtxString + str(do_checksum(StxString + str(resMsg) + EtxString)))
                List.append(StxString + resResult + EtxString + str(do_checksum(StxString + resResult + EtxString)))
                List.append(EotString)
                #resMsg = EnqString + StxString + str(resMsg) + "-" + resResult + EtxString + EotString
                logging.debug("发送数据：" + List[0])
                serial.write(bytes(List[0].encode('utf-8'))) # 数据写回
                List.pop(0)

                cx = sqlite3.connect("C:/Users/Administrator/PycharmProjects/ASTMSerial/LocalData.db")
                cu = cx.cursor()
                cu.execute("insert into ASTMData(SampleId,ResultData) values (?,?)", (sampId,resResult))
                cx.commit()

                resMsg = ""
                resResult = ""
            else:
                for s in data:
                    if(s == 6 and len(List) > 0):
                        logging.debug("发送数据：" + List[0])
                        serial.write(bytes(List[0].encode('utf-8')))  # 数据写回
                        List.pop(0)
                    elif(s == 5 or s == 2):
                        logging.debug("发送6：" + chr(int("06")))
                        serial.write(bytearray(chr(int("06")), encoding="utf-8"))  # 数据写回
                    elif (s == 3):
                        lastNum = data.decode('utf-8').split(chr(int("03")))[1]
                        print(lastNum)
                        source_string = data.decode('utf-8').replace(lastNum,"")
                        logging.debug("校验数据：" + source_string)
                        checkcode = do_checksum(source_string)
                        print(checkcode)
                        if(str(lastNum) == str(checkcode)):
                            logging.debug("发送63：" + chr(int("06")))
                            serial.write(bytearray(chr(int("06")), encoding="utf-8"))  # 数据写回
                        else:
                            logging.debug("发送21：" + chr(int("21")))
                            serial.write(bytearray(chr(int("21")), encoding="utf-8"))  # 数据写回
                            resMsg = ""
                            continue
                if(data[0] == 6):
                     print("只接收到ACK")
                     logging.debug("接收6：" + data.decode('utf-8'))
                else:
                    resMsg = data.decode('utf-8') + resMsg