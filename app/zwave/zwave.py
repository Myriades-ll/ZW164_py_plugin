#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Zwave manager classes"""


# standard libs
from __future__ import annotations

from dataclasses import dataclass, field
from json import loads
from typing import Any

# pylint:disable=invalid-name


@dataclass
class ZwavePayloadDatas:
    """ZwavePayload"""
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


@dataclass
class SendCommandResult:
    """Send command result"""
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
