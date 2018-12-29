"""
Copyright (c) 2018 Cello Spring <cello@cellerich.ch>
https://www.cellerich.ch
Licensed under MIT. All rights reserved.
"""

import urllib.parse as urlp
import requests
import json
import logging

from . import exceptions

_LOGGER = logging.getLogger(__name__)
_RESOURCE = 'http://transport.opendata.ch/v1/'


class OpendataTransport(object):
    """A class to get a information from the Opendata Transport API."""


    #small routine to check if the transport category already is in the transport number, then we just use the number
    def _strip_cat_number(self, category, number):
        """small routine to check if the transport category already is in the transport number, 
        then we just use the number
        """
        if category in number:
            return number
        else:
            return category + ' ' + number


    def get_stationboard(self, station_name, entries=1, departure_time = None):
        """Returns the dictonary with stationboard information for the given station.
    
        Keyword arguments:
        station_name    -- the name of the public transport station 
        entries         -- the number of connections we want back (default 1)
        departure_time  -- to get the stationboard for a specific date and time (default is now)
        """
        if departure_time == None:
            query = { 'station' : station_name, 'limit' : entries}
        else: 
            query = { 'station' : station_name, 'limit' : entries, 'datetime':departure_time.isoformat()}
        url =  _RESOURCE + 'stationboard?' + urlp.urlencode(query)

        # try to load the data from transport opendata api
        try:
            result = requests.get(url)
            sb = result.json()
            _LOGGER.debug("Response from transport.opendata.ch: {}".format(result.status_code))
        except Exception as e:
            _LOGGER.error("Can not load data from transport.opendata.ch: {}".format(e))
            raise exceptions.OpendataTransportConnectionError(e)

        #try to parse the data we need 
        try:
            connections = []
            for connect in sb['stationboard']:
                connection = dict()
                connection['origin'] = sb['station']['name']
                connection['destination'] = connect['to']
                connection['departure'] = connect['stop']['departure']
                connection['platform'] = connect['stop']['platform']
                connection['transport'] = self._strip_cat_number(connect['category'],connect['number'])
                connection['stops'] = len(connect['passList']) -1
                connections.append(connection)

            _LOGGER.debug("Parsed stationboard: {}".format(connections))
            
            #sometimes we get more entries from the api, we just return the number asked for
            return connections[0:entries]

        except Exception as e:
            _LOGGER.error("Can not parse the data from transport.opendata.ch: {}".format(e))
            raise exceptions.OpendataTransportParseError(e)


    def get_connections(self, from_station, to_station, entries=1, departure_time = None):
        """Returns the dictonary with connections information for the given stations.
    
        Keyword arguments:
        from_station    -- the name of the origin public transport station 
        to_station      -- the name of the destination public transport station 
        entries         -- the number of connections we want back (default 1)
        departure_time  -- to get the connecions for a specific date and time (default is now)
        """
        if departure_time == None:
            query = {'from' : from_station, 'to': to_station ,'limit' : entries}
        else: 
            query = { 'from' : from_station, 'to': to_station ,'limit' : entries, 'datetime':departure_time.isoformat()}
        url =  _RESOURCE + 'connections?' + urlp.urlencode(query)

        # try to load the data from transport opendata api
        try:
            result = requests.get(url)
            tt = result.json()
            _LOGGER.debug("Response from transport.opendata.ch: {}".format(result.status_code))
        except Exception as e:
            _LOGGER.error("Can not load data from transport.opendata.ch: {}".format(e))
            raise exceptions.OpendataTransportConnectionError(e)

        #try to parse the data we need 
        try:
            #get returned entries
            connections = []
            for connect in tt['connections']:
                connection = dict()
                connection['from'] = connect['from']['station']['name']
                connection['to'] = connect['to']['station']['name']
                if connect['sections'][0]['journey'] != None:
                    connection['first_to'] = connect['sections'][0]['journey']['to']
                    connection['first_transport'] = self._strip_cat_number(connect['sections'][0]['journey']['category'],connect['sections'][0]['journey']['number'])
                else:
                    connection['first_to'] = from_station
                    connection['first_transport'] = ''
                connection['departure'] = connect['from']['departure']
                connection['platform'] = connect['from']['platform']
                connection['duration'] = connect['duration']
                connection['transfer_count'] = connect['transfers']
                connection['transfers'] = []
                for section in connect['sections'][1:]:
                    transfer = dict()
                    if section['walk'] == None:
                        transfer['station'] = section['departure']['station']['name']
                        transfer['departure'] = section['departure']['departure']
                        transfer['platform'] = section['departure']['platform']
                        if section['journey'] != None:
                            transfer['transport'] = self._strip_cat_number(section['journey']['category'],section['journey']['number'])
                        else:
                            transfer['transport'] = ''
                        connection['transfers'].append(transfer)
                        connection['arrival'] = section['arrival']['arrival']
                connections.append(connection)

            _LOGGER.debug("Parsed connections: {}".format(connections))
            
            #sometimes we get more entries from the api, we just return the number asked for
            return connections[0:entries]

        except Exception as e:
            _LOGGER.error("Can not parse the data from transport.opendata.ch: {}".format(e))
            raise exceptions.OpendataTransportParseError(e)
