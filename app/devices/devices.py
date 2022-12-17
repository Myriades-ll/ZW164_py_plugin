# -*- coding: UTF-8 -*-
"""Devices manager"""

# standard libs
from __future__ import annotations

from typing import Any, Dict, Optional

# plugin libs
import Domoticz
import helpers
from app.config import ZW164Config
from app.zwave.soundswitch import CCSSEndpoint
from domoticz.responses import OnDeviceRemovedResponse as ODRR
from helpers.app_config import DeviceMappingDatas


class DeviceMapping:
    """Device mapping"""
    _devices_ids = set()
    _devices_mapping: Dict[str, DeviceMappingDatas] = {}
    _devices: Dict[int, Domoticz.Device] = {}
    _next_unit_id = -1
    _units_ids = set()

    def init_mapping(self: DeviceMapping) -> None:
        """Acquisition du mapping"""
        with ZW164Config() as pcf:
            self._devices_mapping = pcf.device_mapping
        self._devices_ids = set(self._devices_mapping.keys())
        for key, item in self._devices_mapping.items():
            # convert model data
            if isinstance(item, str):
                item = eval(item)  # pylint:disable=eval-used
            self._devices_mapping.update({key: item})
            self._units_ids.add(item.unit)
        try:
            self._next_unit_id: int = min(set(range(1, 255)) - self._units_ids)
        except ValueError:
            helpers.error('No more unit avaible')

    def save_mapping(self: DeviceMapping) -> None:
        """save device mapping"""
        with ZW164Config() as pcf:
            pcf.device_mapping = self._devices_mapping

    def update_mapping(
        self: DeviceMapping, device_id: str, node_id: int,
        endpoint_id: int, topic: str
    ) -> None:
        """_update_mapping"""
        unit_id = self.get_next_unit_id()
        self._devices_mapping.update(
            {
                device_id: DeviceMappingDatas(
                    endpoint_id,
                    node_id,
                    topic,
                    unit_id
                )
            }
        )
        self._units_ids.add(unit_id)
        self.save_mapping()
        self.init_mapping()

    def remove_from_mapping(self: DeviceMapping, unit_id: int) -> Optional[DeviceMappingDatas]:
        """remove_from_mapping"""
        tmp = self._devices_mapping.copy()
        for key, value in tmp.items():
            if value.unit == unit_id:
                self._devices_mapping.pop(key)
                self.save_mapping()
                self.init_mapping()
                return value
        return None

    def index_of_unit(self: DeviceMapping, search_unit: int) -> Optional[str]:
        """search index of `search` in device mapping"""
        for key, value in self._devices_mapping.items():
            if value.unit == search_unit:
                return key
        return None

    def clean_mapping(self: DeviceMapping) -> None:
        """clean_mapping"""
        tmp = self._devices_mapping.copy()
        for device_id, datas in tmp.items():
            device = self._devices.get(datas.unit)
            if device is None:
                self._devices_mapping.pop(device_id)
        self.save_mapping()
        self.init_mapping()

    def get_next_unit_id(self: DeviceMapping) -> int:
        """get_next_unit_id"""
        try:
            self._next_unit_id: int = min(set(range(1, 255)) - self._units_ids)
        except ValueError:
            helpers.error('No more unit avaible')
        return self._next_unit_id

    def get_device_from_device_id(
            self: DeviceMapping, device_id: str) -> Optional[Domoticz.Device]:
        """
        @return Device if device_id exists, else `None`
        """
        mapping = self._devices_mapping.get(device_id)
        if mapping is not None:
            return self._devices.get(mapping.unit)
        return None

    def get_device_from_unit_id(self: DeviceMapping, unit_id: int) -> Optional[Domoticz.Device]:
        """return the device"""
        return self._devices.get(unit_id)


