"""
Copyright (c) 2018 Cello Spring <cello@cellerich.ch>
https://www.cellerich.ch
Licensed under MIT. All rights reserved.
"""


class Data2TextMLConcatenateError(Exception):
    """Could not concatenate the data properly."""

    pass


class Data2TextMLTranslationError(Exception):
    """Could not find the language you wanted."""

    pass
