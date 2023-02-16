#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import hmac
from hashlib import sha1
import time
from paho.mqtt.client import MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, MQTT_LOG_DEBUG
from paho.mqtt import client as mqtt
import json
import random
import threading

import modbus_tk
from modbus_tk import modbus_rtu
import serial

'''
# 原文链接 - 我的博客，更多内容可查看我的主页。
# MQTT接入阿里云物联网平台Demo，使用一机一密的方式
# 运行时，需安装 paho.mqtt
# 在PyCharm 的 File - Settings - Projectxxx - Python Interpreter 中，搜索并安装 paho.mqtt
# 需要根据个人设备进行改动的仅5项：productKey、deviceName、deviceSecret、regionId、modelName
'''

# 设备证书（ProductKey、DeviceName和DeviceSecret），三元组
productKey = 'a15W5phbSgk'#'hy8e3eWIuXy'#'hy8eyCKm0OF'#'a15W5phbSgk'#'a11VSfKfx4g'  'hy8eyCKm0OF'#  
deviceName = 'kongzhi'#one_floor'#'one_floo'#'kongzhi'#'wangguan'   'one_floo'#
deviceSecret = '42da9526aa112ed3a833f5dc6a9589f4'#'1f89fbe95ec5720638ab360fdb046cb0'#'d639116a928b27fb9a4e7efa2bb6039b'#'42da9526aa112ed3a833f5dc6a9589f4'#'15fe65a8e20e65fb3f6173285ea6acee'   'd639116a928b27fb9a4e7efa2bb6039b'#

# ClientId Username和 Password 签名模式下的设置方法，参考文档 https://help.aliyun.com/document_detail/73742.html?spm=a2c4g.11186623.6.614.c92e3d45d80aqG
# MQTT - 合成connect报文中使用的 ClientID、Username、Password
mqttClientId = deviceName + '|securemode=3,signmethod=hmacsha1|'
mqttUsername = deviceName + '&' + productKey
content = 'clientId' + deviceName + 'deviceName' + deviceName + 'productKey' + productKey
mqttPassword = hmac.new(deviceSecret.encode(), content.encode(), sha1).hexdigest()

# 接入的服务器地址
regionId = 'cn-shanghai'



# MQTT 接入点域名
brokerUrl = productKey + '.iot-as-mqtt.' + regionId + '.aliyuncs.com'

# Topic，post，客户端向服务器上报消息
topic_post = '/sys/' + productKey + '/' + deviceName + '/thing/event/property/post'
# Topic，set，服务器向客户端下发消息
topic_set = '/sys/' + productKey + '/' + deviceName + '/thing/service/property/set'

# 物模型名称的前缀（去除后缀的数字）
modelName = 'onoff_'


master = modbus_rtu.RtuMaster(serial.Serial(port='/dev/ttyUSB0',
                                                    baudrate=9600,
                                                    bytesize=8,
                                                    parity='N',
                                                    stopbits=1))
master.set_timeout(5.0)
master.set_verbose(True)




# 下发的设置报文示例：{"method":"thing.service.property.set","id":"1227667605","params":{"PowerSwitch_1":1},"version":"1.0.0"}
# json合成上报开关状态的报文
def json_switch_set(sswit, status):
    switch_info = {}
    switch_data = json.loads(json.dumps(switch_info))
    switch_data['method'] = '/thing/event/property/post'
    switch_data['id'] = random.randint(100000000,999999999) # 随机数即可，用于让服务器区分开报文
    switch_status = {sswit : status}
    switch_data['params'] = switch_status
    return json.dumps(switch_data, ensure_ascii=False)

# 开关的状态，0/1
onoff = 0

# 建立mqtt连接对象
client = mqtt.Client(mqttClientId, protocol=mqtt.MQTTv311, clean_session=True)

def on_log(client, userdata, level, buf):
    if level == MQTT_LOG_INFO:
        head = 'INFO'
    elif level == MQTT_LOG_NOTICE:
        head = 'NOTICE'
    elif level == MQTT_LOG_WARNING:
        head = 'WARN'
    elif level == MQTT_LOG_ERR:
        head = 'ERR'
    elif level == MQTT_LOG_DEBUG:
        head = 'DEBUG'
    else:
        head = level
    #print('%s: %s' % (head, buf))
# MQTT成功连接到服务器的回调处理函数
def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    # 与MQTT服务器连接成功，之后订阅主题
    client.subscribe(topic_post, qos=0)
    client.subscribe(topic_set, qos=0)
    # 向服务器发布测试消息
    client.publish(topic_post, payload='test msg', qos=0)
