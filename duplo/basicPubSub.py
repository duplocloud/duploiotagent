'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse


# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


def pubSubGetClient():

    # Read in command-line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
    parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                        help="Use MQTT over WebSocket")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                        help="Targeted client id")
    parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")
    parser.add_argument("-d", "--deviceid", action="store", required=True, dest="deviceid", help="device id in duplocloud")
    
    args = parser.parse_args()
    host = args.host
    rootCAPath = args.rootCAPath
    certificatePath = args.certificatePath
    privateKeyPath = args.privateKeyPath
    useWebsocket = args.useWebsocket
    clientId = args.clientId
    topic = args.topic
    deviceid = args.deviceid

    if args.useWebsocket and args.certificatePath and args.privateKeyPath:
        parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
        exit(2)

    if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
        parser.error("Missing credentials for authentication.")
        exit(2)

    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.WARNING)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    
    lAWSIoTMQTTClient = None  

    if useWebsocket:
        lAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
        lAWSIoTMQTTClient.configureEndpoint(host, 443)
        lAWSIoTMQTTClient.configureCredentials(rootCAPath)
    else:
        lAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
        lAWSIoTMQTTClient.configureEndpoint(host, 8883)
        lAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    # AWSIoTMQTTClient connection configuration
    lAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    lAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    lAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    lAWSIoTMQTTClient.configureConnectDisconnectTimeout(30)  # 10 sec
    lAWSIoTMQTTClient.configureMQTTOperationTimeout(30)  # 5 sec
    return lAWSIoTMQTTClient, topic, deviceid

def startPubSub(aInAWSIoTMQTTClient, aInTopic):
    # Connect and subscribe to AWS IoT
    aInAWSIoTMQTTClient.connect()
    #aInAWSIoTMQTTClient.subscribe(aInTopic, 1, customCallback)
    time.sleep(10)

    # Publish to the same topic in a loop forever
    loopCount = 0
    while True:
        aInAWSIoTMQTTClient.publish(aInTopic, "New Message ", 1)
        loopCount += 1
        time.sleep(5)
