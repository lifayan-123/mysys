#!/usr/bin/python
# -*- coding: UTF-8 -*-
import socket,sys
import time
import threading
import string
import os
import serial
import binascii
from binascii import hexlify
#from string import Template


output=''
output1=''
com_data=''
clientsock=''
lianj=''
ser0 = serial.Serial('/dev/ttyS0', 115200)
ser1 = serial.Serial('/dev/ttyS1', 115200)

def hex2char1(data):
    global output1
#    binascii.a2b_hex(data)
    output1 = binascii.unhexlify(data)
    #output = output[::-1]


def hex2char(data):
    global output
#    binascii.a2b_hex(data)
    output = binascii.unhexlify(data)
    output = output[::-1]

network='/etc/config/network'
os.system("sh root/Vport/./xn.sh")

addr=('255.255.255.255',1500)
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
s.bind(addr)
s.sendto("hello from client",addr)
ff = ("0123456789012345678901234567890123456789")
#xf = ("\x9c\xa5\x25\xb4\x47\x19\xb2\x64\x00\xa8\xc0\xa2\x20\x07\x00\xa8\xc0\x0f\x27\x01\x00\xa8\xc0\x03\x80\x25\x00\x03\x00\x01\xa4\x00\xff\xff\xff")
sbh = ("\x31\x31\x30\x34\x31\x35")
aamac = ("\x31\x32\x33\x34\x45\x36")

address='0.0.0.0'     
with open('/root/Vport/port','r') as aa:
    port = aa.read();
aa.close()
time.sleep(0.2)         
buffsize=1024         
tcps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcps.bind((address,int(port)))
tcps.listen(2)     

def tcplink(sock,addr):
    global lianj
    while True:  
        recvdata=clientsock.recv(buffsize)
        if recvdata=='exit' or not recvdata:
            print "tingzhi"
            lianj = 0
            break
        if recvdata: 
            ser1.write(recvdata)
        recvdata=''
 
