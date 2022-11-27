#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Freebox Python Plugin
"""Module FreeBox devices"""

# standard libs
from __future__ import annotations

from typing import Any, Dict, Optional, Union
from collections.abc import Callable
from time import time

# Domoticz lib
import Domoticz

# local lib
from helpers.device_types import DeviceTypes
from helpers.common import debug, status


class DDevice:
    """Domoticz.Device extender
    [mandatory args]:
        - device_id (str): external identifier
        - name (str): device name
        - device_type (helpers.device_types): one of the documented device type

    [optional kwargs]:
        - used (bool): True if device is automaticaly set as Used
        - in_plan (bool): automatically add the device to the plan TODO:
        - protected (bool): password protected device against misuse TODO:
        - command (function): the function to call when onCommand event occurs for the device
        - update (function): the function to call when device has to be updated TODO:
    """

    def __init__(
            self: DDevice, device_id: str, name: str,
            device_type: DeviceTypes, **kwargs: Dict[str, Any]) -> None:
        """Initialisation de la classe"""
        self.unit_id: int = DDevices.get_unit_id(device_id)
        self.name: str = name
        self.device_id: str = device_id
        self.device_type: DeviceTypes = device_type
        # les fonctions
        self._command: Callable = kwargs.pop('command', None)
        self._update: Callable = kwargs.pop('update', None)
        self._modified: Callable = kwargs.pop('modified', None)
        # Interval de mise à jour
        self._update_interval = kwargs.pop('update_interval', None)
        self.next_update_time = 0
        if self._update_interval is not None:
            self.next_update_time = time()
        # device creation
        if not DDevices.is_unit_id_in_devices(self.unit_id):
            self._create(**kwargs)

    def command(self: DDevice, *args: tuple, **kwargs: dict) -> Any:
        """Action sur commande utilisateur"""
        if self._command is not None:
            if callable(self._command):
                return self._command(*args, **kwargs)
        return None

    def update(self: DDevice, *args: tuple, **kwargs: dict) -> Optional[dict]:
        """Mise à jour du device"""
        if 0 != self.next_update_time <= time():
            if self._update is not None:
                if callable(self._update):
                    self.next_update_time += self._update_interval
                    dz_datas, return_datas = self._update(*args, **kwargs)
                    self._update_or_touch(dz_datas)
                    return return_datas
        return None

    def _update_or_touch(self: DDevice, dz_datas: Dict[str, Any]) -> None:
        # pylint:disable=line-too-long
        """Mise à jour device ou activité

        nValue: Mandatory; The Numerical device value
        sValue: Mandatory; The string device value
        Image: Optional; Numeric custom image number
        SignalLevel: Optional; Device signal strength, default 12
        BatteryLevel: Optional; Device battery strength, default 255
        Options: Optional; Dictionary of device options, default is empty {}
        TimedOut: Optional; default is 0
            - Numeric field where 0 (false) is not timed out and other value marks the device as timed out
            - Timed out devices show with a red header in the Domoticz web UI.
        Name: Optional
            - Is appended to the Hardware name to set the initial Domoticz Device name.
            - This should not be used in Python because it can be changed in the Web UI.
        TypeName: Optional
            - Common device types, this will set the values for Type, Subtype and Switchtype.
            - See #Available_Device_Types
        Type: Optional
            - Directly set the numeric Type value.
            - Should only be used if the Device to be created is not supported by TypeName.
        Subtype: Optional
            - Directly set the numeric Subtype value.
            - Should only be used if the Device to be created is not supported by TypeName.
        Switchtype: Optional
            - Directly set the numeric Switchtype value.
            - Should only be used if the Device to be created is not supported by TypeName.
        Used: Optional
            - 0 (default) Unused
            - 1 Used.
            Set the Device Used field.
            Used devices appear in the appropriate tab(s).
            Unused devices appear only in the Devices page and must be manually marked as Used.
        Description: Optional
        Color: Optional; Current color, see documentation of onCommand callback for details on the format.
        SuppressTriggers: Optional
            - Default: False Boolean flag that allows device attributes to be updated without notifications, scene or MQTT, event triggers.
            - nValue and sValue are not written to the database and will be overwritten with current database values.

        """
        # pylint:enable=line-too-long
        # données statiques
        keys_mandatory = {
            'nvalue': 'nValue',
            'svalue': 'sValue'
        }
        keys_optional = {
            'image': 'Image',
            'signallevel': 'SignalLevel',
            'batterylevel': 'BatteryLevel',
            'options': 'Options',
            'timedout': 'TimedOut',
            'name': 'Name',
            'typename': 'TypeName',
            'type': 'Type',
            'subtype': 'Subtype',
            'switchtype': 'Switchtype',
            'used': 'Used',
            'description': 'Description',
            'color': 'Color',
            'suppresstriggers': 'SuppressTriggers'
        }

        device = DDevices.get_device_from_device_id(self.device_id)
        need_update = False
        formated_datas: Dict[str, Any] = {}

        def search(key: str, value: Any, comparison: dict, mandatory=False) -> bool:
            """Comparaison interne"""
            nonlocal device, formated_datas, keys_mandatory
            key_lower = key.lower()
            if key_lower not in comparison:
                return False
            dz_key = comparison[key_lower]
            dz_value = getattr(device, dz_key)
            if dz_value != value:
                formated_datas.update({dz_key: value})
                return True
            if mandatory:
                formated_datas.update({dz_key: value})
                return True
            return False

        # recherches dans les données fournies, pour comparaison et mise à jour
        for key, value in dz_datas.items():
            need_update |= search(key, value, keys_optional)
        for key, value in dz_datas.items():
            if need_update:
                search(key, value, keys_mandatory, True)
            else:
                need_update |= search(key, value, keys_mandatory)
        # mise à jour
        if need_update:
            self.name = formated_datas.get('Name', self.name)
            status('Mise à jour {}'.format(self))
            device.Update(**formated_datas)
        else:
            device.Touch()

    def modified(self: DDevice, *args: tuple, **kwargs: dict) -> Optional[dict]:
        """Modification du device depuis Domoticz"""
        if self._modified is not None:
            if callable(self._modified):
                return self._modified(*args, **kwargs)
        return None

    def _create(self: DDevice, **kwargs: dict) -> None:
        """Création du device dans Domoticz
        [kwargs]:
            - Name (str):       mandatory
            - Unit (int):       mandatory; must be less than 256
            - DeviceID (str):   mandatory; max len is 25
            - Image 	Optional
            - Options 	Optional
            - Used 	(int):      Optional; 0 not used; 1 used

            * specials device kwargs
                - TypeName (str):	Optional
                            OR
                - Type (int):       Optional
                - Subtype (int):    Optional
                - Switchtype (int): Optional
        """
        datas = {
            'Name': self.name,
            'DeviceID': self.device_id,
            'Unit': self.unit_id,
            **self.device_type.value
        }
        allowed_keys = {
            'image': 'Image',
            'options': 'Options',
            'used': 'Used'
        }
        for key in kwargs:
            key_lower = key.lower()
            if key_lower in allowed_keys:
                datas.update({allowed_keys[key_lower]: kwargs[key]})
        device = Domoticz.Device(**datas)
        device.Create()
        status('Création du device: ({}){}'.format(
            device.ID,
            self.name
        ))

    def __str__(self: DDevice) -> str:
        """str() wrapper"""
        return '<({}){}> {}'.format(self.unit_id, self.name, self.device_id)


