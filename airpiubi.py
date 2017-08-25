#!/usr/bin/env python
import time 						# Library for delays
import RPi.GPIO as GPIO 			# Library for using the GPIO ports
from  math import log1p,exp,log10 	# Library for math functions. No need for it if you'll get the raw data from the sensors
from ubidots import ApiClient  		# Ubidots Library
import Adafruit_DHT 				# Library from Adafruit to simplify the use of DHT sensor.

# Set up the SPI interface pins. Through SPI we can connect to the ADC MCP3008

SPICLK = 18
SPIMISO = 24
SPIMOSI = 23
SPICS = 25

GPIO.setmode(GPIO.BCM) 				# Set up BCM as numbering system for inputs
GPIO.setup(SPIMOSI, GPIO.OUT)		# Configure the SPI I/O
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# Setup Variables

dS = None 							# Ubidots Data source. We'll call Airpi
sensor = Adafruit_DHT.AM2302		# Especify the DHT sensor we will use 
									# You can change this line for other DHT sensors like this: Adafruit_DHT.DHT11 or Adafruit_DHT.DHT22
light = 0 							# Save  value of the LDR
UVI = 0								# Save  value of the UVI
air = 0								# Save  value of the Air Quality
#noise = 0 							# Save value of the Mic in
no2 = 0 							# Save value for Nitrogen dioxide level
co = 0 								# Save value for Carbon monoxide level
hum = 0 							# Save value for Humidity
temperature = 0 					# Save value for Temperature
vin = 3.3  							# Voltage reference for the ADC    

# Function to verify if the variable exists or not in your Ubidots account

def getVarbyNames(varName,dS):
	for var in dS.get_variables():
		if var.name == varName:
			return var
	return None

# Function from Adafruit to read analog values

def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  		# start clock low
        GPIO.output(cspin, False)     		# bring CS low

        commandout = adcnum
        commandout |= 0x18  				# start bit + single-ended bit
        commandout <<= 3    				# we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1
        GPIO.output(cspin, True)
        
        adcout >>= 1       					# first bit is 'null' so drop it
        return adcout

# Code to connect a Ubidots

try:
   api = ApiClient("A1E-363908325ca3565186e1baf247bc77631121") # Connect to Ubidots. Don't forget to put your own apikey
   
   for curDs in api.get_datasources():						# Check if there's any Data Source with the name AirPi
	if curDs.name == "AirPi":
		dS = curDs
		break
   if dS is None:
   	  dS = api.create_datasource({"name":"AirPi"})			# If doesn't exist it'll create a Data Source with the name Airpi
  
   lightValue = getVarbyNames("Light_level",dS)
   if lightValue is None:
	  lightValue = dS.create_variable({"name": "Light_level","unit": "lux"}) # Create a new Variable for light

   UVIValue = getVarbyNames("UVI_level",dS)
   if UVIValue is None:
	  UVIValue = dS.create_variable({"name": "UVI_level","unit": "unit"}) # Create a new Variable for UVI

   airquality = getVarbyNames("Smoke_level_concentration",dS)
   if airquality is None:
	  airquality = dS.create_variable({"name": "Smoke_level_concentration", "unit": "unit"}) # Create a new Variable for Smoke level
	  
   nitrogen = getVarbyNames("Nitrogen_dioxide_concentration",dS)
   if nitrogen is None:
	  nitrogen = dS.create_variable({"name": "Nitrogen_dioxide_concentration", "unit": "ppm"}) # Create a new Variable for NO2 level

   carbon = getVarbyNames("Carbon_monoxide_concentration",dS)
   if carbon is None:
	  carbon = dS.create_variable({"name": "Carbon_monoxide_concentration","unit": "ppm"}) # Create a new Variable for CO level
  

   temp = getVarbyNames("Temperature",dS)
   if temp is None:
	  temp = dS.create_variable({"name": "Temperature", "unit": "C"})	#Create a new Variable for temperature

   humidity = getVarbyNames("Humidity",dS)
   if humidity is None:
	  humidity = dS.create_variable({"name": "Humidity","unit": "%"}) # Create a new Variable for humidity

except:
   print("Can't connect to Ubidots")

while True:
    # Code to get light levels data
	light = readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS) # Read the analog pin where the LDR is connected
	light = float(light)/1023*vin						# Voltage value from ADC
	light = 10000/((vin/light)-1)						# Ohm value of the LDR, 10k is used as Pull up Resistor
	light = exp((log1p(light/1000)-4.125)/-0.6704)		# Linear aproximation from http://pi.gate.ac.uk/posts/2014/02/25/airpisensors/ to get Lux value
	
	# Code to get UVI levels data
	UVI = readadc(4, SPICLK, SPIMOSI, SPIMISO, SPICS)   # Read the analog pin where the UVI is connected
	UVI = (float(UVI)/1023*vin)/470					    # Voltage value from ADC / 470 (4.7Mohm / 1Mohm)
	UVI = UVI*1000						            	# mV value of the LDR
	UVI = UVI*(5.25/20)									# aproximation from http://pi.gate.ac.uk/posts/2014/02/25/airpisensors/ to get UVI value
	
	# Code to read Air Quality
	air = readadc(1, SPICLK, SPIMOSI, SPIMISO, SPICS)	# Read the analog input for the Smoke Level value	
	air = float(air)/1023*vin							# Voltage value from the ADC
	air = ((22000*vin)/air)-22000						# Ohm value of the AirQuality resistor, 22k is used as pull down resistor 
	#air = float(air/700)								#Reference value
	time.sleep(0.1)
		
	# Code to read NO2 and CO concentrations
	no2 = readadc(2, SPICLK, SPIMOSI, SPIMISO, SPICS)	# Read the analog input for the nitrogen value	
	no2 = float(no2)/1023*vin							# Voltage value from the ADC
	no2 = ((10000*vin)/no2)-10000						# Ohm value of the no2 resistor, 10k  is used as pull down resistor 
	no2 = float(no2/700)								#Reference value
	time.sleep(0.1)
	
	co = readadc(3, SPICLK, SPIMOSI, SPIMISO, SPICS)	# Read the analog input for the carbon value
	co = float(co)/1023*vin 							# Voltage value from the ADC
	co = ((360000*vin)/co)-360000						# Ohm Value of the co resistor, 360k is used as pull down resistor
	co = float(co/30000) 								#Reference value
	
	# Code to use the DHT sensor
	hum, temperature = Adafruit_DHT.read_retry(sensor, 4)
	if hum is not None and temperature is not None:
        	print 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, hum)
	else:
        	print 'Failed to get DHT sensor reading. Try again!'
	
	# Print sensor values to the console 

	print "light[lux]:", light
	print "UVI[unit]:", UVI
	print "air[unit]:", air	
	print "no2[ohm]:", no2
	print "co[ohm]:", co
	#print "noise[mv]", db

 	# Post values to Ubidots

	lightValue.save_value({'value':light})
	UVIValue.save_value({'value':UVI})
	smokeValue.save_value({'value':air})
	nitrogen.save_value({'value':no2})
	mic.save_value({'value':db})
	carbon.save_value({'value':co})	
	temp.save_value({'value':temperature})
	humidity.save_value({'value':hum})

GPIO.cleanup()						# Reset the status of the GPIO pins