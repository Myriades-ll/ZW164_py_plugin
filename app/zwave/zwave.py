#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Zwave manager classes"""


# standard libs
from __future__ import annotations

from dataclasses import dataclass, field
from json import loads
from typing import Any, List

# plugin libs
import Domoticz
from domoticz.responses import OnCommandResponse as OCDR
# pylint:disable=invalid-name


@dataclass
class ZwavePayloadDatas:
    """ZwavePayload
    {
        "time":1670832488419,
        "value":1,
        "nodeName":"Sirène",
        "nodeLocation":"Salon"
    }
    """
    time: int
    value: Any
    nodeName: str
    nodeLocation: str


@dataclass
class ZwaveGateway:
    """ZwaveGateWay"""
    response_topic: str = field(default_factory=str, init=False)
    command_topic: str = field(default_factory=str, init=False)
    status: bool = field(default=False, init=False)
    version: str = field(default_factory=str, init=False)

    def update(self: ZwaveGateway, topic: str, payload: bytes) -> None:
        """gateway update"""
        if 'ZWAVE_GATEWAY' in topic:
            path = topic.split(('/'))
            cur_topic = path.pop(-1)
            if not bool(self.response_topic):
                self.response_topic = '/'.join(path) + '/api/sendCommand'
                self.command_topic = self.response_topic + '/set'
            decoded_payload: dict = loads(payload)
            if cur_topic == 'status':
                self.status = decoded_payload.get('value')
            elif cur_topic == 'version':
                self.version = decoded_payload.get('value')

    def is_complete(self: ZwaveGateway) -> bool:
        """check if gateway is functionnal"""
        return bool(self.command_topic) and self.status and bool(self.version)


class Zwave:
    """Zwave manager"""


@dataclass
class SendCommandResult:
    """Send command result

    {
        'success': True,
        'message': 'Success zwave api call',
        'result': 30,
        'args': [
            {
                'nodeId': 32,
                'commandClass': 121,
                'endpoint': 0
            },
            'getToneCount',
            []
        ],
        'origin': {'args': [{'nodeId': 32, 'commandClass': 121, 'endpoint': 0}, 'getToneCount', []]}
    }

    """
    args: list
    message: str
    origin: dict
    success: bool
    command_args: list = field(default_factory=list)
    command_class: int = field(default_factory=int)
    command: str = field(default_factory=str)
    endpoint: int = field(default_factory=int)
    node_id: int = field(default_factory=int)
    result: Any = field(default_factory=int)

    def __post_init__(self: SendCommandResult) -> None:
        """post init"""
        if len(self.args) > 0:
            target: dict = self.args[0]
            self.node_id = target.get('nodeId')
            self.command_class = target.get('commandClass')
            self.endpoint = target.get('endpoint')
            self.command = self.args[1]
            self.command_args = self.args[2]
        # helpers.debug(self)


class SoundSwitchCommand:
    """SoundSwitchCommand"""
    _command_ready = False
    _command: list = []
    _ocdr: OCDR
    _device: Domoticz.Device

    def __init__(self: SoundSwitchCommand, device: Domoticz.Device, ocdr: OCDR) -> None:
        """Initialisation de la classe"""
        node_id, endpoint_id, topic = device.DeviceID.split(
            '_'
        )
        self._command.append(f"zwave/{node_id}/121/{endpoint_id}/{topic}/set")
        value = 0
        if ocdr.command == 'Set Level':
            if topic == 'defaultVolume':
                value = ocdr.level
            elif topic == 'toneId':
                if ocdr.level == 310:
                    value = 255
                else:
                    value = int(ocdr.level / 10)
        self._command.append(value)

    def get_command(self: SoundSwitchCommand) -> List[str, int]:
        """get_command"""
        return self._command