def xncom():
    w_str=''
    inmac=''
    global output
    while 1:
        data, Addr=s.recvfrom(1024)
        if not data:
            break
        if (data>0):
            print data
        if data == ff:
            with open('/root/Vport/port','r') as aa:
                PORT1 = aa.read();
            aaaa=int(PORT1)
            aaa1=hex(aaaa)
	    aaa2=aaa1[2:]
	    hex2char(aaa2)
	    pcport=output

	    with open('/root/Vport/pcport','r') as aa:
	        PORT1 = aa.read();
            aaaa=int(PORT1)
	    aaa1=hex(aaaa)
	    aaa2=aaa1[2:]
	    hex2char(aaa2)
	    port=output
	    with open('/root/Vport/Baud','r') as aa:
	        PORT1 = aa.read();
	    aaaa=int(PORT1)
	    aaa1=hex(aaaa)
	    aaa2=aaa1[2:]
	    hex2char(aaa2)
	    Baud=output

	    with open('/root/Vport/gateway','r') as aa:
	        wangg1 = aa.read();
	    wangg=wangg1[:-1]
	    packed_ip_addr = socket.inet_aton(wangg1)
	    hexStr=hexlify(packed_ip_addr)
	    hex2char(hexStr)
	    gateway=output

	    with open('/root/Vport/netmask','r') as aa:
	        PORT1 = aa.read();
	    packed_ip_addr = socket.inet_aton(PORT1)
	    hexStr=hexlify(packed_ip_addr)
	    hex2char(hexStr)
	    netmask=output

	    with open('/root/Vport/addr','r') as aa:
	        sb_addr1 = aa.read();
	    sb_addr=sb_addr1[:-1]
	    packed_ip_addr = socket.inet_aton(sb_addr1)
	    hexStr=hexlify(packed_ip_addr)
	    hex2char(hexStr)
	    Addr1=output
   
	    with open('/root/Vport/pcaddr','r') as aa:
	        PORT1 = aa.read();
	    packed_ip_addr = socket.inet_aton(PORT1)
	    hexStr=hexlify(packed_ip_addr)
	    hex2char(hexStr)
	    pcaddr=output


	    with open('/root/Vport/mac','r') as aa:
	        PORT1 = aa.read();
	    Mac=(PORT1.replace(':',''))
	    Mac=(Mac.strip('\n')) 
	    hex2char1(Mac)
	    mac=output1
            s.sendto('%s\xb2%s%s%s%s%s\x03%s\x00\x03\x00\x00\x04%s' % ( mac,pcaddr,port,Addr1,pcport,gateway,Baud,netmask),addr)
        if data[6:11] == sbh[0:5] and data[0:5] == mac:  #增加对比mac地址，防止同时重复写多台设备
            #data[6:7]="\x30"
            #data[7:8]="\x30"
            inmac=data[18:19]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss1=int(ss,16)
            inmac=data[19:20]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss2=int(ss,16)
            inmac=data[20:21]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss3=int(ss,16)
            inmac=data[21:22]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss4=int(ss,16)
            sbip='%s.%s.%s.%s' % (ss4,ss3,ss2,ss1)
        
            inmac=data[12:13]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss1=int(ss,16)
            inmac=data[13:14]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss2=int(ss,16)
            inmac=data[14:15]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss3=int(ss,16)
            inmac=data[15:16]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss4=int(ss,16)
            pcip='%s.%s.%s.%s' % (ss4,ss3,ss2,ss1)
 
            inmac=data[24:25]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss1=int(ss,16)
            inmac=data[25:26]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss2=int(ss,16)
            inmac=data[26:27]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss3=int(ss,16)
            inmac=data[27:28]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss4=int(ss,16)
            wangguan='%s.%s.%s.%s' % (ss4,ss3,ss2,ss1)
        
            inmac=data[36:37]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss1=int(ss,16)
            inmac=data[37:38]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss2=int(ss,16)
            inmac=data[38:39]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss3=int(ss,16)
            inmac=data[39:40]
            ss=binascii.b2a_hex(inmac).decode('utf-8')
            ss4=int(ss,16)
            zwym='%s.%s.%s.%s' % (ss4,ss3,ss2,ss1)

            ss1=data[16:17]
            ss2=data[17:18]
            inmac=ss2+ss1
            sss=binascii.b2a_hex(inmac).decode('utf-8')
            pcdc1=int(sss,16)
            type(pcdc1)
            pcdc=str(pcdc1)

            ss1=data[22:23]
            ss2=data[23:24]
            inmac=ss2+ss1
            sss=binascii.b2a_hex(inmac).decode('utf-8')
            sbdc1=int(sss,16)        
            type(sbdc1)
            sbdc=str(sbdc1)

            ss1=data[29:30]
            ss2=data[30:31]
            inmac=ss2+ss1
            sss=binascii.b2a_hex(inmac).decode('utf-8')
            btl1=int(sss,16)
            type(btl1)
            btl=str(btl1)

            f =open('/root/Vport/pcaddr','w')
            f.write(pcip)
            f.close()
            #ser1.write(ss)
            f  =open('/root/Vport/gateway','w')
            f.write(wangguan)
            f.close()
            f =open('/root/Vport/Baud','w')
            f.write(btl)
            f.close()
            f =open('/root/Vport/pcport','w')
            f.write(pcdc)
            f.close()
            f =open('/root/Vport/port','w')
            f.write(sbdc)
            f.close()
            f =open('/root/Vport/addr','w')
            f.write(sbip)
            f.close()

            os.system("sh /root/Vport/./xgwl.sh")
            time.sleep(1) 
            os.system("sh /root/Vport/./reboot.sh")
            data= ''
        time.sleep(0.1)
        pass


