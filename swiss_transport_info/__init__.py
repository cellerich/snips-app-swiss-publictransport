#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Cello Spring <cello@cellerich.ch>
https://www.cellerich.ch
Licensed under MIT. All rights reserved.
"""

import urllib as urlp
import requests

import json
import logging
import dateutil.parser
import gettext

from datetime import datetime
from . import exceptions

logging.basicConfig()

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)
_RESOURCE = "http://transport.opendata.ch/v1/"
_LANGUAGES = ["en", "de"]


class SwissTransportInfo(object):
    def __init__(self, language="en"):
        """Initialize the Class with the excpected output language
            
        Keyword arguments:
        language    -- language for text output (default = 'en')
        """
        self._ = gettext.gettext

        if language in _LANGUAGES:
            self.language = language
        else:
            _LOGGER.error('Language "{}" is not available.'.format(language))
            raise exceptions.SwissTransportInfoError(
                self._('Language "{}" is not available').format(language) + "."
            )

        if language != "en":
            try:
                # try to see if the language is supported
                lang = gettext.translation(
                    "snips", localedir="./locale", languages=[language]
                )
                lang.install()
                self._ = lang.gettext

            except Exception as e:
                _LOGGER.error(u"Cannot load the wanted language: {}".format(e))
                raise exceptions.Data2TextMLTranslationError(e)

    def get_station_board(self, station_name, connections=4, departure_time=None):
        """return the stationboard info for the given station

        Keyword arguments:
        station_name    -- the name of the public transport station 
        connections     -- the number of connections we want back (default 1)
        departure_time  -- to get the stationboard for a specific date and time (default is now)
        """

        odta = _OpendataTransport()
        try:
            dtml = _Data2TextML(self._)
        except exceptions.Data2TextMLTranslationError as e:
            raise exceptions.SwissTransportInfoError(
                self._(
                    "Sorry, I cannot load the translations for the language {}"
                ).format(language)
                + "."
            )

        try:
            return dtml.get_stationboard_text(
                odta.get_stationboard(station_name, connections)
            )
        except exceptions.Data2TextMLConcatenateError:
            raise exceptions.SwissTransportInfoError(
                self._(
                    "Sorry! I received some invalid data, please try again with another station"
                )
                + "."
            )
        except exceptions.OpendataTransportConnectionError as e:
            raise exceptions.SwissTransportInfoError(
                self._(
                    "Sorry! I dont have a connection to the Swiss Transport Infos at the moment"
                )
                + ". "
                + self._("Please try again later")
                + "."
            )
        except exceptions.OpendataTransportParseError as e:
            raise exceptions.SwissTransportInfoError(
                self._("Sorry! I have trouble understanding the data I received")
                + "."
                + self._("You might have a talk with the programmer of this App")
                + "!"
            )

    def get_connection(
        self, from_station, to_station, connections=1, departure_time=None
    ):
        """Returns the connection information for the given stations.
    
        Keyword arguments:
        from_station    -- the name of the origin public transport station 
        to_station      -- the name of the destination public transport station 
        connections     -- the number of connections we want back (default 1)
        departure_time  -- to get the connecions for a specific date and time (default is now)
        """

        odta = _OpendataTransport()
        try:
            dtml = _Data2TextML(self._)
        except exceptions.Data2TextMLTranslationError as e:
            raise exceptions.SwissTransportInfoError(
                self._(
                    "Sorry, I cannot load the translations for the language {}"
                ).format(language)
                + "."
            )

        try:
            return dtml.get_connection_text(
                odta.get_connections(from_station, to_station, connections)
            )
        except exceptions.Data2TextMLConcatenateError as e:
            raise exceptions.SwissTransportInfoError(
                self._(
                    "Sorry! I received some invalid data, please try again with another station"
                )
                + "."
            )
        except exceptions.OpendataTransportConnectionError as e:
            raise exceptions.SwissTransportInfoError(
                self._(
                    "Sorry! I dont have a connection to the Swiss Transport Infos at the moment"
                )
                + ". "
                + self._("Please try again later")
                + "."
            )
        except exceptions.OpendataTransportParseError as e:
            raise exceptions.SwissTransportInfoError(
                self._("Sorry! I have trouble understanding the data I received")
                + "."
                + self._("You might have a talk with the programmer of this App")
                + "!"
            )


###############################################################################
#
# Class to handle Data to Text in multiple languages
#
###############################################################################


class _Data2TextML(object):
    """A class to render the transport connections data into speakable text
    The module uses 'gettext' for the translation into the available languages

    The module is depending on the opendata_transport_api module and will
    receive the output data of its functions
    """

    # TODO: create functions no connection (with suggestion)
    # TODO: implement ngettext for numbers :-)

    def __init__(self, _):
        """Initialize the Class with the needed language

        Keyword arguments:
        _           -- translation routine from "gettext" 
        """

        self._ = _

    def _get_time_string(self, iso_time):
        """Returns the Hour and Minute of a iso formatted date string
        
        Keyword arguments:
        iso_time        -- string in the form "2019-01-02T09:32:00+0100"
        """

        return dateutil.parser.parse(iso_time).strftime("%H:%M")

    def _get_duration_string(self, duration):
        """Returns the ML translated Hour and Minute of a formatted duration string
        
        Keyword arguments:
        duration        -- string in the form "00d01:38:00"
        """
        duration_format = self._("%H hours %M minutes")
        return datetime.strptime(duration, "%fd%H:%M:%S").strftime(duration_format)

    def _get_platform_string(self, platform):
        """Returns the platform if available or an empty string"""
        platform_format = self._("on platform {}")
        if platform == None:
            return ""
        else:
            return platform_format.format(platform)

    def get_stationboard_text(self, sb_data):
        """Returns the speakable text for the timetable data provided
    
        Keyword arguments:
        sb_data         -- dictionary from the get_stationboard function of the API
        """

        """--------------TEXT TO BE SPOKEN --------------------------------------------
        The next train from Bern is number 'S 7' and leaves at 16:30 from platform 24 
        towards Worb Dorf. There are 10 stops before the final destination. 
        Other connections are: 
        number 'S 3' towards Biel leaving 16:30 from platform 12 with 10 stops; 
        'IC 1' towards St. Gallen leaving 16:32 from platform 7 with 5 stops and 
        'S 9' towards Unterzollikofen leaving 16:32 from platform 22 with 5 stops.
        ----------------------------------------------------------------------------"""

        # reformat input data (mainly the date/time strings)
        for connection in sb_data:
            connection["departure"] = self._get_time_string(connection["departure"])
            connection["platform"] = self._get_platform_string(connection["platform"])

        # try to concatenate the output data we need
        try:
            # create the sentences
            t_frag_1 = (
                self._(
                    "The next connection from {origin} is {transport} and leaves at {departure} {platform} towards {destination}"
                )
                + ". "
                + self._("There are {stops} stops before the final destination")
                + ". "
            )

            sentence = unicode(t_frag_1, "utf-8").format(**sb_data[0])

            sentence += self._("Other connections are") + ": "

            t_frag_2 = (
                self._(
                    "{transport} towards {destination} leaving {departure} {platform} with {stops} stops"
                )
                + "; "
            )

            sentence += unicode(t_frag_2, "utf-8").format(**sb_data[1])

            t_frag_3 = (
                self._(
                    "{transport} towards {destination} leaving {departure} {platform} with {stops} stops"
                )
                + " "
                + self._("and")
                + " "
            )
            sentence += unicode(t_frag_3, "utf-8").format(**sb_data[2])

            t_frag_4 = (
                self._(
                    "{transport} towards {destination} leaving {departure} {platform} with {stops} stops"
                )
                + "."
            )
            sentence += unicode(t_frag_4, "utf-8").format(**sb_data[3])

            _LOGGER.debug(u"concatenated sentence: {}".format(sentence))
            return sentence

        except Exception as e:
            _LOGGER.error(u"Can not concatenate the input data: {}".format(e))
            raise exceptions.Data2TextMLConcatenateError(e)

    def get_connection_text(self, cn_data):
        """Returns the speakable text for the connection data
    
        Keyword arguments:
        cn_data         -- dictionary from the get_connections function of the API
        """

        """--------------TEXT TO BE SPOKEN --------------------------------------------
        Your next connection from _Davos Platz_ to _Lausanne_ leaves at 15:26. 
        It has the number RE 1050 on Platform 1. 
        The journey takes 4 hours and 50 minutes, you will arrive in Lausanne at 20:16.
        There are 4 transfers: 
        - in Klosters Platz - 15:57, number RE 1350 on platform 2
        - in Landquart - 16:49, number IC 3 on platform 3.
        - in Zürich HB - 18:02, number IC 8 on platform 31
        - in in Bern - 19:04 number IR 15 on platform 3.
        ----------------------------------------------------------------------------"""

        # we just use the first entry in list
        data = cn_data[0]
        # reformat input data (mainly the date/time strings)
        try:
            data["departure"] = self._get_time_string(data["departure"])
            data["arrival"] = self._get_time_string(data["arrival"])
            data["platform"] = self._get_platform_string(data["platform"])
            data["duration"] = self._get_duration_string(data["duration"])
            for transfer in data["transfers"]:
                transfer["platform"] = self._get_platform_string(transfer["platform"])
                transfer["departure"] = self._get_time_string(transfer["departure"])

            _LOGGER.debug(u"reformatted data: {}".format(data))

        except Exception as e:
            _LOGGER.error(u"Error reformatting data: {}".format(e))
            raise exceptions.Data2TextMLConcatenateError(e)

        # try to concatenate the output data we need
        try:

            # create the sentences
            t_frag_1 = (
                self._("Your next connection from {from} to {to} leaves at {departure}")
                + ". "
            )
            sentence = unicode(t_frag_1, "utf-8").format(**data)

            t_frag_2 = self._("It has the number {first_transport} {platform}") + ". "
            sentence += unicode(t_frag_2, "utf-8").format(**data)

            t_frag_3 = (
                self._(
                    "The journey takes {duration}, you will arrive in {to} at {arrival}"
                )
                + ". "
            )
            sentence += unicode(t_frag_3, "utf-8").format(**data)

            if data["transfer_count"] > 0:
                t_frag_4 = self._("There are {transfer_count} transfers") + ": "
                sentence += unicode(t_frag_4, "utf-8").format(**data)

                t_frag_loop = (
                    self._("- in {station}: {departure}, {transport} {platform}") + ". "
                )

                # add all the transfer data
                for transfer in data["transfers"][1:]:
                    sentence += unicode(t_frag_loop, "utf-8").format(**transfer)

            _LOGGER.debug(u"concatenated sentence: {}".format(sentence))
            return sentence

        except Exception as e:
            _LOGGER.error(u"Can not concatenate the input data: {}".format(data))
            raise exceptions.Data2TextMLConcatenateError(e)


###############################################################################
#
# Class to handle the Opendata Transport API
#
###############################################################################


class _OpendataTransport(object):
    """A class to get a information from the Opendata Transport API."""

    # small routine to check if the transport category already is in the transport number, then we just use the number
    def _strip_cat_number(self, category, number):
        """small routine to check if the transport category already is in the transport number, 
        then we just use the number
        """
        if category in number:
            return number
        else:
            return category + " " + number

    def get_stationboard(self, station_name, entries=1, departure_time=None):
        """Returns the dictonary with stationboard information for the given station.
    
        Keyword arguments:
        station_name    -- the name of the public transport station 
        entries         -- the number of connections we want back (default 1)
        departure_time  -- to get the stationboard for a specific date and time (default is now)
        """
        if departure_time == None:
            query = {"station": station_name, "limit": entries}
        else:
            query = {
                "station": station_name,
                "limit": entries,
                "datetime": departure_time.isoformat(),
            }
        url = _RESOURCE + "stationboard?" + urlp.urlencode(query)

        # try to load the data from transport opendata api
        try:
            result = requests.get(url)
            #sb = result.json()
            
            sb = json.loads(result.content.decode('utf-8'))
            _LOGGER.debug(
                u"Response from transport.opendata.ch: {}".format(result.status_code)
            )
        except Exception as e:
            _LOGGER.error(u"Can not load data from transport.opendata.ch: {}".format(e))
            raise exceptions.OpendataTransportConnectionError(e)

        # try to parse the data we need
        try:
            connections = []
            for connect in sb["stationboard"]:
                connection = dict()
                connection["origin"] = sb["station"]["name"]
                connection["destination"] = connect["to"]
                connection["departure"] = connect["stop"]["departure"]
                connection["platform"] = connect["stop"]["platform"]
                connection["transport"] = self._strip_cat_number(
                    connect["category"], connect["number"]
                )
                connection["stops"] = len(connect["passList"]) - 1
                connections.append(connection)

            _LOGGER.debug(u"Parsed stationboard: {}".format(connections))

            # sometimes we get more entries from the api, we just return the number asked for
            return connections[0:entries]

        except Exception as e:
            _LOGGER.error(
                "Can not parse the data from transport.opendata.ch: {}".format(e)
            )
            raise exceptions.OpendataTransportParseError(e)

    def get_connections(self, from_station, to_station, entries=1, departure_time=None):
        """Returns the dictonary with connections information for the given stations.
    
        Keyword arguments:
        from_station    -- the name of the origin public transport station 
        to_station      -- the name of the destination public transport station 
        entries         -- the number of connections we want back (default 1)
        departure_time  -- to get the connecions for a specific date and time (default is now)
        """
        if departure_time == None:
            query = {"from": from_station, "to": to_station, "limit": entries}
        else:
            query = {
                "from": from_station,
                "to": to_station,
                "limit": entries,
                "datetime": departure_time.isoformat(),
            }
        url = _RESOURCE + "connections?" + urlp.urlencode(query)

        # try to load the data from transport opendata api
        try:
            result = requests.get(url)
            tt = result.json()
            _LOGGER.debug(
                u"Response from transport.opendata.ch: {}".format(result.status_code)
            )
        except Exception as e:
            _LOGGER.error(u"Can not load data from transport.opendata.ch: {}".format(e))
            raise exceptions.OpendataTransportConnectionError(e)

        # try to parse the data we need
        try:
            # get returned entries
            connections = []
            for connect in tt["connections"]:
                connection = dict()
                connection["from"] = connect["from"]["station"]["name"]
                connection["to"] = connect["to"]["station"]["name"]
                if connect["sections"][0]["journey"] != None:
                    connection["first_to"] = connect["sections"][0]["journey"]["to"]
                    connection["first_transport"] = self._strip_cat_number(
                        connect["sections"][0]["journey"]["category"],
                        connect["sections"][0]["journey"]["number"],
                    )
                else:
                    connection["first_to"] = from_station
                    connection["first_transport"] = ""
                connection["departure"] = connect["from"]["departure"]
                connection["platform"] = connect["from"]["platform"]
                connection["duration"] = connect["duration"]
                connection["transfer_count"] = connect["transfers"]
                connection["transfers"] = []
                for section in connect["sections"]:
                    transfer = dict()
                    if section["walk"] == None:
                        transfer["station"] = section["departure"]["station"]["name"]
                        transfer["departure"] = section["departure"]["departure"]
                        transfer["platform"] = section["departure"]["platform"]
                        if section["journey"] != None:
                            transfer["transport"] = self._strip_cat_number(
                                section["journey"]["category"],
                                section["journey"]["number"],
                            )
                        else:
                            transfer["transport"] = ""
                        connection["transfers"].append(transfer)
                        connection["arrival"] = section["arrival"]["arrival"]
                connections.append(connection)

            _LOGGER.debug(u"Parsed connections: {}".format(connections))

            # sometimes we get more entries from the api, we just return the number asked for
            return connections[0:entries]

        except Exception as e:
            _LOGGER.error(
                "Can not parse the data from transport.opendata.ch: {}".format(e)
            )
            raise exceptions.OpendataTransportParseError(e)
