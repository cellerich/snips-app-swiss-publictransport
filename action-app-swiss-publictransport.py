#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
# from tesla_api import TeslaApiClient

import io
import logging

CONFIG_INI = "config.ini"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class Swiss_Publictransport_app(object):
    """Class used to wrap action code with mqtt connection
        
        Tesla appp
        Dispatch the intents to the corresponding actions
    """

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
            logging.debug('read the config file')
            print 'Config readed'
            print self.config
            print MQTT_ADDR
        except :
            self.config = None
            print 'Error config'

        # start listening to MQTT
        self.start_blocking()
        
    # --> Sub callback function, one per intent

    #===train_schedule_to intent action ==========================================
    def train_schedule_to(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "Intent - Zug nach")
        
        # action code goes here...
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)
        print self.config

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, "Session Notification", "")


    #===train_schedule_from_to intent action ==========================================
    def train_schedule_from_to(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "Intent - Zug von - nach")
        
        # action code goes here...
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)


    #===station_timetable intent action ==========================================
    def station_timetable(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "Intent - nächster Zug")
        
        # action code goes here...
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)


    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == 'cellerich:train_schedule_to':
            self.train_schedule_to(hermes, intent_message)
        if coming_intent == 'cellerich:train_schedule_from_to':
            self.train_schedule_from_to(hermes, intent_message)
        if coming_intent == 'cellerich:station_timetable':
            self.station_timetable(hermes, intent_message)


    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    Swiss_Publictransport_app()
