from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import basicPubSub

basicPubSub.pubSubValidateArg()

basicPubSub.startPubSub()

