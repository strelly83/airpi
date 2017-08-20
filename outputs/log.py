# /outputs/log.py
import output
import datetime

class Log(output.Output):
	requiredData = []
	optionalData = []
	def __init__(self,data):
		pass
	def outputData(self,dataPoints):
		f = open('sensors.log', 'a')
		logline = '{"time":"'
		logline += str(datetime.datetime.now())
		logline += '",'
		for i in dataPoints:
			logline += '"' + i["name"] + '"' + ":" + '"' + str(i["value"]) + '"'
		
		logline += "}\n"

		print(logline)
		f.write(logline)
		f.close()

		return True

