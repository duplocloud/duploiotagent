from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import sys
import traceback
import argparse
import os
import json
import requests
import socket
import boto3
import datetime
from threading import Thread
import basicPubSub
from dockerutils import processGoalState
from dockerutils import getContainersJson

g_deviceid = ""

def invokePubSub():
	global g_deviceid
	while(True):
	    try:
			lAwsMQTTClient, ltopic, g_deviceid = basicPubSub.pubSubGetClient()
			print("++++++++ Device ID is {}".format(g_deviceid))
			basicPubSub.startPubSub(lAwsMQTTClient, ltopic)
	    except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			el = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
			print('pubsub threw an error {}'.format(el))
	    time.sleep(10)	

def getDeviceShadow():
	global g_deviceid
	try:
	    client = boto3.client('iot-data', region_name='us-west-2')
	    response = client.get_thing_shadow(thingName=g_deviceid)
	    streamingBody = response["payload"]
	    data = json.loads(streamingBody.read())
	    #formattedData = json.dumps(data["state"]["desired"], indent=4, sort_keys=True)
	    #print(formattedData)
	    processGoalState(data["state"]["desired"])
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		el = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
		print('getDeviceShadow threw an error {}'.format(el))

def updateDeviceShadow():
	global g_deviceid
	try:
		lData = getContainersJson()
		lJsonObj = json.loads(lData)
		lHostName = os.getenv('HOST_HOSTNAME', socket.gethostname())
		d = datetime.datetime.utcnow()

		status = '{ "ReportedAt":"' + d.isoformat() + '", "Containers":' +  json.dumps(lJsonObj) + ' }'
		status = '{ "reported":' +  status + ' }'
		status = '{ "state":' +  status + ' }'
		lJsonObj = json.loads(status)
		print(json.dumps(lJsonObj))
		client = boto3.client('iot-data', region_name='us-west-2')
		response = client.update_thing_shadow(thingName=g_deviceid, payload=json.dumps(lJsonObj))
		print('Updated Device Shadow')
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		el = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
		print('updateDeviceShadow threw an error {}'.format(el))

if __name__ == '__main__':
	print('Launching pubsub thread')
	lPubSubthrd = Thread(target = invokePubSub, args = [])
	lPubSubthrd.setDaemon(True)
	lPubSubthrd.start()

	while(True):
		time.sleep(12)
		print("++++++++ Device ID is {}".format(g_deviceid))
		getDeviceShadow()
		print("++++++++ Device ID is {}".format(g_deviceid))
		updateDeviceShadow()
						
