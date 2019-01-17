#!/usr/bin/python
# coding=utf-8
# 22.12.2011
# Dieses Programm kommuniziert mit dem Gira RWM Diagnosetool
# und emuliert einen Rauchmelder

import serial
import signal
import sys
import binascii
import types
import time

# Seriellen Port eintragen
ser = serial.Serial('/dev/ttyUSB0', 9600,)

# Steuerzeichen
null = binascii.unhexlify("00")
stx  = binascii.unhexlify("02")
etx  = binascii.unhexlify("03")
ack  = binascii.unhexlify("06")

# Dieser Rauchmelder wird emuliert
group = "167B"
rm = "1777"

# Daten im Format [Req, Res] bzw [Req,[Res1, Res2, ... ,Resn]]
req_res = [ 
[stx+"SV"+etx,stx+"GI_RM_V00.70"+etx+ack],       # Softwareverion von der Gira Funk Schnittstelle
[stx+"01TESTA1"+etx,ack+stx+"Timeout"+etx],      # Sinn? Debug?
[stx+"GD:"+group+etx,ack],						 # Gruppe
[stx+"DA:"+rm+":05"+etx,[ack,stx+"REC"+etx,stx+"Done"+etx,ack]], # Anforderung zum RM auslesen
[stx+"SD:"+rm+""+etx,[                                           # Anforderung die ausgelesenen Daten zu übermitteln
stx+"0001:111633CA"+etx, # Serial
stx+"0002:014D0145"+etx, # ?
stx+"0003:00059A21"+etx, # Betriebszeit
stx+"0004:005C0000"+etx, # Rauchkammerwert / Anz Rauchalarm / Verschmutzungsgrad
stx+"0005:01DB5252"+etx, # Batt (V) / Temp 1 / Temp 2
stx+"0006:00000000"+etx, # Anzahl Thremoalarm / Anzahl Testalarm / Anzahl Alarm Draht / Anzahl Alarm Funk
stx+"0007:00000000"+etx, # Anz Testalarm Draht / Anz Testalarm Funk
stx+"0014:FFFFFFFF"+etx, # ?
stx+"0015:FFFFFFFF"+etx,
stx+"0016:FFFFFFFF"+etx,
stx+"0017:FFFFFFFF"+etx,
stx+"0018:FFFFFFFF"+etx,
stx+"0019:FFFFFFFF"+etx,
stx+"001A:FFFFFFFF"+etx,
stx+"001B:FFFFFFFF"+etx,
stx+"001C:FFFFFFFF"+etx,
stx+"001D:FFFFFFFF"+etx,
stx+"001E:FFFFFFFF"+etx,
stx+"001F:FFFFFFFF"+etx,
stx+"0020:FFFFFFFF"+etx,
stx+"0021:FFFFFFFF"+etx,
stx+"0022:FFFFFFFF"+etx,
stx+"0023:FFFFFFFF"+etx,
stx+"0024:FFFFFFFF"+etx,
stx+"0025:FFFFFFFF"+etx,
stx+"0026:FFFFFFFF"+etx,
stx+"0027:FFFFFFFF"+etx,
stx+"0028:FFFFFFFF"+etx,
stx+"0029:FFFFFFFF"+etx,
stx+"002A:FFFFFFFF"+etx,
stx+"002B:FFFFFFFF"+etx,
stx+"002C:FFFFFFFF"+etx,
stx+"002D:FFFFFFFF"+etx,
stx+"002E:FFFFFFFF"+etx,
stx+"002F:FFFFFFFF"+etx,
stx+"0030:FFFFFFFF"+etx,
stx+"0031:FFFFFFFF"+etx,
stx+"0032:FFFFFFFF"+etx,
stx+"0033:FFFFFFFF"+etx,
stx+"0034:FFFFFFFF"+etx,
stx+"0035:FFFFFFFF"+etx,
stx+"0036:00740311"+etx,
stx+"0037:20000000"+etx,
stx+"0038:000A8B11"+etx,
stx+"0039:20000000"+etx,
stx+"003A:000A8B11"+etx,
stx+"003B:20000000"+etx,
stx+"0064:00000001"+etx,
stx+"Timeout"+etx]
],
[stx+"DA:"+rm+":01"+etx,ack+stx+"Done"+etx],        # Datenübertragung bestätigen?
[stx+"DA:"+rm+":04"+etx,ack+stx+"Timeout"+etx],     # 
[stx+"X"+etx,ack]                                   # Abbruchtaste in Gria Software - erw. Response bisher unbekannt
]

# Saubes Beenden mit Strg+C
def process_sigint(signum, frame):
	print "Ende"
	ser.close()
	sys.exit(0)

def process_data(p_data):
	for rr in req_res:
		if rr[0] == p_data:
			if type(rr[1]) == types.ListType:
				print "AFound",rr[0],"-->"
				for rrr in rr[1]:
					print ">",rrr
					ser.write(rrr)
#					time.sleep(0.1)
			else:
				print "Found",rr[0],"-->",rr[1]
				ser.write(rr[1])


signal.signal(signal.SIGINT, process_sigint)
state = 0
data = ""

while 1:
	read = ser.read()
	if read == null or read == ack:
		print "Got 1Data ", read, "->", binascii.b2a_hex(read)
		process_data(read)
		continue
	if read == stx:
#		print "Begin"
		state = 1
		data = ""
	if read == etx:
		state = 0
		data = data + read
		print "Got Data ", data, "->", binascii.b2a_hex(data)
		process_data(data)
	if state == 1:
		data = data + read