# MQTT接收到服务器消息的回调处理函数
def on_message(client, userdata, msg):

    global ss1 
    print(str(msg.payload))  #'recv:', msg.topic + ' ' +
    xdata= (str(msg.payload))
     
    if (xdata.rfind('method')==2):
        if (xdata.rfind('TargetTemperature01')!=-1): #目标温度1
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=1,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        elif (xdata.rfind('TargetTemperature02')!=-1): #目标温度2
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=2,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
           
        elif (xdata.rfind('TargetTemperature03')!=-1): #目标温度3
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=3,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)  
           
        elif (xdata.rfind('TargetTemperature04')!=-1): #目标温度4
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=4,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)

        
        elif (xdata.rfind('TargetTemperature05')!=-1): #目标温度5
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=5,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        elif (xdata.rfind('TargetTemperature06')!=-1): #目标温度6
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=6,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('TargetTemperature07')!=-1): #目标温度7
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=7,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('TargetTemperature08')!=-1): #目标温度8
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=8,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('TargetTemperature09')!=-1): #目标温度9
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=9,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('TargetTemperature10')!=-1): #目标温度10
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=10,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('TargetTemperature11')!=-1): #目标温度11
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=11,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('TargetTemperature12')!=-1): #目标温度12
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=12,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('TargetTemperature13')!=-1): #目标温度13
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=13,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        
        elif (xdata.rfind('TargetTemperature14')!=-1): #目标温度14
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=14,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        elif (xdata.rfind('TargetTemperature17')!=-1): #目标温度17
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=17,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        elif (xdata.rfind('TargetTemperature18')!=-1): #目标温度18
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=18,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        
        elif (xdata.rfind('TargetTemperature20')!=-1): #目标温度20
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=20,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('TargetTemperature21')!=-1): #目标温度21
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=21,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('TargetTemperature24')!=-1): #目标温度24
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=24,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('TargetTemperature25')!=-1): #目标温度25
           xdata= xdata[:-20]
           ss1=xdata.index('"Target')
           ss1=xdata[ss1:]
           ssname=ss1[:21]
           ssv=ss1[22:]
           try:

               read = master.execute(slave=25,
                             function_code=0x06,
                             starting_address=0x01,
                             output_value=int(ssv)*10)

               print(read)

           except Exception as exc:
               print(str(exc))
           ssname=json.loads(ssname)
           ssv1=json.loads(ssv)
           switchPost = json_switch_set(ssname,ssv1)
           client.publish(topic_post, payload=switchPost, qos=0)
        
        

        elif (xdata.rfind('VehACSwitch01')!=-1):  #空调开关
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=1,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)    
           
        elif (xdata.rfind('VehACSwitch02')!=-1):  #空调开关2
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=2,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('VehACSwitch03')!=-1):  #空调开关3
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=3,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('VehACSwitch04')!=-1):  #空调开关4
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=4,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('VehACSwitch05')!=-1):  #空调开关5
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=5,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        elif (xdata.rfind('VehACSwitch06')!=-1):  #空调开关6
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=6,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('VehACSwitch07')!=-1):  #空调开关7
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=7,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('VehACSwitch08')!=-1):  #空调开关8
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=8,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('VehACSwitch09')!=-1):  #空调开关9
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=9,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('VehACSwitch10')!=-1):  #空调开关10
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=10,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        elif (xdata.rfind('VehACSwitch11')!=-1):  #空调开关11
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=11,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
          
        elif (xdata.rfind('VehACSwitch12')!=-1):  #空调开关12
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=12,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)

        
        elif (xdata.rfind('VehACSwitch13')!=-1):  #空调开关13
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=13,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)

        elif (xdata.rfind('VehACSwitch14')!=-1):  #空调开关14
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=14,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))
            
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
            
            
        elif (xdata.rfind('VehACSwitch17')!=-1):  #空调开关17
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=17,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))
            
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
                 
        elif (xdata.rfind('VehACSwitch18')!=-1):  #空调开关18
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=18,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc)) 

          
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        elif (xdata.rfind('VehACSwitch20')!=-1):  #空调开关20
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=20,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('VehACSwitch21')!=-1):  #空调开关21
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=21,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('VehACSwitch24')!=-1):  #空调开关24
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=24,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
        
        elif (xdata.rfind('VehACSwitch25')!=-1):  #空调开关25
            xdata= xdata[:-20]
            ss1=xdata.index('"VehACS')
            ss1=xdata[ss1:]
            ssname=ss1[:15]
            ssv=ss1[16:]
            print ssname
            print ssv
            try:

                read = master.execute(slave=25,
                             function_code=0x06,
                             starting_address=0x00,
                             output_value=int(ssv))

                print(read)

            except Exception as exc:
                print(str(exc))

                            
                             
            ssname=json.loads(ssname)
            ssv1=json.loads(ssv)
            switchPost = json_switch_set(ssname,ssv1)
            client.publish(topic_post, payload=switchPost, qos=0)
        
         
        else:
            pass
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected disconnection %s' % rc)

def mqtt_connect_aliyun_iot_platform():
    client.on_log = on_log
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.username_pw_set(mqttUsername, mqttPassword)
    #print('clientId:', mqttClientId)
    #print('userName:', mqttUsername)
    #print('password:', mqttPassword)
    #print('brokerUrl:', brokerUrl)
    # ssl设置，并且port=8883
    # client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    try:
        client.connect(brokerUrl, 1883, 60)
    except:
        print('阿里云物联网平台MQTT服务器连接错误，请检查设备证书三元组、及接入点的域名！')
    client.loop_forever()

def publish_loop():
    
    while 1:
        time.sleep(5)
        wendu=28.8
        payload_json = {
            'id': int(time.time()),
            'params': {
                    #'CurrentTemperature': random.uniform(20, 30),
                    "CurrentTemperature01": wendu#random.uniform(16, 32)
                    #'EnvironmentTemperature3': random.uniform(20, 30),
               
            },
            'method': "thing.event.property.post"
            }
        client.publish(topic_post, payload=str(payload_json))
        #print ('hwzn')
            


def usb0(slave,function_code,starting_address,output_value):
    global shebei
    global shebei2
    global shebei3
    global shebei4
    global shebei5
    global shebei6
    global shebei7
    global shebei8
    global shebei9
    global shebei10
    global shebei11
    global shebei12
    global shebei13
    global shebei14
    global shebei17
    global shebei18
    global shebei20
    global shebei21
    global shebei24
    global shebei25
    try:
        # 通信设置
        master = modbus_rtu.RtuMaster(serial.Serial(port='/dev/ttyUSB0',	# 连接端口
                                                    baudrate=9600, 	# 连接波特率
                                                    bytesize=8, 	# 数据位
                                                    parity='N', 	# 奇偶校验位
                                                    stopbits=1))	# 停止位
        master.set_timeout(5.0)
        master.set_verbose(True)

        # 发送数据并接受数据
        read = master.execute(slave,function_code,starting_address,output_value)
        #print(read)	# 打印获取的数据
        if (slave==1):
            shebei=1
        elif (slave==2):   
            shebei2=1
        elif (slave==3):
            shebei3=1
        elif (slave==4):   
            shebei4=1 
        elif (slave==5):   
            shebei5=1
        elif (slave==6):
            shebei6=1
        elif (slave==7):   
            shebei7=1 
        elif (slave==8):   
            shebei8=1
        elif (slave==9):
            shebei9=1
        elif (slave==10):   
            shebei10=1 
        elif (slave==11):   
            shebei11=1
        elif (slave==12):
            shebei12=1
        elif (slave==13):   
            shebei13=1  
        elif (slave==14):
            shebei14=1
        elif (slave==17):
            shebei17=1
        elif (slave==18):
            shebei18=1
        
        elif (slave==20):   
            shebei20=1 
        elif (slave==21):   
            shebei21=1
        elif (slave==24):
            shebei24=1
        elif (slave==25):   
            shebei25=1            
        return read
    except Exception as exc:
        print(str(exc))
        if (0==cmp('Response length is invalid 0',(str(exc)))):
            print 'hwznnn' #shebei=0           

        
