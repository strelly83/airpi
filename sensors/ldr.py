import mcp3008
import sensor
import math
class Analogue(sensor.Sensor):
	requiredData = ["adcPin","measurement","sensorName"]
	optionalData = ["pullUpResistance","pullDownResistance"]
	def __init__(self, data):
		self.adc = mcp3008.MCP3008.sharedClass
		self.adcPin = int(data["adcPin"])
		self.valName = data["measurement"]
		self.sensorName = data["sensorName"]
		self.pullUp, self.pullDown = None, None
		if "pullUpResistance" in data:
			self.pullUp = int(data["pullUpResistance"])
		if "pullDownResistance" in data:
			self.pullDown = int(data["pullDownResistance"])
		class ConfigError(Exception): pass
		if self.pullUp!=None and self.pullDown!=None:
			print "Please choose whether there is a pull up or pull down resistor for the " + self.valName
			raise ConfigError
		self.valUnit = "Lux"
		self.valSymbol = "Lux"
		if self.pullUp==None and self.pullDown==None:
			self.valUnit = "millvolts"
			self.valSymbol = "mV"

	def getVal(self):
		result = self.adc.readADC(self.adcPin)
		if result == 0:
			#print "Check wiring for the " + self.sensorName + " measurement, no voltage detected on A$
			return None
		if result == 1023:
			#print "Check wiring for the " + self.sensorName + " measurement, full voltage detected on$
			return 0.0
		vin = 3.3
		vout = float(result)/1023 * vin

		if self.pullDown!= None:
			#Its a pull down resistor
			resOut = (self.pullDown*vin)/vout - self.pullDown
		elif self.pullUp!= None:
			resOut = self.pullUp/((vin/vout)-1)
		else:
			resOut = vout*1000
		resOut = float(5e9) * (math.log10(resOut)**-12.78)
		resOut = float("%.2f" % resOut)
		return resOut


