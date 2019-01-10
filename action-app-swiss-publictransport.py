#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *

import swiss_transport_info as STI

import io
import sys
import logging

CONFIG_INI = "config.ini"
logging.basicConfig()

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.ERROR)


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

    def __init__(self):
        """Initialize our app 
        - read the config file
        - initialize our API and Multilanguage Text handler class with 
          correct language 
        """

        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)

            # set log level according to config.ini
            if self.config["global"]["log_level"] == "DEBUG":
                _LOGGER.setLevel(logging.DEBUG)

            _LOGGER.debug(u"[__init__] - reading the config file {}".format(self.config))
            _LOGGER.debug(u"[__init__] - MQTT address is {}".format(MQTT_ADDR))

        except:
            self.config = None
            _LOGGER.error(u"[__init__] - not able to read config file!")

        # get the API and Multilanguage Text handler class
        try:
            self.sti = STI.SwissTransportInfo(self.config["secret"]["language"])
        except Exception as e:
            _LOGGER.error(e)

        # start listening to MQTT
        self.start_blocking()

    def _parse_slots(self, intent_message):
        """Parse the received slots into class variables
        """

        # default origin is our home station from config
        self.origin = self.config["secret"]["home_station"].encode("utf8")
        # defualt transport and destination is empty
        self.transport = u""
        self.destinantion = u""

        # Parse the query slots
        for (slot_value, slot) in intent_message.slots.items():
            print (slot_value)
            print (slot.first().value.encode("utf8"))
            if slot_value == "transport_type":
                self.transport = slot.first().value.encode("utf8")
            if slot_value == "from_station":
                self.origin = slot.first().value.encode("utf8")
            if slot_value == "to_station":
                self.destinantion = slot.first().value.encode("utf8")

        _LOGGER.debug("[_parse_slots] type: {}, from: {}, to: {}".format(
            self.transport, self.origin, self.destinantion
        ))

    # -------------------------------------------------------------------------
    # --> Sub callback function, one per intent
    # -------------------------------------------------------------------------

    # ===train_schedule_to intent action ======================================
    def train_schedule_to(self, hermes, intent_message):
        """fulfill the intent 
        """

        # get the slots from intent_message.intent
        self._parse_slots(intent_message)
        # call our API
        try:
            text_to_speak = self.sti.get_connection(self.origin, self.destinantion)
        except Exception as e:
            text_to_speak = unicode(str(e), "utf-8")
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, text_to_speak)

    # ===train_schedule_from_to intent action =================================
    def train_schedule_from_to(self, hermes, intent_message):
        """fulfill the intent 
        """

        # get the slots from intent
        self._parse_slots(intent_message)
        # call our API
        try:
            text_to_speak = self.sti.get_connection(self.origin, self.destinantion)
        except Exception as e:
            text_to_speak = unicode(str(e), "utf-8")

        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, text_to_speak)

    # ===station_timetable intent action ======================================
    def station_timetable(self, hermes, intent_message):
        """fulfill the intent 
        """

        # get the slots from intent
        self._parse_slots(intent_message)
        # call our API
        try:
            text_to_speak = self.sti.get_station_board(self.origin)
        except Exception as e:
            text_to_speak = unicode(str(e), "utf-8")

        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, text_to_speak)

    # -------------------------------------------------------------------------
    # --> Master callback function, triggered everytime an intent is recognized
    # -------------------------------------------------------------------------

    def master_intent_callback(self, hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        _LOGGER.debug(u"[master_intent_callback] - Intent: {}".format(coming_intent))
        if coming_intent == "cellerich:train_schedule_to":
            self.train_schedule_to(hermes, intent_message)
        if coming_intent == "cellerich:train_schedule_from_to":
            self.train_schedule_from_to(hermes, intent_message)
        if coming_intent == "cellerich:station_timetable":
            self.station_timetable(hermes, intent_message)

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()


if __name__ == "__main__":
    Swiss_Publictransport_app()
