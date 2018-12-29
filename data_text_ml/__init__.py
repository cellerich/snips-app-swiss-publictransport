"""
Copyright (c) 2018 Cello Spring <cello@cellerich.ch>
https://www.cellerich.ch
Licensed under MIT. All rights reserved.
"""

import json
import logging
import dateutil.parser
import gettext

from datetime import datetime
from . import exceptions

_LOGGER = logging.getLogger(__name__)


class Data2TextML(object):
    """A class to render the transport connections data into speakable text
    The module uses 'gettext' for the translation into the available languages

    The module is depending on the opendata_transport_api module and will
    receive the output data of its functions
    """

    def __init__(self, language='en'):
        """Initialize the Class with the needed language
        
        Keyword arguments:
        language            -- language for text output (default = 'en')
        """
        try:
            #try to see if the language is supported
            lang = gettext.translation('snips', localedir='./locale', languages=[language])
            lang.install()

        except Exception as e:
            _LOGGER.error("Cannot load the wanted language: {}".format(e))
            raise exceptions.Data2TextMLTranslationError(e)


    def _get_time_string(self, c_time):
        """Returns the Hour and Minute of a iso formatted date string"""
        return dateutil.parser.parse(c_time).strftime('%H:%M')


    def _get_duration_string(self, duration):
        """Returns the Hour and Minute of a iso formatted date string"""
        duration_format = _('%H hours %M minutes ')
        return datetime.strptime(duration,'%fd%H:%M:%S').strftime(duration_format)


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

        #try to concatenate the output data we need 
        try:

            sentence = ''

            #create the sentences 
            t_frag_1 = _( \
            'The next connection from {origin} is number {transport} and leaves at {} from platform {platform} towards {destination}. ') + \
            _('There are {stops} stops before the final destination. ') 
            sentence += t_frag_1.format(self._get_time_string(sb_data[0]['departure']), **sb_data[0])

            sentence += _('Other connections are: ')
            
            t_frag_3 = _( \
            'number {transport} towards {destination} leaving {} from platform {platform} with {stops} stops; ')
            sentence += t_frag_3.format(self._get_time_string(sb_data[1]['departure']), **sb_data[1])

            t_frag_4 = _( \
            '{transport} towards {destination} leaving {} from platform {platform} with {stops} stops and ')
            sentence += t_frag_4.format(self._get_time_string(sb_data[2]['departure']), **sb_data[2])

            t_frag_5 = _( \
            '{transport} towards {destination} leaving {} from platform {platform} with {stops} stops.')
            sentence += t_frag_5.format(self._get_time_string(sb_data[3]['departure']), **sb_data[3])

            _LOGGER.debug("concatenated sentence: {}".format(sentence))
            return  sentence

        except Exception as e:
            _LOGGER.error("Can not concatenate the input data: {}".format(e))
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

        #try to concatenate the output data we need 
        try:
            sentence = ''

            #create the sentences 
            t_frag_1 = _( \
            'Your next connection from {from} to {to} leaves at {}. ')
            sentence += t_frag_1.format(self._get_time_string(cn_data[0]['departure']), **cn_data[0])

            t_frag_2 = _(
            'It has the number {first_transport} on Platform {platform}. ')
            sentence += t_frag_2.format(**cn_data[0])
            
            t_frag_3 = _( \
            'The journey takes {}, you will arrive in {to} at {}. ')
            sentence += t_frag_3.format(self._get_duration_string(cn_data[0]['duration']), self._get_time_string(cn_data[0]['arrival']), **cn_data[0])

            t_frag_4 = _( \
            'There are {transfer_count} transfers: ')
            sentence += t_frag_4.format(**cn_data[0])

            t_frag_loop = _( \
            '- in {station} - {}, number {transport} on platform {platform}. ')

            #add all the transfer data
            for transfer in cn_data[0]['transfers']:
                sentence += t_frag_loop.format(self._get_time_string(transfer['departure']), **transfer)

            _LOGGER.debug("concatenated sentence: {}".format(sentence))
            return  sentence

        except Exception as e:
            _LOGGER.error("Can not concatenate the input data: {}".format(e))
            raise exceptions.Data2TextMLConcatenateError(e)

