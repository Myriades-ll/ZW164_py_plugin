# -*- coding: UTF-8 -*-
"""HTML page"""

# standard libs
from __future__ import annotations

from dataclasses import dataclass

# pylint:disable=invalid-name,too-many-instance-attributes


@dataclass
class PluginParameters:
    """wrapper pour Parameters"""
    Address: str  # '127.0.0.1'
    Author: str  # 'Myriades'
    Database: str  # '~/domoticz/domoticz.db',
    DomoticzBuildTime: str  # '2022-11-05 13:05:35',
    DomoticzHash: str  # 'eea9db734',
    DomoticzVersion: str  # '2022.2',
    HardwareID: int  # 23,
    HomeFolder: str  # '~/domoticz/plugins/ZW164_py_plugin/',
    Key: str  # 'zw164_pyplug',
    Language: str  # 'fr',
    Mode1: str  # '',
    Mode2: str  # '',
    Mode3: str  # '',
    Mode4: str  # '',
    Mode5: str  # '',
    Mode6: str  # '2.0',
    Name: str  # 'ZW164',
    Password: str  # '',
    Port: str  # '1883',
    SerialPort: str  # '',
    StartupFolder: str  # '~/domoticz/',
    UserDataFolder: str  # '~/domoticz/',
    Username: str  # '',
    Version: str  # '1.0',
    WebRoot: str  # ''
