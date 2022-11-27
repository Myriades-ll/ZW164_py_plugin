#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""MQTT manager classes"""

# standard libs
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, unique
from time import time_ns
from typing import Any, Callable, List, Optional

# App libs
import Domoticz
import helpers
from app.config import ZW164Config


@dataclass(frozen=True)
class MQTTResponse:
    """Réponse MQTT"""
    # pylint:disable=invalid-name
    Verb: str = ""
    Description: str = field(default="")
    DUP: bool = field(default=False)
    Error: str = field(default="")
    PacketIdentifier: str = field(default="")
    Payload: bytes = field(default_factory=bytes)
    QoS: int = field(default=0)
    Retain: bool = field(default=False)
    Status: int = field(default=-1)
    Topic: str = field(default="")
    Topics: List[str] = field(default_factory=list)
    # pylint:enable=invalid-name


@unique
class MQTTCommands(Enum):
    """Les commandes MQTT"""
    CONNECT = {
        'Verb':  "CONNECT",
        'ID':  "",
        'CleanSession': 1,
        'WillTopic':  0,
        'WillQoS':  0,
        'WillRetain': 0,
        'WillPayload': 0
    }
    DISCONNECT = {
        'Verb': 'DISCONNECT'
    }
    PING = {
        'Verb': 'PING'
    }
    SUBSCRIBE = {
        'Verb': 'SUBSCRIBE',
        'Topics': [
            {
                'Topic': 'zwave/+/121/+/#',
                'QoS': 0
            },
        ]
    }
    PUBLISH = {
        'Verb': 'PUBLISH',
        'Topic': '',
        'Payload': '',
        'QoS': 0
    }


class Mqtt:
    """Les fonctions de base du serveur MQTT"""

    _conn: Optional[Domoticz.Connection] = None
    _mqtt_command_connect = MQTTCommands.CONNECT.value
    _mqtt_command_subscribe = MQTTCommands.SUBSCRIBE.value
    _mqtt_command_publish = MQTTCommands.PUBLISH.value
    _mqtt_connected = False
    _mqtt_id = ''
    _name = 'MQTT_ZW164'
    _cd_publish: Optional[Callable] = None
    _mqtt_error = False
    _cb_suback: Optional[Callable] = None
    MQTT_CONN = {
        'Name': 'MQTT_ZW164',
        **helpers.transport_protocol.TCP_IP_MQTT
    }

    def __init__(self: Mqtt) -> None:
        """Initialisation de la classe"""

    def __str__(self: Mqtt) -> str:
        """str() wrapper"""
        return f'mqtt id: {self._mqtt_id}, connected: {self._mqtt_connected}'

    def _get_id(self: Mqtt) -> str:
        """Unique ID generator"""
        if len(self._mqtt_id) == 0:
            with ZW164Config() as pcf:
                self._mqtt_id = pcf.mqtt_id
                if len(self._mqtt_id) == 0:
                    self._mqtt_id = pcf.mqtt_id = self._name + \
                        '_' + str(time_ns())
        # self._mqtt_id = self._name + '_' + str(time_ns())
        return self._mqtt_id

    def on_start(self: Mqtt, parameters: dict) -> None:
        """place this in `on_start`"""
        self._mqtt_command_connect.update(
            {
                'ID': self._get_id()
            }
        )
        self.MQTT_CONN.update(
            {
                'Address': parameters['Address'],
                'Port': parameters['Port']
            }
        )
        self._conn = Domoticz.Connection(**self.MQTT_CONN)
        if not self._conn.Connected():
            self._conn.Connect()

    def on_stop(self: Mqtt) -> None:
        """place this in `on_stop`"""
        if self._conn is not None:
            self._conn.Send(MQTTCommands.DISCONNECT.value)

    def on_connect(
            self: Mqtt, connection: Domoticz.Connection,
            status: int, _description: str) -> None:
        """place this in `on_connect`"""
        if connection is self._conn:
            if status == 0:
                if not self._mqtt_connected:
                    self._conn.Send(self._mqtt_command_connect)

    def on_message(self: Mqtt, connection: Domoticz.Connection, data: dict) -> None:
        """place this in `on_message`"""
        if connection is self._conn:
            response = MQTTResponse(**data)
            # helpers.debug(response)
            if response.Verb == 'CONNACK':  # follow CONNECT
                if self._connack(response):
                    helpers.status('MQTT connection successfull!')
                    self._conn.Send(self._mqtt_command_subscribe)
            elif response.Verb == 'PUBLISH':  # server send message
                if callable(self._cd_publish):
                    self._cd_publish(response)

    def on_heartbeat(self: Mqtt) -> None:
        """place this in `on_heartbeat`"""
        if self._mqtt_connected:
            self._conn.Send(MQTTCommands.PING.value)

    def on_disconnect(self: Mqtt, connection: Domoticz.Connection):
        """DocString"""
        # if connection is self._conn:
        #     self._mqtt_connected = False
        #     if not self._mqtt_error:
        #         self._conn.Connect()

    def _connack(self: Mqtt, response: MQTTResponse) -> bool:
        """Manage the connack response"""
        if 'Accepted' in response.Description:
            if response.Status == 0:  # success
                self._mqtt_connected = True
                return True
            # anything below is error!
            self._mqtt_error = True
            if response.Status == 5:
                helpers.error("Invalid username or password")
            else:
                helpers.error("Error")
        elif 'Refused' in response.Description:
            helpers.error(response.Description)
            self._mqtt_connected = False
        return False

    def set_publish_callback(self: Mqtt, callback: Callable) -> None:
        """Set the publish callback"""
        self._cd_publish = callback

    def publish(self: Mqtt, topic: str, value: Any) -> None:
        """Publish new message on broker"""
        self._mqtt_command_publish.update(
            {
                'Topic': topic,
                'Payload': str(value)
            }
        )
        self._conn.Send(self._mqtt_command_publish)
