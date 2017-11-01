import os
import sys
import time
import json
import requests
import docker
import traceback

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

client = docker.APIClient(base_url='unix://var/run/docker.sock')
highClient = docker.from_env()

def getRoleName(aInContainer):
	val = 'not_duplo'
	try:
		for env in aInContainer.attrs['Config']['Env']:
			if env.startswith("ROLE_NAME="):
				return env.split("ROLE_NAME=")[1]
	except:
		val = 'unknown'

	return val		

def getContainersJson():
	lJsonData = "["
	lContainers = highClient.containers.list()
	for lCont in lContainers:
		lRoleName = getRoleName(lCont)
		lName = lCont.name.lower()
		lContData = '{ "Id":"' + lCont.id + '", "Image":"' + lCont.attrs['Config']['Image'] + '", "Role":"' + lRoleName + '", "Status":"' + lCont.status + '", "Names":["' + lCont.name + '"]}'
		if lJsonData != "[":
			lJsonData = lJsonData + ", " + lContData
		else:
			lJsonData = lJsonData + lContData
	lJsonData = lJsonData + " ]"
	return lJsonData

def processGoalState(aInState):
	lExpectedContainers = {}
	for index, item in enumerate(aInState["Pods"]):
		lName = item["DuploId"].lower()
		lExpectedContainers[lName] = lName
		try:
			print("Processing expected container {}".format(lName))
			processContainer(item)
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			el = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
			print('processContainer {} threw an error {}'.format(lName, el))

	processExtraneousContainers(lExpectedContainers)			

def processContainer(item):
	contId = item["DuploId"]
	print(json.dumps(item))
	cont = doesContainerExists(contId)
	if cont is None:
		print("Container {} is missing".format(contId))
		createAndStartContainer(contId, item)
	else:
		print("Container {} exists. status {}".format(contId, cont.status))	
		if cont.status != "running":
			print("Container starting {} ".format(contId))
			cont.start()
			print("Container started {} ".format(contId))

def doesContainerExists(aInName):
	try:
		conts = highClient.containers.get(aInName)
		return conts
	except docker.errors.NotFound as e:
		return None

def createAndStartContainer(aInId, aInItem):
	lImgName = aInItem["Image"]
	lImg = doesImageExist(lImgName)
	if lImg is None:
		print("Container Image {} is missing. Downloading".format(lImgName))
		highClient.images.pull(aInItem["Image"])
		print("Container Image {} download complete".format(lImgName))
	else:
		print("Container Image {} exists.".format(lImgName))

	url = client._url("/containers/create?name=" + aInId)
	r = client._post_json(url, data=aInItem)
	processStatusCode(r)
	print("SUCCESS CREATING CONTAINER. STARTING ======")
	cont = doesContainerExists(aInId)
	cont.start()

def doesImageExist(aInImage):
	try:
		lImg = highClient.images.get(aInImage)
		return lImg
	except docker.errors.ImageNotFound as e:
		return None

def processExtraneousContainers(aInExpectedNames):
	lContainers = highClient.containers.list()
	for lCont in lContainers:
		lName = lCont.name.lower()
		if not lName.startswith("duplo_"):
			continue
		print("Processing extraneous check for container {}".format(lCont.name))
		if not aInExpectedNames.has_key(lName):
			print("Container {} is unexpected".format(lName))
			cont = doesContainerExists(lName)
			cont.remove(force=True)
			print("Container {} has been removed".format(lName))
			


def processStatusCode(r):
	try:
		r.raise_for_status()
	except:
		printError(r.text)
		sys.exit()     

def printError(msg) :
	print(bcolors.FAIL + "FAILURE: **** " + msg +  bcolors.ENDC)  

def printSuccess(msg) :
	print(bcolors.OKGREEN + "SUCCESS: ++++ " + msg +  bcolors.ENDC)                  