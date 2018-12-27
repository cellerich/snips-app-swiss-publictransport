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
        
        Swiss Publictransport app
        Dispatch the intents to the corresponding actions
    """

    transport = ''
    origin = ''
    destinantion = ''

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
            logging.debug('read the config file')
            print 'Config readed'
            print MQTT_ADDR
        except :
            self.config = None
            print 'Error config'

        # start listening to MQTT
        self.start_blocking()

    def parse_slots(self,intent_message):

        # Parse the query slots, and fetch the weather forecast from Open Weather Map's API

        for (slot_value, slot) in intent_message.slots.items():
            if slot_value == 'transport_type':
                self.transport = slot[0].slot_value.value.value.encode('utf8')
            if slot_value == 'from_station':
                self.origin = slot[0].slot_value.value.value.encode('utf8')
            if slot_value == 'to_station':
                self.destinantion = slot[0].slot_value.value.value.encode('utf8')



    # --> Sub callback function, one per intent
    #===train_schedule_to intent action ==========================================
    def train_schedule_to(self, hermes, intent_message):
        # terminate the session first if not continue
        self.parse_slots(intent_message)
        intent = 'Absicht: {} nach {}'.format(self.transport, self.destinantion)
        hermes.publish_end_session(intent_message.session_id, intent.decode('utf8'))
        
        # action code goes here...
        print '[Received] {}'.format(intent)

        # if need to speak the execution result by tts
        #hermes.publish_start_session_notification(intent_message.site_id, "Noch eine Schlussbemerkung - eins", "")


    #===train_schedule_from_to intent action ==========================================
    def train_schedule_from_to(self, hermes, intent_message):
        # terminate the session first if not continue
        self.parse_slots(intent_message)
        intent = 'Absicht: {} von {} nach {}'.format(self.transport, self.origin, self.destinantion)
        hermes.publish_end_session(intent_message.session_id, intent.decode('utf8'))
        
        # action code goes here...
        print '[Received] {}'.format(intent)

        # if need to speak the execution result by tts
        #hermes.publish_start_session_notification(intent_message.site_id, "Noch eine Schlussbemerkung - eins", "")


    #===station_timetable intent action ==========================================
    def station_timetable(self, hermes, intent_message):
        # terminate the session first if not continue
        self.parse_slots(intent_message)
        intent = 'Absicht: {} '.format(self.transport)
        hermes.publish_end_session(intent_message.session_id, intent.decode('utf8'))
        
        # action code goes here...
        print '[Received] {}'.format(intent)

        # if need to speak the execution result by tts
        #hermes.publish_start_session_notification(intent_message.site_id, "Noch eine Schlussbemerkung - eins", "")


    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        print coming_intent
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
