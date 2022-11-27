#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""App base"""

# standard libs
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

# Domoticz lib
import Domoticz
import helpers
from app.config import ZW164Config
from zw164.classes import ZW164Node, ZW164Payload
from zw164.definitions import ZW164Sounds


class DeviceMapping:
    """Device mapping"""
    _devices: Dict[int, Domoticz.Device] = {}
    _devices_mapping: Dict[str, Dict[str, Any]] = {}
    _devices_ids = set()
    _units_ids = set()
    _next_unit_id = -1

    def _init_mapping(self: DomXZW164) -> None:
        """Acquisition du mapping"""
        with ZW164Config() as pcf:
            self._devices_mapping = pcf.device_mapping
        self._devices_ids = set(self._devices_mapping.keys())
        for item in self._devices_mapping.values():
            self._units_ids.add(item.get('unit'))
        # self._units_ids = set(self._devices_mapping.values())
        try:
            self._next_unit_id: int = min(set(range(1, 255)) - self._units_ids)
        except ValueError:
            helpers.error('No more unit avaible')

    def _save_mapping(self: DomXZW164) -> None:
        """save device mapping"""
        with ZW164Config() as pcf:
            pcf.device_mapping = self._devices_mapping
        self._init_mapping()

    def _index_of_unit(self: DomXZW164, search_unit: int) -> Optional[str]:
        """search index of `search` in device mapping"""
        # helpers.debug(
        #     f'device mapping: ({type(self._devices_mapping)}){self._devices_mapping}'
        # )
        for key, value in self._devices_mapping.items():
            if value['unit'] == search_unit:
                return key
        return None