def com1():
   
    comfw_data= '' 
    #ser0.flushInput()
    #ser1.flushInput()
    check =''
    SendBuff = ("\x6E\x00\x00\x9C\x00\x08\x01\x12\x00\x00\x00\x7B\x00\xD7\x00\x00\x02\x16")
    while 1:
        while ser1.inWaiting() > 0:
            comfw_data += ser1.read(1)
        if comfw_data !='':
            print('hwzn') 
            global check
            if comfw_data[0]=="\xAA" and comfw_data[1]=="\x19"and comfw_data[2]=="\x01"and comfw_data[3]=="\x08"and comfw_data[4]=="\x01"and comfw_data[5]=="\x03":
                xg = comfw_data[7]#//x¸ß-   SendBuff[10]
                xd = comfw_data[6]#//xµÍ-  ok SendBuff[11]
		yg = comfw_data[9]#//y¸ß-  SendBuff[12]
		yd = comfw_data[8]#//yµÍ-   SendBuff[13]
                jgwz2=binascii.b2a_hex(SendBuff).decode('utf-8')
                jgwz3=jgwz2[:32]
                jy1=jgwz2[0:2]
                jy2=jgwz2[2:4]
                jy3=jgwz2[4:6]
                jy4=jgwz2[6:8]
                jy5=jgwz2[8:10]
                jy6=jgwz2[10:12]
                jy7=jgwz2[12:14]
                jy8=jgwz2[14:16]
                jy9=jgwz2[16:18]
                jy10=jgwz2[18:20]
                jy11=jgwz2[20:22]
                jy12=jgwz2[22:24]
                jy13=jgwz2[24:26]
                jy14=jgwz2[26:28]
                jy15=jgwz2[28:30]
                jy16=jgwz2[30:32]
                
                jy1=int(jy1,16)
                jy2=int(jy2,16)
                jy3=int(jy3,16)
                jy4=int(jy4,16)
                jy5=int(jy5,16)
                jy6=int(jy6,16)
                jy7=int(jy7,16)
                jy8=int(jy8,16)
                jy9=int(jy9,16)
                jy10=int(jy10,16)
                jy11=int(jy11,16)
                jy12=int(jy12,16)
                jy13=int(jy13,16)
                jy14=int(jy14,16)
                jy15=int(jy15,16)
                jy16=int(jy16,16)
                jaog = (jy1+jy2+jy3+jy4+jy5+jy6+jy7+jy8+jy9+jy10+jy11+jy12+jy13+jy14+jy15+jy16)/256
                jaoyd = (jy1+jy2+jy3+jy4+jy5+jy6+jy7+jy8+jy9+jy10+jy11+jy12+jy13+jy14+jy15+jy16)%256
                jaog = hex(jaog)
                jaoyd = hex(jaoyd)
                jaog = jaog[2:]
                jaoyd = jaoyd[2:]
                type(jaog)
                type(jaoyd)
                jaog = str(jaog)
                jaoyd = str(jaoyd) 
                ss2=len(jaog)
                if (ss2<2):
                    jaog = jaog.zfill(2)
                ss2=len(jaoyd)
                if (ss2<2):
                    jaoyd = jaoyd.zfill(2)
                jaog=(binascii.a2b_hex(jaog))
                jaoyd=(binascii.a2b_hex(jaoyd))
                ser0.write('\x6E\x00\x00\x9C\x00\x08\x01\x12\x00\x00%s%s%s%s\x00\x00%s%s' % (xg,xd,yg,yd,jaog,jaoyd))
                print("baojing")
            else:
         
                if lianj==1:
                #print clientsock
                    clientsock.send(comfw_data)
 
        comfw_data=''
        time.sleep(0.1)
        pass

threads = [] 
t1 =threading.Thread(target=xncom,name='')
threads.append(t1)
#t2 =threading.Thread(target=comjs,name='')
#threads.append(t2)
t2 =threading.Thread(target=com1,name='')
threads.append(t2)
if __name__ == "__main__":
    for t in threads:
        t.setDaemon(True)
        t.start()
        f=open('/sys/class/gpio/export','w')
    f.write('40')
    f.close()
    time.sleep(0.1)
    f=open('/sys/class/gpio/gpio40/direction','w')
    f.write('out')
    f.close()
    f=open('/sys/class/gpio/gpio40/value','w')
    f.write('0')
    f.close()
    global clientsock
    global lianj 
    while True:
        clientsock,clientaddress=tcps.accept()
        print('connect from:',clientaddress)
        lianj = 1
        t=threading.Thread(target=tcplink,args=(clientsock,clientaddress))  
        t.start()
        time.sleep(0.1)
        pass
    tcps.close()

