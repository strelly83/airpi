# 2014-02-16 khs 
# Data from AirPi-master to the emoncms server 
# /outputs/emoncms.py

import output
import datetime
import urllib2

class Emoncms(output.Output):

	requiredData = []
	optionalData = []

	def __init__(self,data):
		pass

	def outputData(self,dataPoints):
		
		out_to_emon = "http://192.168.XXX.XXX/emoncms/input/post.json?json={"
		
		for i in dataPoints:
			out_to_emon+=  i["name"] + ":" + str(i["value"]) + ","
		
		out_to_emon +="}&apikey=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

#		print(out_to_emon)
		urllib2.urlopen(out_to_emon)
		return True
