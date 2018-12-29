"""
Copyright (c) 2018 Cello Spring <cello@cellerich.ch>
https://www.cellerich.ch
Licensed under MIT. All rights reserved.
"""


class OpendataTransportParseError(Exception):
    """Could not parse the data returned from the API."""

    pass


class OpendataTransportConnectionError(Exception):
    """Could not load data from the API."""

    pass