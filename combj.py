#!/usr/bin/python
# -*- coding: UTF-8 -*-  
import serial
import binascii 
import os  
os.system("/etc/init.d/./kaiji.sh")
#import serial
import socket
import time
import threading 
import re
#baojing = 0
global datas 
#SENDERIP = '192.168.1.189'
#MYPORT = 20000

MYGROUP_zb = '239.255.255.250'
MYPORT_zb =37020
ADDR_zb =(MYGROUP_zb,MYPORT_zb)

HOST = '192.168.1.105' 
#PORT = 20000
#ADDR = (HOST, PORT)
bjwd=open('/etc/init.d/temp','r')
wendu=bjwd.read()
#wendu1=wendu[8:10]
#wendu2=wendu[10:12]
#wendu1 = binascii.b2a_hex(wendu1)
#wendu2 = binascii.b2a_hex(wendu2)
#print (wendu1)
#print (wendu2)
with open('/root/port','r') as aa:
    PORT1 = aa.read();
ADDR = (HOST, int(PORT1))
BUFSIZ = 1200

#import socket
#os.system("/etc/init.d/./kaiji.sh") 
#SENDERIP = socket.gethostbyname(socket.getfqdn(socket.gethostname()))

#os.system("/etc/init.d/./kaiji.sh")   
with open('/etc/config/network','r') as fin:
    text = fin.read();
regex = r'config interface \'lan\'([\s\S]*?)config interface \'wan\''
matches = re.findall(regex, text)
for match in matches:
    #fout.write(match)
    pass
 
regex = r'macaddr \'([\s\S]*?)\''
matches = re.findall(regex, match)
for mac_g in matches:
    print(mac_g)
    
regex = r'ipaddr \'([\s\S]*?)\''
matches = re.findall(regex, match)    
for addr_g in matches:
    print(addr_g)    
           
regex = r'gateway \'([\s\S]*?)\''
matches = re.findall(regex, match)
for gateway_g in matches:
    print(gateway_g)

regex = r'dns \'([\s\S]*?)\''
matches = re.findall(regex, match)
for dns_g in matches:
    print(dns_g)

regex = r'netmask \'([\s\S]*?)\''
matches = re.findall(regex, match)
for netmask_g in matches:
    print(netmask_g)
   
 
fin.close() 
old_file='/etc/config/network'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
    socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind( ('', 8000) )

#import serial
ser = serial.Serial('/dev/ttyS1', 115200)
#os.system("/etc/init.d/./kaiji.sh")

#cewen = ("\xaa\x06\x07\x31\x01\x40\x1f\x48\xeb\xaa")
cewen = ("\xaa\x04\x07\x31\xe6\xeb\xaa")
ff = ("\x02\x19\x40\x07\x01\x72\x00\x65\x01\x72\xcd")
f=open('/sys/class/gpio/export','w')
f.write('40')
f.close()
time.sleep(0.05)
f=open('/sys/class/gpio/gpio40/direction','w')
f.write('out')
f.close()
f=open('/sys/class/gpio/gpio40/value','w')
f.write('1')
f.close()

f=open('/sys/class/gpio/export','w')
f.write('39')
f.close()
time.sleep(0.05)
f=open('/sys/class/gpio/gpio39/direction','w')
f.write('out')
f.close()
f=open('/sys/class/gpio/gpio39/value','w')
f.write('0')
f.close()



def receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
        socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sock.bind( ('', int(PORT1)) )
    global datas
    while 1:
        try:
            data, addr = sock.recvfrom(1200)
        except socket.error, e:
            pass
        else:
            if "\x02"==data[0] and "\x18"==data[1] and "\x41"==data[2]:
                #wd = binascii.b2a_hex(data)
                f=open('/etc/init.d/temp','w')
                f.write(data)
                f.close()
    
                print('ok')
        ser.write(data)
        print "Receive data!"
       # else: pass 
                #ser.write(data)
            #print('hwzn1')
            #time.sleep(0.2)
       
       
    
threads = []
t1 =threading.Thread(target=receiver,name='')
threads.append(t1)               
#t2 =threading.Thread(target=baojing2,name='')
#threads.append(t2)
#t3 =threading.Thread(target=baojing1,name='')
#threads.append(t3)
if __name__ == "__main__":
    #t1 =threading.Thread(target=receiver,name='')
    #t1.start()
    for t in threads:
        t.setDaemon(True)
        t.start()
    global datas
    datas = ''
    ser.write(cewen)
    while 1:
        time.sleep(0.75)
        #ser.write(cewen)
        time.sleep(0.02)
        while ser.inWaiting() > 0:
            datas += ser.read(1)
        if datas != '':
            print('hwzn111')
            jgwz2=binascii.b2a_hex(datas).decode('utf-8')
            f=open('/etc/init.d/temp','w')
            f.write(jgwz2)
            f.close()
            sock.sendto(datas , ADDR)
            if len(datas)==11:
                if ff[0]==datas[0] and ff[1]==datas[1] and ff[2]==datas[2]:
                    #print(datas)
                    f=open('/sys/class/gpio/gpio39/value','w')
                    f.write('1')
                    f.close()
                    #ser.write(datas)
                    #time.sleep(0.05)
                    f=open('/sys/class/gpio/gpio39/value','w')
                    f.write('0')
                    f.close()
                    #print (datas[8])
                    if wendu[4]<datas[8] or (wendu[4]==datas[8] and wendu[5]<datas[9]): 
                        f=open('/sys/class/gpio/gpio40/value','w')
                        f.write('0')
                        f.close()
	                os.system("/etc/init.d/./baojing.sh")
	                f=open('/sys/class/gpio/gpio40/value','w')
                        f.write('1')
                        f.close()
            
            else:
                pass
                f=open('/sys/class/gpio/gpio40/value','w')
                f.write('1')
                f.close()

        datas=''
        #time.sleep(0.1)
        f=open('/sys/class/gpio/gpio40/value','w')
        f.write('1')
        f.close()
        #datas = ser.inWaiting()
        #time.sleep(0.2) 
        
