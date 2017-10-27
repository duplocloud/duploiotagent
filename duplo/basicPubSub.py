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

# AWSIoTMQTTClient
g_AWSIoTMQTTClient = None    

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


def pubSubValidateArg():

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

    args = parser.parse_args()
    host = args.host
    rootCAPath = args.rootCAPath
    certificatePath = args.certificatePath
    privateKeyPath = args.privateKeyPath
    useWebsocket = args.useWebsocket
    clientId = args.clientId
    topic = args.topic

    if args.useWebsocket and args.certificatePath and args.privateKeyPath:
        parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
        exit(2)

    if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
        parser.error("Missing credentials for authentication.")
        exit(2)

    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    if useWebsocket:
        g_AWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
        g_AWSIoTMQTTClient.configureEndpoint(host, 443)
        g_AWSIoTMQTTClient.configureCredentials(rootCAPath)
    else:
        g_AWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
        g_AWSIoTMQTTClient.configureEndpoint(host, 8883)
        g_AWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    # AWSIoTMQTTClient connection configuration
    g_AWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    g_AWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    g_AWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    g_AWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    g_AWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

def startPubSub():
    # Connect and subscribe to AWS IoT
    g_AWSIoTMQTTClient.connect()
    g_AWSIoTMQTTClient.subscribe(topic, 1, customCallback)
    time.sleep(2)

    # Publish to the same topic in a loop forever
    loopCount = 0
    while True:
        g_AWSIoTMQTTClient.publish(topic, "New Message " + str(loopCount), 1)
        loopCount += 1
        time.sleep(1)
