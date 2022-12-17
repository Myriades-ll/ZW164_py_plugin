#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""MQTT manager classes"""

# standard libs
from __future__ import annotations

from dataclasses import asdict, astuple, dataclass, field
from json import dumps
from time import time, time_ns
from typing import Any, Dict, List, Optional, Union

# App libs
import Domoticz
import helpers
from app.config import ZW164Config
from domoticz.responses import OnConnectResponse as OCTR
from domoticz.responses import OnDisconnectResponse as ODTR
from domoticz.responses import OnMessageResponse as OMER


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

    def is_success(self: MQTTResponse) -> bool:
        """check if message is success"""
        return not bool(self.Error)

# region - Mqtt command datas
# pylint:disable=invalid-name


@dataclass
class _MqttBaseCommand:
    """MqttBaseCommand"""
    Verb: str = field(default_factory=str, init=False)

    def as_dict(self: _MqttBaseCommand) -> dict:
        """
        @return self as dict
        """
        return asdict(self)

    def as_tuple(self: _MqttBaseCommand) -> tuple:
        """
        @return self as tuple
        """
        return astuple(self)

    def as_list(self: _MqttBaseCommand) -> list:
        """
        @return self as list
        """
        return list(self.as_tuple())

    def as_json(self: _MqttBaseCommand) -> str:
        """return self as json"""
        return dumps(self.as_dict())


@dataclass
class MqttPing(_MqttBaseCommand):
    """MqttPing"""

    def __post_init__(self: MqttPing) -> None:
        """post init"""
        self.Verb = "PING"


@dataclass
class MqttDisconnect(_MqttBaseCommand):
    """MqttDisconnect"""

    def __post_init__(self: MqttDisconnect) -> None:
        """__init__"""
        self.Verb = "DISCONNECT"


@dataclass
class MqttConnect(_MqttBaseCommand):
    """MqttConnect"""
    ID: str = field(default_factory=str)
    CleanSession: int = field(default=1)
    WillTopic: int = field(default_factory=int)
    WillQoS: int = field(default_factory=int)
    WillRetain: int = field(default_factory=int)
    WillPayload: int = field(default_factory=int)

    def __post_init__(self: MqttConnect) -> None:
        """__init__"""
        self.Verb = "CONNECT"


@dataclass
class MqttSubscribe(_MqttBaseCommand):
    """MqttSubscribe
    @var Topics is a `list` of `dict`. Each dict is defined as below
    {
        'Topic' : 'foo', # (str)
        'Qos' : 0 # (int)
    }
    """
    Topics: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self: MqttSubscribe) -> None:
        """__init__"""
        self.Verb = "SUBSCRIBE"


@dataclass
class MqttUnsubscribe(_MqttBaseCommand):
    """MqttUnsubscribe
    @var Topics is a `list` of `str`
    """
    Topics: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self: MqttUnsubscribe) -> None:
        """__init__"""
        self.Verb = "UNSUBSCRIBE"


@dataclass
class MqttPublish(_MqttBaseCommand):
    """MqttPublish"""
    Topic: str
    Payload: str
    QoS: int = field(default=0)

    def __post_init__(self: MqttPublish) -> None:
        """__init__"""
        self.Verb = "PUBLISH"


# pylint:enable=invalid-name
# endregion


class Mqtt:
    """Les fonctions de base du serveur MQTT"""

    _conn: Optional[Domoticz.Connection] = None
    _last_request_time = 0
    _mqtt_connected = False
    _mqtt_id = ''
    _name = 'MQTT_ZW164'
    _mqtt_error = False
    MQTT_CONN = {
        'Name': '',
        **helpers.transport_protocol.TCP_IP_MQTT
    }

    def __init__(self: Mqtt) -> None:
        """Initialisation de la classe"""
        self.MQTT_CONN.update({'Name': self._name})

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
        return self._mqtt_id

    def on_start(self: Mqtt, parameters: dict) -> None:
        """place this in `on_start`"""
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
        if isinstance(self._conn, Domoticz.Connection):
            if self._conn.Connected():
                self._conn.Send(MqttDisconnect().as_dict())

    def on_connect(self: Mqtt, octr: OCTR) -> None:
        """place this in `on_connect`"""
        if octr.connection is self._conn:
            if not self._mqtt_connected:
                mqtt_connect = MqttConnect()
                mqtt_connect.ID = self._get_id()
                self._send_domoticz(mqtt_connect)

    def on_message(self: Mqtt, omer: OMER) -> Optional[Any]:
        """place this in `on_message`"""
        self._last_request_time = time()
        if omer.connection is self._conn:
            response = MQTTResponse(**omer.data)
            if response.Verb == 'CONNACK':  # follow CONNECT
                if self._on_connack(response):
                    helpers.status('MQTT connection successfull!')
                    # searching for zwave-js-ui command topic
                    self.subscribe(
                        'zwave/_CLIENTS/#'
                    )
            elif response.Verb == 'PUBLISH':  # server send message
                return response
        return None

    def on_heartbeat(self: Mqtt) -> None:
        """place this in `on_heartbeat`"""
        if self._mqtt_connected and self._last_request_time + 5 < time():
            self._send_domoticz(MqttPing())

    def on_disconnect(self: Mqtt, odtr: ODTR):
        """on_disconnect"""
        if odtr.connection is self._conn:
            self._mqtt_connected = False
            if not self._mqtt_error:
                self._conn.Connect()

    def publish(self: Mqtt, topic: str, payload: Any) -> None:
        """Publish new message on broker"""
        mqtt_publish = MqttPublish(topic, dumps(payload))
        self._send_domoticz(mqtt_publish)

    def subscribe(self: Mqtt, topic: Union[str, List[str]], qos: int = 0) -> None:
        """Subscribe to topic"""
        topic_list = []
        if isinstance(topic, list):
            for item in topic:
                topic_list.append({
                    'Topic': item,
                    'QoS': qos
                })
        elif isinstance(topic, str):
            topic_list.append({
                'Topic': topic,
                'QoS': qos
            })
        else:
            helpers.error(
                f'No valid topic type to subscribe: ({type(topic)}){topic}'
            )
            return
        self._send_domoticz(MqttSubscribe(topic_list))

    def unsubscribe(self: Mqtt, topic: str) -> None:
        """Unsubscribe topic from broker"""
        topic_list = []
        if isinstance(topic, str):
            topic_list.append(topic)
        else:
            helpers.error(
                f'No valid topic type to subscribe: ({type(topic)}){topic}'
            )
            return
        self._send_domoticz(MqttUnsubscribe(topic_list))

    def _on_connack(self: Mqtt, response: MQTTResponse) -> bool:
        """Manage the connack response"""
        if 'Accepted' in response.Description:
            if response.Status == 0:  # success
                self._mqtt_connected = True
                return True
            # anything below is error!
            self._mqtt_error = True
            if response.Status == 5:
                helpers.error(
                    f"Invalid username or password: {response.Error}"
                )
            else:
                helpers.error(f"Error: ({response.Status}){response.Error}")
        elif 'Refused' in response.Description:
            helpers.error(response.Description)
            self._mqtt_connected = False
        else:
            helpers.error(f"""
                Unknown MQTT response: {response.Description})
                Please send feedback: https://github.com/Myriades-ll/ZW164_py_plugin/issues
            """)
        return False

    def is_connected(self: Mqtt) -> bool:
        """@return `True` if connected and auth, else `False`"""
        return self._mqtt_connected

    def _send_domoticz(self: Mqtt, datas: _MqttBaseCommand) -> None:
        """Send datas through domoticz connection"""
        self._conn.Send(datas.as_dict())