class DzDevices(DeviceMapping):
    """Domoticz devices"""

    def on_start(self: DzDevices, devices: Dict[int, Domoticz.Device]) -> None:
        """onStart event"""
        self._devices = devices
        self.init_mapping()
        self.clean_mapping()

    def remove_device(self: DzDevices, odrr: ODRR) -> None:
        """remove_device"""
        index = self.index_of_unit(odrr.unit)
        if index is not None:
            deleted = self.remove_from_mapping(odrr.unit)
            helpers.status(f'Deleted device: {deleted}')

    @helpers.log_func('debug', True, True)
    def update(self: DzDevices, endpoint: CCSSEndpoint) -> None:
        """update or create devices
        #ignore_self_arg
        """
        self.init_mapping()
        base_device_id = f'{endpoint.node_id}_{endpoint.endpoint_id}_'

        # defaultVolume
        device_id = base_device_id + 'defaultVolume'
        device = self.get_device_from_device_id(device_id)
        if device is None:  # create
            device = self._create_default_volume(
                endpoint.node_id,
                endpoint.endpoint_id,
                'defaultVolume',
                device_id
            )
        # update defaultVolume
        datas = self._update_default_volume(endpoint.defaultVolume)
        device.Update(**datas)
        helpers.debug(
            f'Mise à jour volume: ({endpoint.node_id}-{endpoint.endpoint_id}){datas}'
        )

        # toneId
        device_id = base_device_id + 'toneId'
        device = self.get_device_from_device_id(device_id)
        if device is None:  # create
            device = self._create_default_tone(
                endpoint,
                'toneId',
                device_id
            )
        # update toneId
        datas = self._update_default_tone(len(endpoint.tones), endpoint.toneId)
        device.Update(**datas)
        helpers.debug(
            f'Mise à jour son: ({endpoint.node_id}-{endpoint.endpoint_id}){datas}'
        )

    def _create_default_volume(
            self: DzDevices,
            node_id: int,
            endpoint_id: int,
            topic: str,
            device_id: str) -> Domoticz.Device:
        """creates a toneId device"""
        my_dev = Domoticz.Device(
            Name=f'N{node_id}E{endpoint_id}: volume',
            Unit=self.get_next_unit_id(),
            DeviceID=device_id,
            TypeName='Dimmer',
            Image=8  # speaker
        )
        my_dev.Create()
        self.update_mapping(device_id, node_id, endpoint_id, topic)
        helpers.status(f'Device created: {my_dev.Name}')
        return my_dev

    @staticmethod
    def _update_default_volume(value: int) -> Dict[str, Any]:
        """_update_default_volume"""
        kwargs = {
            'nValue': 0,
            'sValue': '0'
        }
        if 0 < value <= 100:
            kwargs.update(
                {
                    'nValue': 1,
                    'sValue': str(value)
                }
            )
        return kwargs

    def _create_default_tone(
            self: DzDevices, endpoint: CCSSEndpoint,
            topic: str, device_id: str) -> Domoticz.Device:
        """creates a toneId device"""
        # preparing device options
        tones = dict(sorted(endpoint.tones.items()))
        names = ''
        actions = '|' * (len(tones) - 1)
        for values in tones.values():
            names += f'{values.name}'
            if values.duration > 0:
                names += f' ({values.duration}s)'
            names += '|'
        names = names[:-1]
        # creating device options
        options = {
            "LevelActions": actions,
            "LevelNames": names,
            "LevelOffHidden": "false",
            "SelectorStyle": "1"  # drop down
        }
        # create the device
        my_dev = Domoticz.Device(
            Name=f'N{endpoint.node_id}E{endpoint.endpoint_id}: tone',
            Unit=self.get_next_unit_id(),
            DeviceID=device_id,
            TypeName="Selector Switch",
            Switchtype=18,
            Image=8,  # speaker
            Options=options
        )
        my_dev.Create()
        self.update_mapping(
            device_id,
            endpoint.node_id,
            endpoint.endpoint_id,
            topic
        )
        helpers.status(f'Device created: {my_dev.Name}')
        return my_dev

    @staticmethod
    def _update_default_tone(nb_tones: int, tone_id: int) -> Dict[str, Any]:
        """_update_default_tone"""
        kwargs = {
            'nValue': 0,
            'sValue': '0'
        }
        if tone_id == 255:
            tone_ref = (nb_tones - 1) * 10
            kwargs.update(
                {
                    'nValue': tone_ref,
                    'sValue': str(tone_ref)
                }
            )
        else:
            tone_id *= 10
            kwargs.update(
                {
                    'nValue': tone_id,
                    'sValue': str(tone_id)
                }
            )
        return kwargs
