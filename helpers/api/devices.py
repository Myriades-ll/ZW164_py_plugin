#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Domoticz helpers
"""Module Domoticz JSON/API:Plan"""
# standard libs
from __future__ import annotations

# helpers libs
from helpers.requests import RequestRequest, RequestMethod
from helpers.api import API_REQUEST

class DeviceExtend:
    """Extra device functions using JSON/API"""

    def __init__(self: DeviceExtend, device_id: int) -> None:
        """Initialisation de la classe"""
        self._device_id = device_id

    def protect(self: DeviceExtend, protected=True) -> None:
        """Protège le device contre les actions intentionnelles"""
        url = f"/json.htm?type=setused&idx={self._device_id} \
        &used=true&protected={str(protected).lower()}"
        request = RequestRequest('SetUsed', url, RequestMethod.GET)
        API_REQUEST.send(request)

    def __str__(self: DeviceExtend) -> str:
        """str() wrapper"""
        return f"{self.__repr__()}device ID: {self._device_id}"

    def __repr__(self: DeviceExtend) -> str:
        """repr() wrapper"""
        return f'<class helpers.devices.DeviceExtend @{hex(id(self)).lower()}>'
