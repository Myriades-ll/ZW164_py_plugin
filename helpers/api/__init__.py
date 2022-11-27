#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module API/JSON"""

# standard libs
from typing import Optional

# helpers libs
from helpers.requests import register_connection, Request
from helpers.transport_protocol import TCP_IP_HTTP
from helpers.common import debug

# API libs
from helpers.api.plan import Plan


DOM_API_CON_NAME = 'DomAPI'
API_REQUEST: Optional[Request] = None


def on_start() -> Request:
    """to place in onStart event
    Place the line above in the on_start plugin event and before everything

        helpers.api.API_REQUEST = helpers.api.on_start()

    """
    register_connection(
        DOM_API_CON_NAME,
        address='127.0.0.1',
        port='8080',
        **TCP_IP_HTTP
    )
    return Request(DOM_API_CON_NAME)


def on_stop() -> None:
    """to place in onStop event
    this function closes the API connection
    """
    API_REQUEST.close()
