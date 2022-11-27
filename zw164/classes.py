#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# ZW164 app
"""ZW164 manager classes"""

# standard libs
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

# App libs
import helpers
from mqtt.classes import MQTTResponse


@dataclass
class ZW164Payload:
    """ZW164 payload"""
    payload: bytes = b''
    time: int = field(default=0)
    value: int = field(default=-1)
    # pylint:disable=invalid-name
    nodeName: str = field(default_factory=str)
    nodeLocation: str = field(default_factory=str)
    # pylint:enable=invalid-name

    def __post_init__(self: ZW164Payload) -> None:
        """post init"""
        tmp = json.loads(self.payload)
        if isinstance(tmp, dict):
            for key, value in tmp.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    helpers.error(
                        f'Payload unknown key: {key}=({type(value)}){value}'
                    )

    def update_payload(self: ZW164Payload, payload: bytes) -> None:
        """mise à jour"""
        self.payload = payload
        self.__post_init__()


class ZW164Node:
    """ZW164 node details"""
    node_id = 0
    switch_id = 0
    topics: Dict[str, ZW164Payload] = {}

    def __init__(self: ZW164Node, node_id: int, switch_id: int, topic: str, payload: bytes) -> None:
        """Initialisation de la classe"""
        self.node_id = node_id
        self.switch_id = switch_id
        self.topics.update({topic: ZW164Payload(payload)})

    def __str__(self: ZW164Node) -> str:
        """str() wWrapper"""
        return f'Node ID: {self.node_id}, switch ID: {self.switch_id}, topics: {self.topics}'

    def __repr__(self: ZW164Node) -> str:
        """repr() wrapper"""
        return str(self)

    def update(self: ZW164Node, topic: str, payload: bytes) -> None:
        """Mise à jour"""
        topic_ = self.topics.get(topic)
        if topic_ is None:
            self.topics.update({topic: ZW164Payload(payload)})
        else:
            topic_.update_payload(payload)


class ZW164Nodes:
    """The zw164 manager"""
    nodes: Dict[str, ZW164Node] = {}
    _cur_node = 0
    _cur_node_index: str = ""
    _topics = [
        'defaultVolume',
        'defaultToneId',
        'toneId',
        'volume'
    ]
    _publish_callback: Optional[Callable] = None

    def cb_publish(self: ZW164Nodes, response: MQTTResponse) -> None:
        """publish callback"""
        self._update_node(response)
        if callable(self._publish_callback):
            # helpers.debug(self._cur_node)
            self._publish_callback(self._cur_node)

    def set_publish_callback(self: ZW164Nodes, callback: Callable) -> None:
        """Set the publish callback"""
        self._publish_callback = callback

    @ staticmethod
    def _build_hex_number(value: int) -> str:
        """Build an hex number like 32 -> 20; adding leading zero if needed"""
        return ('000' + hex(value)[2:].upper())[-4:]

    def _update_node(self: ZW164Nodes, response: MQTTResponse) -> None:
        """Mise à jour du noeud"""
        topic_details = response.Topic.split('/')
        if len(topic_details) == 5:

            # zwave node
            zwave_node_id = int(topic_details[1])
            switch_sound_id = int(topic_details[3])
            switch_topic = topic_details[-1]
            if switch_topic not in self._topics:
                helpers.error(f'unknown topic: {switch_topic}')
                return
            self._cur_node_index = (
                self._build_hex_number(zwave_node_id) +
                self._build_hex_number(switch_sound_id)
            )
            self._cur_node = self.nodes.get(self._cur_node_index)
            if self._cur_node is None:
                self._cur_node = ZW164Node(
                    zwave_node_id,
                    switch_sound_id,
                    switch_topic,
                    response.Payload
                )
                self.nodes.update(
                    {
                        self._cur_node_index: self._cur_node
                    }
                )
            else:
                self._cur_node.update(switch_topic, response.Payload)

    def __str__(self) -> str:
        """Wrapper pour str()"""
        return str(self.nodes)

    def __repr__(self) -> str:
        """Wrapper pour repr()"""
        return str(self.nodes)