class DomXZW164(DeviceMapping):
    """Echanges Domoticz avec ZW164"""
    _cb_publish: Optional[Callable] = None

    def __init__(self: DomXZW164) -> None:
        """Initialisation de la classe"""
        DeviceMapping.__init__(self)

    def on_start(self: DomXZW164, devices: Dict[int, Domoticz.Device]) -> None:
        """à placer dans `onStart`"""
        self._devices = devices
        # with ZW164Config() as pcf:
        #     pcf.device_mapping = {}
        self._init_mapping()

    def on_device_removed(self: DomXZW164, unit: int) -> None:
        """place in `onDeviceRemoved`"""
        self._init_mapping()
        deleted = self._devices_mapping.pop(self._index_of_unit(unit))
        helpers.status(f'deleted device ({unit}): {deleted}')
        self._save_mapping()

    def on_command(self: DomXZW164, unit_id: int, command: str, level: int, _color: str) -> None:
        """A placer dans `on_command`"""
        if self._cb_publish is not None:
            node_infos = self._devices_mapping.get(
                self._index_of_unit(unit_id)
            )
            sub_topic = node_infos.get('topic')
            topic = f"zwave/{node_infos.get('node_id')}/121/{node_infos.get('switch_id')}/{sub_topic}/set"
            value = 0
            if command == 'Set Level':
                if sub_topic == 'defaultVolume':
                    value = level
                elif sub_topic == 'toneId':
                    if level == 310:
                        value = 255
                    else:
                        value = int(level / 10)
            # helpers.debug(topic, value)
            self._cb_publish(topic, value)

    def cb_publish(self: DomXZW164, zw164_node: ZW164Node) -> None:
        """callback on publish
        # ignore_self_arg
        """
        self._init_mapping()
        for topic, payload in zw164_node.topics.items():
            device_id = (
                str(zw164_node.node_id)
                + '_'
                + str(zw164_node.switch_id)
                + '_'
                + topic
            )
            # create if necessary
            if device_id not in self._devices_mapping:
                self._create_device(
                    zw164_node.node_id,
                    zw164_node.switch_id,
                    topic,
                    device_id
                )
                self._save_mapping()
            # update
            device_details: Optional[dict] = self._devices_mapping.get(
                device_id)
            if device_details is not None:
                self._update_device(device_details.get('unit'), topic, payload)

    def set_publish_callback(self: DomXZW164, callback: Callable[str, Any]) -> None:
        """set publish callback"""
        if callable(callback):
            self._cb_publish: Callable[str, Any] = callback

    def _create_device(
            self: DomXZW164,
            node_id: int,
            switch_id: int,
            topic: str,
            device_id: str) -> None:
        """Create devices"""
        if topic not in ['defaultVolume', 'toneId']:
            return
        if topic == 'defaultVolume':
            self._create_default_volume(node_id, switch_id, topic, device_id)
        elif topic == 'toneId':
            self._create_tone_id(node_id, switch_id, topic, device_id)
        # useless
        else:
            helpers.error(f'Unknown topic: {topic}')

    def _update_device(self: DomXZW164, unit_id: str, topic: str, payload: ZW164Payload) -> None:
        """Update devices"""
        if topic not in ['defaultVolume', 'toneId']:
            return
        if payload.value < 0:  # no value!
            return
        kwargs = {
            'nValue': 0,
            'sValue': '0'
        }
        if topic == 'defaultVolume':
            # helpers.debug(f'Changing volume: {payload.value}')
            if 0 < payload.value <= 100:
                kwargs.update(
                    {
                        'nValue': 1,
                        'sValue': str(payload.value)
                    }
                )
            self._devices[unit_id].Update(**kwargs)
        elif topic == 'toneId':
            if payload.value == 255:
                kwargs.update(
                    {
                        'nValue': 310,
                        'sValue': '310'
                    }
                )
            else:
                value = payload.value * 10
                kwargs.update(
                    {
                        'nValue': value,
                        'sValue': str(value)
                    }
                )
            self._devices[unit_id].Update(**kwargs)

    def _create_default_volume(
            self: DomXZW164,
            node_id: int,
            switch_id: int,
            topic: str,
            device_id: str) -> None:
        """creates a toneId device"""
        my_dev = Domoticz.Device(
            Name=(
                "N"
                + str(node_id)
                + 'SS'
                + str(switch_id)
                + ": volume"
            ),
            Unit=self._next_unit_id,
            DeviceID=device_id,
            TypeName='Dimmer',
            Image=8  # speaker
        )
        my_dev.Create()
        self._devices_mapping.update(
            {
                device_id: {
                    'unit': self._next_unit_id,
                    'node_id': node_id,
                    'switch_id': switch_id,
                    'topic': topic
                }
            }
        )
        helpers.status(f'Device created: {my_dev.Name}')

    def _create_tone_id(
            self: DomXZW164,
            node_id: int,
            switch_id: int,
            topic: str,
            device_id: str) -> None:
        """creates a toneId device
            Options = {
                "LevelActions": "|| ||",
                "LevelNames": "Off|Video|Music|TV Shows|Live TV",
                "LevelOffHidden": "false",
                "SelectorStyle": "1"
            }
        """
        options = {
            "LevelActions": "",
            "LevelNames": "",
            "LevelOffHidden": "false",
            "SelectorStyle": "1"  # drop down
        }
        prefix = ''
        # updating options
        for element in ZW164Sounds:
            element_values = element.value
            options.update(
                {
                    "LevelActions": options.get('LevelActions') + prefix,
                    "LevelNames": (
                        options.get('LevelNames')
                        + prefix
                        + element_values.get('name')
                        + f" ({element_values.get('duration')}s)"
                    ),
                }
            )
            prefix = '|'
        # helpers.debug(options)
        # create the device
        my_dev = Domoticz.Device(
            Name=(
                "N"
                + str(node_id)
                + 'SS'
                + str(switch_id)
                + ": tone"
            ),
            Unit=self._next_unit_id,
            DeviceID=device_id,
            TypeName="Selector Switch",
            Switchtype=18,
            Image=8,  # speaker
            Options=options
        )
        my_dev.Create()
        self._devices_mapping.update(
            {
                device_id: {
                    'unit': self._next_unit_id,
                    'node_id': node_id,
                    'switch_id': switch_id,
                    'topic': topic
                }
            }
        )
        helpers.status(f'Device created: {my_dev.Name}')

    def __str__(self) -> str:
        """Wrapper pour str()"""
        return ""

    def __repr__(self) -> str:
        """Wrapper pour repr()"""
        return ""