class DDevices:
    """Gestionnaire des devices"""
    _devices: Dict[int, Domoticz.Device] = {}
    _device_mapping: Dict[str, int] = {}
    _rest_ids = set()

    def __new__(cls: DDevices, devices: Optional[Domoticz.Devices] = None) -> DDevices:
        """Constructeur"""
        if devices is not None:
            cls._devices = devices
            cls._build_mapping()
            debug('Devices: {}'.format(cls._devices))
            debug('Mapping: {}'.format(cls._device_mapping))
        return super(DDevices, cls).__new__(cls)

    @classmethod
    def _build_mapping(cls: DDevices) -> None:
        """Construction du mapping"""
        # build mapping from devices list
        for key, values in cls._devices.items():
            cls._update_mapping(values.DeviceID, key)
        cls._rest_ids = set(range(1, 256)) - set(cls._device_mapping.values())

    @classmethod
    def _update_mapping(cls: DDevices, device_id: Union[str, int], unit_id: int) -> None:
        """Mise à jour des mapping"""
        cls._device_mapping.update({device_id: unit_id})

    @classmethod
    def get_device_id(cls: DDevices, unit_id: int) -> str:
        """Return the device ID"""
        return cls._devices[unit_id].DeviceID

    @classmethod
    def get_unit_id(cls: DDevices, device_id: str) -> int:
        """Return unit_id"""
        if device_id in cls._device_mapping:
            return cls._device_mapping[device_id]
        unit_id = cls._rest_ids.pop()
        cls._update_mapping(device_id, unit_id)
        return unit_id

    @classmethod
    def get_device_from_device_id(cls: DDevices, device_id: str) -> Domoticz.Device:
        """Return device from device_id"""
        return cls._devices[cls._device_mapping[device_id]]

    @classmethod
    def get_device_from_unit_id(cls: DDevices, unit_id: str) -> Domoticz.Device:
        """Return device from device_id"""
        return cls._devices[unit_id]

    @classmethod
    def is_device_id_in_mapping(cls: DDevices, device_id: str) -> bool:
        """Return True if device is in mapping"""
        return device_id in cls._device_mapping

    @classmethod
    def is_unit_id_in_devices(cls: DDevices, unit_id: int) -> bool:
        """Return True if device exists"""
        return unit_id in cls._devices

    @classmethod
    def remove(cls: DDevices, unit_id: int) -> None:
        """Retire le device du mapping"""
        device_id = cls.get_device_id(unit_id)
        cls._device_mapping.pop(device_id)
        cls._rest_ids.add(unit_id)
        cls._rest_ids = set(sorted(cls._rest_ids))
        debug(
            'Deletion of unit: {}'.format(unit_id),
            cls._device_mapping
        )

    @classmethod
    def __str__(cls: DDevices) -> str:
        return 'Domoticz devices: {}'.format(cls._devices)
