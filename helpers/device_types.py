#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Domoticz device types"""

# standard libs
from enum import Enum


class DeviceTypes(Enum):
    """Test Enum"""
    PUSH_BUTTON_ON = {
        'Type': 244,  # Light/Switch
        'Subtype': 73,  # Switch
        'Switchtype': 9  # Push On Button
    }
    PUSH_BUTTON_OFF = {
        'Type': 244,  # Light/Switch
        'Subtype': 73,  # Switch
        'Switchtype': 10  # Push Off Button
    }
    SWITCH_ON_OFF = {
        'Type': 244,  # Light/Switch
        'Subtype': 73,  # Switch
        'Switchtype': 0  # On/Off
    }
    DOOR_LOCK_INVERTED = {
        'Type': 244,  # Light/Switch
        'Subtype': 73,  # Switch
        'Switchtype': 20  # Door lock inverted
    }
    DOOR_LOCK = {
        'Type': 244,  # Light/Switch
        'Subtype': 73,  # Switch
        'Switchtype': 19  # Door lock
    }
    FAN_RPM = {
        'Type': 243,  # general
        'Subtype': 7,  # fan
        'Image': 'Fan'
    }
    PERCENTAGE = {
        'Type': 243,  # general
        'Subtype': 6,  # Percentage
    }
    SELECTOR_DROP_DOWN = {
        'Type': 244,  # Light/Switch
        'Subtype': 62,  # Selector Switch
        'Switchtype': 18  # Selector Switch
    }
