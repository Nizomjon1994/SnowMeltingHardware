import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
from gpiozero import Buzzer
import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import datetime
import json
import sys
import os, urlparse
import serial
import urllib2, urllib

from config import Config

GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.OUT)
GPIO.output(40, GPIO.HIGH)

GPIO.setup(11, GPIO.OUT)
GPIO.output(11, GPIO.LOW)

modified_time = datetime.datetime.now()
sensor_id = 1112

client = mqtt.Client()
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

s = [0, 1]
heating_on_time_fixed = 0;

udb_sensor_id = Config.SENSOR_ID


def init_auth():
    if udb_sensor_id is None:
        print("Missing value from the Enjoy Weather")
        sys.exit(1)

    data = {
        'sensor_id': udb_sensor_id,
        'location': {
            'latitude': '',
            'longitude': ''
        },
        'created_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    udb_sensor_data = urllib.urlencode(data)
    url = "http://159.203.160.131/api/v1/sensor_list/"
    request = urllib2.Request(url,udb_sensor_data)
    response = urllib2.urlopen(request).read()
    print(response)

def init_mqtt():
    try:
        isMain = True
        client.username_pw_set('udblab', '12345')
        client.connect("159.203.160.131", 1883)
    except:
        try:
            client.username_pw_set('hlqbtvzv', 'rGA8NiRaD2KX')
            client.connect("m12.cloudmqtt.com", 13226, 60)
            isMain = False
        except:
            try:
                client.connect("broker.hivemq.com", 1883)
                isMain = False
            except:
                isMain = True
                client.username_pw_set('udblab', '12345')
                client.connect("159.203.160.131", 1883)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.loop_start()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("udblab/sensor/" + str(sensor_id) + "/heating/")


def on_disconnect(client, userdata, rc):
    print("Disconnected with result code " + str(rc))
    init_mqtt()


def on_message(client, userdata, msg):
    if (msg.payload == 'on'):
        GPIO.output(11, GPIO.HIGH)
        heating_on_time = time.time()
        print("Heating on time : " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(heating_on_time)))
    elif (msg.payload == 'off'):
        GPIO.output(11, GPIO.LOW)
        heating_off_time = time.time()
        print("Heating off time : " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(heating_off_time)))
        calculateOfDurationOfHeating(heating_off_time)


def calculateOfDurationOfHeating(heating_off_time):
    formatted_heating_on_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(heating_on_time_fixed))
    formatted_heating_off_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(heating_off_time))
    calculated_heating_time = heating_off_time - heating_on_time_fixed
    d = divmod(calculated_heating_time, 86400)
    h = divmod(d[1], 3600)  # hours
    m = divmod(h[1], 60)  # minutes
    s = m[1]  # seconds
    formatted_calculated_heating_time = '%d' % (d[0] * 86400 + h[0] * 3600 + m[0] * 60 + s)
    data = {
        'heating_on_time': str(formatted_heating_on_time),
        'heating_off_time': formatted_heating_off_time,
        'calculated_heating_time': formatted_calculated_heating_time
    }
    client.publish("udblab/sensor/" + str(sensor_id) + "/duration_of_heating/", json.dumps(data))
    print(data)


def readDHT():
    # This function will take the readings from the sensor, perform a not null validation and send the data to the calling fucntion
    DHTSensor = dht.DHT22  # Selecting the type of DHT Sensor
    DHTpin = 20
    DHTHumidity, DHTTemp = dht.read_retry(DHTSensor, DHTpin)
    DHTHumidity = "%.1f" % DHTHumidity
    DHTTemp = "%.1f" % DHTTemp
    if DHTHumidity is not None and DHTTemp is not None:
        return DHTHumidity, DHTTemp
    else:
        print('Failed to get reading from DHT22. Try again!')
        return "Data Unavailable", "Data Unavailable"


def readBMP():
    # This function will tkae the readings from the sensor, perform a not null validation and send the data to the calling function
    BMPSensor = BMP085.BMP085()  # Selecting the type of BMP Sensor, the sensor used in my station in BMP180 but the class is only available for BMP085, both use the same class and fucntions and connection circuit
    BMPTemp = '{0:0.2f}'.format(BMPSensor.read_temperature())
    pressure = '{0:0.2f}'.format(BMPSensor.read_pressure())
    altitude = '{0:0.2f}'.format(BMPSensor.read_altitude())
    seaLevelPressure = '{0:0.2f}'.format(BMPSensor.read_sealevel_pressure())
    if BMPTemp is not None and pressure is not None and altitude is not None and seaLevelPressure is not None:
        return BMPTemp, pressure, altitude, seaLevelPressure
    else:
        print('Failed to get reading from BMP180. Try again!')
        return "Data Unavailable", "Data Unavailable"


def readArduino():
    try:
        arduinoSerial = serial.Serial('/dev/ttyACM0', 9600)  # The port to which the arduino is connected to.
        readSerial = arduinoSerial.readline()
        # readSerialSplit = readSerial.split("*")
        return readSerial
    except:
        return readSerial


def main():
    DHTHumidity, DHTTemp = readDHT()
    wind_speed = readArduino()
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    data = {
        'temp': DHTTemp,
        'hum': DHTHumidity,
        'wind_speed': wind_speed,
        'date': formatted_time}
    client.publish("udblab/sensor/" + str(sensor_id) + "/current_data/", json.dumps(data))
    print(data)

    # weatherData=urllib.urlencode(data)
    # path="http://159.203.160.131/api/v1/weather/"
    # request=urllib2.Request(path,weatherData)
    # page=urllib2.urlopen(request).read()

    # BMPTemp,pressure,altitude,seaLevelPressure=readBMP()
    # latitude,longitude=getLocation()
    # temperature=str(((float(DHTTemp)+float(BMPTemp)))/2)
    # arduinoReading = readArduino()
    # rainfall = arduinoReading[0]
    # light = arduinoReading[1]
    # co2 = arduinoReading[2]
    # print('Rainfall data from Uno ' + rainfall)
    # print('Light Intensity data from Uno ' + light)
    # print('CO2 Concentration from Uno ' + co2)

init_mqtt()
init_auth()
while True:
    main()
    time.sleep(3)
