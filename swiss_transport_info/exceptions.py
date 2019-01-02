"""
Copyright (c) 2019 Cello Spring <cello@cellerich.ch>
https://www.cellerich.ch
Licensed under MIT. All rights reserved.
"""


class SwissTransportInfoError(Exception):
    """Main Class error, has translated/speakable text in exception message"""

    pass


# Internal Exceptions


class OpendataTransportParseError(Exception):
    """Could not parse the data returned from the API."""

    pass


class OpendataTransportConnectionError(Exception):
    """Could not load data from the API."""

    pass


class Data2TextMLConcatenateError(Exception):
    """Could not concatenate the data properly."""

    pass


class Data2TextMLTranslationError(Exception):
    """Could not find the language you wanted."""

    pass

