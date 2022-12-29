#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Domoticz plugin configuration"""

# standard libs
from __future__ import annotations

from typing import Optional

# Domoticz lib
import Domoticz

# local libs
from helpers.decorators import log_func


class PluginConfig:
    """Configuration du plugin"""
    address = ''
    port = ''
    mac_address = []
    auto_protect = False
    debug_level = 0
    debug_level_python = 0
    _parameters = {}
    plan_name = ''
    plugin_name = ''
    domoticz_version = ''
    hardware_id = 0

    def __new__(cls: PluginConfig, parameters: Optional[dict] = None) -> PluginConfig:
        """Initialisation de la classe"""
        if isinstance(parameters, dict):
            cls._parameters: dict = parameters
            cls.plugin_name: str = parameters.get('Name', cls.plugin_name)
            cls.domoticz_version: str = parameters.get(
                'DomoticzVersion', cls.domoticz_version)
            cls.address: str = parameters.get('Address', cls.address)
            cls.port: str = parameters.get('Port', cls.port)
            cls._mode6()
        return super(PluginConfig, cls).__new__(cls)

    @classmethod
    def _mode6(cls: PluginConfig) -> None:
        """Positionne debug_level, debug_level_python
        Défini le niveau de debbogage de Domoticz
        """
        debug_levels = (cls._parameters.get(
            'Mode6', cls.debug_level)).split('.')
        cls.debug_level = int(debug_levels[0])
        if len(debug_levels) >= 2:
            cls.debug_level_python = int(debug_levels[1])
        if cls.debug_level:
            Domoticz.Debugging(cls.debug_level)

    @classmethod
    @log_func('debug')
    def __str__(cls: PluginConfig) -> str:
        """Wrapper pour str()"""
        return f'<PluginConfig>{cls._parameters}'

    @classmethod
    def __repr__(cls: PluginConfig) -> str:
        """Wrapper pour repr()"""
        return cls.__str__()