def com_Polling(): #查巡各个房间状态变化上送平台

    onbz=0
    offbz=0
    shebei=0
    kaiguan=''
    fengsu=0
    moshi=0
    mubiao=0
    dangqian=0
    
    onbz2=0
    offbz2=0
    shebei2=0
    kaiguan2=''
    fengsu2=0
    moshi2=0
    mubiao2=0
    dangqian2=0

    onbz3=0
    offbz3=0
    shebei3=0
    kaiguan3=''
    fengsu3=0
    moshi3=0
    mubiao3=0
    dangqian3=0

    onbz4=0
    offbz4=0
    shebei4=0
    kaiguan4=''
    fengsu4=0
    moshi4=0
    mubiao4=0
    dangqian4=0

    onbz5=0
    offbz5=0
    shebei5=0
    kaiguan5=''
    fengsu5=0
    moshi5=0
    mubiao5=0
    dangqian5=0

    onbz6=0
    offbz6=0
    shebei6=0
    kaiguan6=''
    fengsu6=0
    moshi6=0
    mubiao6=0
    dangqian6=0

    onbz7=0
    offbz7=0
    shebei7=0
    kaiguan7=''
    fengsu7=0
    moshi7=0
    mubiao7=0
    dangqian7=0

    onbz8=0
    offbz8=0
    shebei8=0
    kaiguan8=''
    fengsu8=0
    moshi8=0
    mubiao8=0
    dangqian8=0
    
    onbz9=0
    offbz9=0
    shebei9=0
    kaiguan9=''
    fengsu9=0
    moshi9=0
    mubiao9=0
    dangqian9=0

    onbz10=0
    offbz10=0
    shebei10=0
    kaiguan10=''
    fengsu10=0
    moshi10=0
    mubiao10=0
    dangqian10=0
    
    onbz11=0
    offbz11=0
    shebei11=0
    kaiguan11=''
    fengsu11=0
    moshi11=0
    mubiao11=0
    dangqian11=0
    
    onbz12=0
    offbz12=0
    shebei12=0
    kaiguan12=''
    fengsu12=0
    moshi12=0
    mubiao12=0
    dangqian12=0
    
    onbz13=0
    offbz13=0
    shebei13=0
    kaiguan13=''
    fengsu13=0
    moshi13=0
    mubiao13=0
    dangqian13=0
    
    onbz14=0
    offbz14=0
    shebei14=0
    kaiguan14=''
    fengsu14=0
    moshi14=0
    mubiao14=0
    dangqian14=0
    
    onbz17=0
    offbz17=0
    shebei17=0
    kaiguan17=''
    fengsu17=0
    moshi17=0
    mubiao17=0
    dangqian17=0
    
    onbz18=0
    offbz18=0
    shebei18=0
    kaiguan18=''
    fengsu18=0
    moshi18=0
    mubiao18=0
    dangqian18=0
    
    onbz20=0
    offbz20=0
    shebei20=0
    kaiguan20=''
    fengsu20=0
    moshi20=0
    mubiao20=0
    dangqian20=0
    
    onbz21=0
    offbz21=0
    shebei21=0
    kaiguan21=''
    fengsu21=0
    moshi21=0
    mubiao21=0
    dangqian21=0
    
    onbz24=0
    offbz24=0
    shebei24=0
    kaiguan24=''
    fengsu24=0
    moshi24=0
    mubiao24=0
    dangqian24=0
    
    onbz25=0
    offbz25=0
    shebei25=0
    kaiguan25=''
    fengsu25=0
    moshi25=0
    mubiao25=0
    dangqian25=0
    
    while 1:
        while 1:
            try:
                comdata=usb0(1,0x03,0x00,7)

                if(shebei==0 and offbz<3): 
                    offbz=offbz+1
                    onbz=0
                if(shebei==0 and offbz==3):     
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState01': shebei
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz=offbz+1
                #if(shebei==1):  
                     #onbz=onbz+1               
                if(shebei==1 and onbz<3):
                    onbz=onbz+1
                    offbz=0
                if(shebei==1 and onbz==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState01': shebei
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz=onbz+1
                    
                if (comdata!=''):
                    shebei=1
                
                if ((comdata[0]!=kaiguan)or(float(comdata[1]/10))!=mubiao or(comdata[2]!=moshi) or(comdata[3]!=fengsu)or(float(comdata[6]/10))!=dangqian):
                    kaiguan=comdata[0]  
                    mubiao=float(comdata[1]/10)
                    moshi=comdata[2]  
                    fengsu=comdata[3]
                    dangqian=float(comdata[6]/10)
                    shebei=1
                    print(kaiguan)
                    print(mubiao)
                    print(moshi)
                    print(fengsu)
                    print(dangqian)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch01': kaiguan,
                            'TargetTemperature01': mubiao,
                            'WorkMode01': moshi,
                            'WindSpeed01': fengsu,
                            'CurrentTemperature01': dangqian,
                            'RunningState01': shebei
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                shebei=0
            break 

        while 1:
            try:
                comdata=usb0(2,0x03,0x00,7)
      
                if(shebei2==0 and offbz2<3):
                    offbz2=offbz2+1
                    onbz2=0
                if(shebei2==0 and offbz2==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState02': shebei2
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz2=offbz2+1
  
                if(shebei2==1 and onbz2<3):
                    onbz2=onbz2+1
                    offbz2=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState02': shebei2
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz2=onbz2+1
                    offbz2=0
                    
                if (comdata!=''):
                    shebei2=1    
                    
                if ((comdata[0]!=kaiguan2)or(float(comdata[1]/10))!=mubiao2 or(comdata[2]!=moshi2) or(comdata[3]!=fengsu2)or(float(comdata[6]/10))!=dangqian2):
                    kaiguan2=comdata[0]  
                    mubiao2=float(comdata[1]/10)
                    moshi2=comdata[2]  
                    fengsu2=comdata[3]
                    dangqian2=float(comdata[6]/10)
                    shebei2=1
                    print(kaiguan2)
                    print(mubiao2)
                    print(moshi2)
                    print(fengsu2)
                    print(dangqian2)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch02': kaiguan2,
                            'TargetTemperature02': mubiao2,
                            'WorkMode02': moshi2,
                            'WindSpeed02': fengsu2,
                            'CurrentTemperature02': dangqian2,
                            'RunningState02': shebei2
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei2=0
            break 
            
            
            
        while 1:
            try:
                comdata=usb0(3,0x03,0x00,7)
      
                if(shebei3==0 and offbz3<3):
                    offbz3=offbz3+1
                    onbz3=0
                if(shebei3==0 and offbz3==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState03': shebei3
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz3=offbz3+1
  
                if(shebei3==1 and onbz3<3):
                    onbz3=onbz3+1
                    offbz3=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState03': shebei3
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz3=onbz3+1
                    offbz3=0
                    
                if (comdata!=''):
                    shebei3=1    
                    
                if ((comdata[0]!=kaiguan3)or(float(comdata[1]/10))!=mubiao3 or(comdata[2]!=moshi3) or(comdata[3]!=fengsu3)or(float(comdata[6]/10))!=dangqian3):
                    kaiguan3=comdata[0]  
                    mubiao3=float(comdata[1]/10)
                    moshi3=comdata[2]  
                    fengsu3=comdata[3]
                    dangqian3=float(comdata[6]/10)
                    shebei3=1
                    print(kaiguan3)
                    print(mubiao3)
                    print(moshi3)
                    print(fengsu3)
                    print(dangqian3)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch03': kaiguan3,
                            'TargetTemperature03': mubiao3,
                            'WorkMode03': moshi3,
                            'WindSpeed03': fengsu3,
                            'CurrentTemperature03': dangqian3,
                            'RunningState03': shebei3
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei3=0
            break    
        
        
        while 1:
            try:
                comdata=usb0(4,0x03,0x00,7)
      
                if(shebei4==0 and offbz4<3):
                    offbz4=offbz4+1
                    onbz4=0
                if(shebei4==0 and offbz4==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState04': shebei4
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz4=offbz4+1
  
                if(shebei4==1 and onbz4<3):
                    onbz4=onbz4+1
                    offbz4=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState04': shebei4
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz4=onbz4+1
                    offbz4=0
                    
                if (comdata!=''):
                    shebei4=1    
                    
                if ((comdata[0]!=kaiguan4)or(float(comdata[1]/10))!=mubiao4 or(comdata[2]!=moshi4) or(comdata[3]!=fengsu4)or(float(comdata[6]/10))!=dangqian4):
                    kaiguan4=comdata[0]  
                    mubiao4=float(comdata[1]/10)
                    moshi4=comdata[2]  
                    fengsu4=comdata[3]
                    dangqian4=float(comdata[6]/10)
                    shebei4=1
                    print(kaiguan4)
                    print(mubiao4)
                    print(moshi4)
                    print(fengsu4)
                    print(dangqian4)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch04': kaiguan4,
                            'TargetTemperature04': mubiao4,
                            'WorkMode04': moshi4,
                            'WindSpeed04': fengsu4,
                            'CurrentTemperature04': dangqian4,
                            'RunningState04': shebei4
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei4=0
            break    
        
        
        
        
        while 1:
            try:
                comdata=usb0(5,0x03,0x00,7)
      
                if(shebei5==0 and offbz5<3):
                    offbz5=offbz5+1
                    onbz5=0
                if(shebei5==0 and offbz5==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState05': shebei5
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz5=offbz5+1
  
                if(shebei5==1 and onbz5<3):
                    onbz5=onbz5+1
                    offbz5=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState05': shebei5
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz5=onbz5+1
                    offbz5=0
                    
                if (comdata!=''):
                    shebei5=1    
                    
                if ((comdata[0]!=kaiguan5)or(float(comdata[1]/10))!=mubiao5 or(comdata[2]!=moshi5) or(comdata[3]!=fengsu5)or(float(comdata[6]/10))!=dangqian5):
                    kaiguan5=comdata[0]  
                    mubiao5=float(comdata[1]/10)
                    moshi5=comdata[2]  
                    fengsu5=comdata[3]
                    dangqian5=float(comdata[6]/10)
                    shebei5=1
                    print(kaiguan5)
                    print(mubiao5)
                    print(moshi5)
                    print(fengsu5)
                    print(dangqian5)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch05': kaiguan5,
                            'TargetTemperature05': mubiao5,
                            'WorkMode05': moshi5,
                            'WindSpeed05': fengsu5,
                            'CurrentTemperature05': dangqian5,
                            'RunningState05': shebei5
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei5=0
            break
        
        
        
        while 1:
            try:
                comdata=usb0(6,0x03,0x00,7)
      
                if(shebei6==0 and offbz6<3):
                    offbz6=offbz6+1
                    onbz6=0
                if(shebei6==0 and offbz6==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState06': shebei6
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz6=offbz6+1
  
                if(shebei6==1 and onbz6<3):
                    onbz6=onbz6+1
                    offbz6=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState06': shebei6
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz6=onbz6+1
                    offbz6=0
                    
                if (comdata!=''):
                    shebei6=1    
                    
                if ((comdata[0]!=kaiguan6)or(float(comdata[1]/10))!=mubiao6 or(comdata[2]!=moshi6) or(comdata[3]!=fengsu6)or(float(comdata[6]/10))!=dangqian6):
                    kaiguan6=comdata[0]  
                    mubiao6=float(comdata[1]/10)
                    moshi6=comdata[2]  
                    fengsu6=comdata[3]
                    dangqian6=float(comdata[6]/10)
                    shebei6=1
                    print(kaiguan6)
                    print(mubiao6)
                    print(moshi6)
                    print(fengsu6)
                    print(dangqian6)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch06': kaiguan6,
                            'TargetTemperature06': mubiao6,
                            'WorkMode06': moshi6,
                            'WindSpeed06': fengsu6,
                            'CurrentTemperature06': dangqian6,
                            'RunningState06': shebei6
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei6=0
            break
        
        
        
        # while 1:
            # try:
                # comdata=usb0(7,0x03,0x00,7)
      
                # if(shebei7==0 and offbz7<3):
                    # offbz7=offbz7+1
                    # onbz7=0
                # if(shebei7==0 and offbz7==3):    
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                        # 'RunningState07': shebei7
                        # },
                        # 'method': "thing.event.property.post"
                    # }
                    # client.publish(topic_post, payload=str(payload_json))
                    # offbz7=offbz7+1
  
                # if(shebei7==1 and onbz7<3):
                    # onbz7=onbz7+1
                    # offbz7=0
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                        # 'RunningState07': shebei7
                        # },
                        # 'method': "thing.event.property.post"
                    # }
                    # client.publish(topic_post, payload=str(payload_json))
                    # onbz7=onbz7+1
                    # offbz7=0
                    
                # if (comdata!=''):
                    # shebei7=1    
                    
                # if ((comdata[0]!=kaiguan7)or(float(comdata[1]/10))!=mubiao7 or(comdata[2]!=moshi7) or(comdata[3]!=fengsu7)or(float(comdata[6]/10))!=dangqian7):
                    # kaiguan7=comdata[0]  
                    # mubiao7=float(comdata[1]/10)
                    # moshi7=comdata[2]  
                    # fengsu7=comdata[3]
                    # dangqian7=float(comdata[6]/10)
                    # shebei7=1
                    # print(kaiguan7)
                    # print(mubiao7)
                    # print(moshi7)
                    # print(fengsu7)
                    # print(dangqian7)
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                            # 'VehACSwitch07': kaiguan7,
                            # 'TargetTemperature07': mubiao7,
                            # 'WorkMode07': moshi7,
                            # 'WindSpeed07': fengsu7,
                            # 'CurrentTemperature07': dangqian7,
                            # 'RunningState07': shebei7
                        # },
                        # 'method': "thing.event.property.post"
                        # }
                    # client.publish(topic_post, payload=str(payload_json))
                # break    
            # except Exception as exc:
                # print(str(exc))
                # print '0000'
                # shebei7=0
            # break
        
        
        # while 1:
            # try:
                # comdata=usb0(8,0x03,0x00,7)
      
                # if(shebei8==0 and offbz8<3):
                    # offbz8=offbz8+1
                    # onbz8=0
                # if(shebei8==0 and offbz8==3):    
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                        # 'RunningState08': shebei8
                        # },
                        # 'method': "thing.event.property.post"
                    # }
                    # client.publish(topic_post, payload=str(payload_json))
                    # offbz8=offbz8+1
  
                # if(shebei8==1 and onbz8<3):
                    # onbz8=onbz8+1
                    # offbz8=0
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                        # 'RunningState08': shebei8
                        # },
                        # 'method': "thing.event.property.post"
                    # }
                    # client.publish(topic_post, payload=str(payload_json))
                    # onbz8=onbz8+1
                    # offbz8=0
                    
                # if (comdata!=''):
                    # shebei8=1    
                    
                # if ((comdata[0]!=kaiguan8)or(float(comdata[1]/10))!=mubiao8 or(comdata[2]!=moshi8) or(comdata[3]!=fengsu8)or(float(comdata[6]/10))!=dangqian8):
                    # kaiguan8=comdata[0]  
                    # mubiao8=float(comdata[1]/10)
                    # moshi8=comdata[2]  
                    # fengsu8=comdata[3]
                    # dangqian8=float(comdata[6]/10)
                    # shebei8=1
                    # print(kaiguan8)
                    # print(mubiao8)
                    # print(moshi8)
                    # print(fengsu8)
                    # print(dangqian8)
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                            # 'VehACSwitch08': kaiguan8,
                            # 'TargetTemperature08': mubiao8,
                            # 'WorkMode08': moshi8,
                            # 'WindSpeed08': fengsu8,
                            # 'CurrentTemperature08': dangqian8,
                            # 'RunningState08': shebei8
                        # },
                        # 'method': "thing.event.property.post"
                        # }
                    # client.publish(topic_post, payload=str(payload_json))
                # break    
            # except Exception as exc:
                # print(str(exc))
                # print '0000'
                # shebei8=0
            # break
        
        
        
        
        while 1:
            try:
                comdata=usb0(9,0x03,0x00,7)
      
                if(shebei9==0 and offbz9<3):
                    offbz9=offbz9+1
                    onbz9=0
                if(shebei9==0 and offbz9==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState09': shebei9
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz9=offbz9+1
  
                if(shebei9==1 and onbz9<3):
                    onbz9=onbz9+1
                    offbz9=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState09': shebei9
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz9=onbz9+1
                    offbz9=0
                    
                if (comdata!=''):
                    shebei9=1    
                    
                if ((comdata[0]!=kaiguan9)or(float(comdata[1]/10))!=mubiao9 or(comdata[2]!=moshi9) or(comdata[3]!=fengsu9)or(float(comdata[6]/10))!=dangqian9):
                    kaiguan9=comdata[0]  
                    mubiao9=float(comdata[1]/10)
                    moshi9=comdata[2]  
                    fengsu9=comdata[3]
                    dangqian9=float(comdata[6]/10)
                    shebei9=1
                    print(kaiguan9)
                    print(mubiao9)
                    print(moshi9)
                    print(fengsu9)
                    print(dangqian9)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch09': kaiguan9,
                            'TargetTemperature09': mubiao9,
                            'WorkMode09': moshi9,
                            'WindSpeed09': fengsu9,
                            'CurrentTemperature09': dangqian9,
                            'RunningState09': shebei9
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei9=0
            break
        
        
        
        while 1:
            try:
                comdata=usb0(10,0x03,0x00,7)
      
                if(shebei10==0 and offbz10<3):
                    offbz10=offbz10+1
                    onbz10=0
                if(shebei10==0 and offbz10==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState10': shebei10
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz10=offbz10+1
  
                if(shebei10==1 and onbz10<3):
                    onbz10=onbz10+1
                    offbz10=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState10': shebei10
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz10=onbz10+1
                    offbz10=0
                    
                if (comdata!=''):
                    shebei10=1    
                    
                if ((comdata[0]!=kaiguan10)or(float(comdata[1]/10))!=mubiao10 or(comdata[2]!=moshi10) or(comdata[3]!=fengsu10)or(float(comdata[6]/10))!=dangqian10):
                    kaiguan10=comdata[0]  
                    mubiao10=float(comdata[1]/10)
                    moshi10=comdata[2]  
                    fengsu10=comdata[3]
                    dangqian10=float(comdata[6]/10)
                    shebei10=1
                    print(kaiguan10)
                    print(mubiao10)
                    print(moshi10)
                    print(fengsu10)
                    print(dangqian10)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch10': kaiguan10,
                            'TargetTemperature10': mubiao10,
                            'WorkMode10': moshi10,
                            'WindSpeed10': fengsu10,
                            'CurrentTemperature10': dangqian10,
                            'RunningState10': shebei10
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei10=0
            break
        
        
        # while 1:
            # try:
                # comdata=usb0(11,0x03,0x00,7)
      
                # if(shebei11==0 and offbz11<3):
                    # offbz11=offbz11+1
                    # onbz11=0
                # if(shebei11==0 and offbz11==3):    
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                        # 'RunningState11': shebei11
                        # },
                        # 'method': "thing.event.property.post"
                    # }
                    # client.publish(topic_post, payload=str(payload_json))
                    # offbz11=offbz11+1
  
                # if(shebei11==1 and onbz11<3):
                    # onbz11=onbz11+1
                    # offbz11=0
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                        # 'RunningState11': shebei11
                        # },
                        # 'method': "thing.event.property.post"
                    # }
                    # client.publish(topic_post, payload=str(payload_json))
                    # onbz11=onbz11+1
                    # offbz11=0
                    
                # if (comdata!=''):
                    # shebei11=1    
                    
                # if ((comdata[0]!=kaiguan11)or(float(comdata[1]/10))!=mubiao11 or(comdata[2]!=moshi11) or(comdata[3]!=fengsu11)or(float(comdata[6]/10))!=dangqian11):
                    # kaiguan11=comdata[0]  
                    # mubiao11=float(comdata[1]/10)
                    # moshi11=comdata[2]  
                    # fengsu11=comdata[3]
                    # dangqian11=float(comdata[6]/10)
                    # shebei11=1
                    # print(kaiguan11)
                    # print(mubiao11)
                    # print(moshi11)
                    # print(fengsu11)
                    # print(dangqian11)
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                            # 'VehACSwitch11': kaiguan11,
                            # 'TargetTemperature11': mubiao11,
                            # 'WorkMode11': moshi11,
                            # 'WindSpeed11': fengsu11,
                            # 'CurrentTemperature11': dangqian11,
                            # 'RunningState11': shebei11
                        # },
                        # 'method': "thing.event.property.post"
                        # }
                    # client.publish(topic_post, payload=str(payload_json))
                # break    
            # except Exception as exc:
                # print(str(exc))
                # print '0000'
                # shebei11=0
            # break
        
        
        # while 1:
            # try:
                # comdata=usb0(12,0x03,0x00,7)
      
                # if(shebei12==0 and offbz12<3):
                    # offbz12=offbz12+1
                    # onbz12=0
                # if(shebei12==0 and offbz12==3):    
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                        # 'RunningState12': shebei12
                        # },
                        # 'method': "thing.event.property.post"
                    # }
                    # client.publish(topic_post, payload=str(payload_json))
                    # offbz12=offbz12+1
  
                # if(shebei12==1 and onbz12<3):
                    # onbz12=onbz12+1
                    # offbz12=0
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                        # 'RunningState12': shebei12
                        # },
                        # 'method': "thing.event.property.post"
                    # }
                    # client.publish(topic_post, payload=str(payload_json))
                    # onbz12=onbz12+1
                    # offbz12=0
                    
                # if (comdata!=''):
                    # shebei12=1    
                    
                # if ((comdata[0]!=kaiguan12)or(float(comdata[1]/10))!=mubiao12 or(comdata[2]!=moshi12) or(comdata[3]!=fengsu12)or(float(comdata[6]/10))!=dangqian12):
                    # kaiguan12=comdata[0]  
                    # mubiao12=float(comdata[1]/10)
                    # moshi12=comdata[2]  
                    # fengsu12=comdata[3]
                    # dangqian12=float(comdata[6]/10)
                    # shebei12=1
                    # print(kaiguan12)
                    # print(mubiao12)
                    # print(moshi12)
                    # print(fengsu12)
                    # print(dangqian12)
                    # payload_json = {
                        # 'id': int(time.time()),
                        # 'params': {
                            # 'VehACSwitch12': kaiguan12,
                            # 'TargetTemperature12': mubiao12,
                            # 'WorkMode12': moshi12,
                            # 'WindSpeed12': fengsu12,
                            # 'CurrentTemperature12': dangqian12,
                            # 'RunningState12': shebei12
                        # },
                        # 'method': "thing.event.property.post"
                        # }
                    # client.publish(topic_post, payload=str(payload_json))
                # break    
            # except Exception as exc:
                # print(str(exc))
                # print '0000'
                # shebei12=0
            # break
        
        
        while 1:
            try:
                comdata=usb0(13,0x03,0x00,7)
      
                if(shebei13==0 and offbz13<3):
                    offbz13=offbz13+1
                    onbz13=0
                if(shebei13==0 and offbz13==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState13': shebei13
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz13=offbz13+1
  
                if(shebei13==1 and onbz13<3):
                    onbz13=onbz13+1
                    offbz13=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState13': shebei13
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz13=onbz13+1
                    offbz13=0
                    
                if (comdata!=''):
                    shebei13=1    
                    
                if ((comdata[0]!=kaiguan13)or(float(comdata[1]/10))!=mubiao13 or(comdata[2]!=moshi13) or(comdata[3]!=fengsu13)or(float(comdata[6]/10))!=dangqian13):
                    kaiguan13=comdata[0]  
                    mubiao13=float(comdata[1]/10)
                    moshi13=comdata[2]  
                    fengsu13=comdata[3]
                    dangqian13=float(comdata[6]/10)
                    shebei13=1
                    print(kaiguan13)
                    print(mubiao13)
                    print(moshi13)
                    print(fengsu13)
                    print(dangqian13)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch13': kaiguan13,
                            'TargetTemperature13': mubiao13,
                            'WorkMode13': moshi13,
                            'WindSpeed13': fengsu13,
                            'CurrentTemperature13': dangqian13,
                            'RunningState13': shebei13
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei13=0
            break
        
        
        while 1:
            try:
                comdata=usb0(14,0x03,0x00,7)
      
                if(shebei14==0 and offbz14<3):
                    offbz14=offbz14+1
                    onbz14=0
                if(shebei14==0 and offbz14==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState14': shebei14
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz14=offbz14+1
  
                if(shebei14==1 and onbz14<3):
                    onbz14=onbz14+1
                    offbz14=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState14': shebei14
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz14=onbz14+1
                    offbz14=0
                    
                if (comdata!=''):
                    shebei14=1    
                    
                if ((comdata[0]!=kaiguan14)or(float(comdata[1]/10))!=mubiao14 or(comdata[2]!=moshi14) or(comdata[3]!=fengsu14)or(float(comdata[6]/10))!=dangqian14):
                    kaiguan14=comdata[0]  
                    mubiao14=float(comdata[1]/10)
                    moshi14=comdata[2]  
                    fengsu14=comdata[3]
                    dangqian14=float(comdata[6]/10)
                    shebei14=1
                    print(kaiguan14)
                    print(mubiao14)
                    print(moshi14)
                    print(fengsu14)
                    print(dangqian14)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch14': kaiguan14,
                            'TargetTemperature14': mubiao14,
                            'WorkMode14': moshi14,
                            'WindSpeed14': fengsu14,
                            'CurrentTemperature14': dangqian14,
                            'RunningState14': shebei14
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei14=0
            break
        
        
        while 1:
            try:
                comdata=usb0(17,0x03,0x00,7)
      
                if(shebei17==0 and offbz17<3):
                    offbz17=offbz17+1
                    onbz17=0
                if(shebei17==0 and offbz17==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState17': shebei17
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz17=offbz17+1
  
                if(shebei17==1 and onbz17<3):
                    onbz17=onbz17+1
                    offbz17=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState17': shebei17
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz17=onbz17+1
                    offbz17=0
                    
                if (comdata!=''):
                    shebei17=1    
                    
                if ((comdata[0]!=kaiguan17)or(float(comdata[1]/10))!=mubiao17 or(comdata[2]!=moshi17) or(comdata[3]!=fengsu17)or(float(comdata[6]/10))!=dangqian17):
                    kaiguan17=comdata[0]  
                    mubiao17=float(comdata[1]/10)
                    moshi17=comdata[2]  
                    fengsu17=comdata[3]
                    dangqian17=float(comdata[6]/10)
                    shebei17=1
                    print(kaiguan17)
                    print(mubiao17)
                    print(moshi17)
                    print(fengsu17)
                    print(dangqian17)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch17': kaiguan17,
                            'TargetTemperature17': mubiao17,
                            'WorkMode17': moshi17,
                            'WindSpeed17': fengsu17,
                            'CurrentTemperature17': dangqian17,
                            'RunningState17': shebei17
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei17=0
            break
        
        while 1:
            try:
                comdata=usb0(18,0x03,0x00,7)
      
                if(shebei18==0 and offbz18<3):
                    offbz18=offbz18+1
                    onbz18=0
                if(shebei18==0 and offbz18==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState18': shebei18
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz18=offbz18+1
  
                if(shebei18==1 and onbz18<3):
                    onbz18=onbz18+1
                    offbz18=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState18': shebei18
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz18=onbz18+1
                    offbz18=0
                    
                if (comdata!=''):
                    shebei18=1    
                    
                if ((comdata[0]!=kaiguan18)or(float(comdata[1]/10))!=mubiao18 or(comdata[2]!=moshi18) or(comdata[3]!=fengsu18)or(float(comdata[6]/10))!=dangqian18):
                    kaiguan18=comdata[0]  
                    mubiao18=float(comdata[1]/10)
                    moshi18=comdata[2]  
                    fengsu18=comdata[3]
                    dangqian18=float(comdata[6]/10)
                    shebei18=1
                    print(kaiguan18)
                    print(mubiao18)
                    print(moshi18)
                    print(fengsu18)
                    print(dangqian18)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch18': kaiguan18,
                            'TargetTemperature18': mubiao18,
                            'WorkMode18': moshi18,
                            'WindSpeed18': fengsu18,
                            'CurrentTemperature18': dangqian18,
                            'RunningState18': shebei18
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei18=0
            break
        
        
        
        
        while 1:
            try:
                comdata=usb0(20,0x03,0x00,7)
      
                if(shebei20==0 and offbz20<3):
                    offbz20=offbz20+1
                    onbz20=0
                if(shebei20==0 and offbz20==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState20': shebei20
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz20=offbz20+1
  
                if(shebei20==1 and onbz20<3):
                    onbz20=onbz20+1
                    offbz20=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState20': shebei20
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz20=onbz20+1
                    offbz20=0
                    
                if (comdata!=''):
                    shebei20=1    
                    
                if ((comdata[0]!=kaiguan20)or(float(comdata[1]/10))!=mubiao20 or(comdata[2]!=moshi20) or(comdata[3]!=fengsu20)or(float(comdata[6]/10))!=dangqian20):
                    kaiguan20=comdata[0]  
                    mubiao20=float(comdata[1]/10)
                    moshi20=comdata[2]  
                    fengsu20=comdata[3]
                    dangqian20=float(comdata[6]/10)
                    shebei20=1
                    print(kaiguan20)
                    print(mubiao20)
                    print(moshi20)
                    print(fengsu20)
                    print(dangqian20)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch20': kaiguan20,
                            'TargetTemperature20': mubiao20,
                            'WorkMode20': moshi20,
                            'WindSpeed20': fengsu20,
                            'CurrentTemperature20': dangqian20,
                            'RunningState20': shebei20
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei20=0
            break
        
        while 1:
            try:
                comdata=usb0(21,0x03,0x00,7)
      
                if(shebei21==0 and offbz21<3):
                    offbz21=offbz21+1
                    onbz21=0
                if(shebei21==0 and offbz21==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState21': shebei21
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz21=offbz21+1
  
                if(shebei21==1 and onbz21<3):
                    onbz21=onbz21+1
                    offbz21=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState21': shebei21
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz21=onbz21+1
                    offbz21=0
                    
                if (comdata!=''):
                    shebei21=1    
                    
                if ((comdata[0]!=kaiguan21)or(float(comdata[1]/10))!=mubiao21 or(comdata[2]!=moshi21) or(comdata[3]!=fengsu21)or(float(comdata[6]/10))!=dangqian21):
                    kaiguan21=comdata[0]  
                    mubiao21=float(comdata[1]/10)
                    moshi21=comdata[2]  
                    fengsu21=comdata[3]
                    dangqian21=float(comdata[6]/10)
                    shebei21=1
                    print(kaiguan21)
                    print(mubiao21)
                    print(moshi21)
                    print(fengsu21)
                    print(dangqian21)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch21': kaiguan21,
                            'TargetTemperature21': mubiao21,
                            'WorkMode21': moshi21,
                            'WindSpeed21': fengsu21,
                            'CurrentTemperature21': dangqian21,
                            'RunningState21': shebei21
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei21=0
            break
        
        
        while 1:
            try:
                comdata=usb0(24,0x03,0x00,7)
      
                if(shebei24==0 and offbz24<3):
                    offbz24=offbz24+1
                    onbz24=0
                if(shebei24==0 and offbz24==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState24': shebei24
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz24=offbz24+1
  
                if(shebei24==1 and onbz24<3):
                    onbz24=onbz24+1
                    offbz24=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState24': shebei24
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz24=onbz24+1
                    offbz24=0
                    
                if (comdata!=''):
                    shebei24=1    
                    
                if ((comdata[0]!=kaiguan24)or(float(comdata[1]/10))!=mubiao24 or(comdata[2]!=moshi24) or(comdata[3]!=fengsu24)or(float(comdata[6]/10))!=dangqian24):
                    kaiguan24=comdata[0]  
                    mubiao24=float(comdata[1]/10)
                    moshi24=comdata[2]  
                    fengsu24=comdata[3]
                    dangqian24=float(comdata[6]/10)
                    shebei24=1
                    print(kaiguan24)
                    print(mubiao24)
                    print(moshi24)
                    print(fengsu24)
                    print(dangqian24)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch24': kaiguan24,
                            'TargetTemperature24': mubiao24,
                            'WorkMode24': moshi24,
                            'WindSpeed24': fengsu24,
                            'CurrentTemperature24': dangqian24,
                            'RunningState24': shebei24
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei24=0
            break
        
        
        while 1:
            try:
                comdata=usb0(25,0x03,0x00,7)
      
                if(shebei25==0 and offbz25<3):
                    offbz25=offbz25+1
                    onbz25=0
                if(shebei25==0 and offbz25==3):    
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState25': shebei25
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    offbz25=offbz25+1
  
                if(shebei25==1 and onbz25<3):
                    onbz25=onbz25+1
                    offbz25=0
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                        'RunningState25': shebei25
                        },
                        'method': "thing.event.property.post"
                    }
                    client.publish(topic_post, payload=str(payload_json))
                    onbz25=onbz25+1
                    offbz25=0
                    
                if (comdata!=''):
                    shebei25=1    
                    
                if ((comdata[0]!=kaiguan25)or(float(comdata[1]/10))!=mubiao25 or(comdata[2]!=moshi25) or(comdata[3]!=fengsu25)or(float(comdata[6]/10))!=dangqian25):
                    kaiguan25=comdata[0]  
                    mubiao25=float(comdata[1]/10)
                    moshi25=comdata[2]  
                    fengsu25=comdata[3]
                    dangqian25=float(comdata[6]/10)
                    shebei25=1
                    print(kaiguan25)
                    print(mubiao25)
                    print(moshi25)
                    print(fengsu25)
                    print(dangqian25)
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'VehACSwitch25': kaiguan25,
                            'TargetTemperature25': mubiao25,
                            'WorkMode25': moshi25,
                            'WindSpeed25': fengsu25,
                            'CurrentTemperature25': dangqian25,
                            'RunningState25': shebei25
                        },
                        'method': "thing.event.property.post"
                        }
                    client.publish(topic_post, payload=str(payload_json))
                break    
            except Exception as exc:
                print(str(exc))
                print '0000'
                shebei25=0
            break
        
        
        
if __name__ == '__main__':
    # 建立线程t1：mqtt连接阿里云物联网平台
    # 建立线程t2：定时向阿里云发布消息：5s为间隔，变化开关状态
    
    t1 = threading.Thread(target=mqtt_connect_aliyun_iot_platform, )
    #t2 = threading.Thread(target=publish_loop, )
    t3 = threading.Thread(target=com_Polling, )
    t1.start()
    #t2.start()
    t3.start()
