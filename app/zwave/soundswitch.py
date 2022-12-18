#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Zwave soundswitch classes"""
# standard libs
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, unique
from json import loads
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Union

# plugin libs
import helpers
from app.zwave.zwave import SendCommandResult
from domoticz.responses import OnCommandResponse as OCDR


class ZW164EnumMethods(Enum):
    """[DOCSTRING]"""
    @classmethod
    def find_value(cls: ZW164EnumMethods, search: int) -> Optional[SoundSwitchToneValues]:
        """recherche l'élément search dans la liste"""
        return cls._find('value', search)

    @classmethod
    def find_name(cls: ZW164EnumMethods, search: str) -> Optional[SoundSwitchToneValues]:
        """recherche l'élément search dans la liste

        @param search (string) le texte à chercher

        @return ZW164Sounds or None
        """
        return cls._find('name', search)

    @classmethod
    def _find(
            cls: ZW164EnumMethods, type_: str,
            search: Union[int, str]) -> Optional[SoundSwitchToneValues]:
        """Recherche de l'élément `search` selon `type`

        @param type_ (string) - <'name', 'value', ''>
        @param search (int, string) - La valeur recherchée

        @return ZW164Sounds or None
        """
        for elm in cls:
            if elm.value[type_] == search:
                return elm
        return None

    @classmethod
    def find_duration(cls: ZW164EnumMethods, search: int) -> Optional[List[SoundSwitchToneValues]]:
        """Find element where duration match

        @return: List[ZW164Sounds] or None
        """
        if cls.__name__ != 'ZW164Sounds':
            return None
        return_list = []
        for elm in cls:
            if elm.value['duration'] == search:
                return_list.append(elm)
        if return_list:
            return return_list
        return None


@unique
class ZW164LightEffects(ZW164EnumMethods):
    """ZW164 light effects"""
    LIGHT_EFFECT_1 = {
        'name': 'Light effect #1',
        'value': 1
    }
    LIGHT_EFFECT_2 = {
        'name': 'Light effect #2',
        'value': 2
    }
    LIGHT_EFFECT_3 = {
        'name': 'Light effect #3',
        'value': 4
    }
    LIGHT_EFFECT_4 = {
        'name': 'Light effect #4',
        'value': 8
    }
    LIGHT_EFFECT_5 = {
        'name': 'Light effect #5',
        'value': 16
    }
    LIGHT_EFFECT_6 = {
        'name': 'Light effect #6',
        'value': 32
    }
    LIGHT_EFFECT_7 = {
        'name': 'Light effect #7',
        'value': 64
    }
    LAST_VALUE = {
        'name': 'Last configuration value',
        'value': 1
    }


@unique
class ZW164PlayModes(ZW164EnumMethods):
    """ZW164 play mode list"""
    SINGLE_PLAYBACK = {
        'name': 'Single playback',
        'value': 0
    }
    SINGLE_LOOP_PLAYBACK = {
        'name': 'Single loop playback',
        'value': 1
    }
    LOOP_PLAYBACK_TONES = {
        'name': 'Loop playback tones',
        'value': 2
    }
    RANDOM_PLAYBACK_TONES = {
        'name': 'Random playback tones',
        'value': 3
    }
    LAST_VALUE = {
        'name': 'Last value',
        'value': 255
    }


@dataclass
class SoundSwitchToneValues:
    """Sound switch tone values"""
    name: str = ""
    duration: int = -1
    tone_id: int = -1

# pylint:disable=invalid-name


@dataclass
class CCSSEndpoint:
    """Endpoint manager"""
    node_id: int
    endpoint_id: int
    tones: Dict[int, SoundSwitchToneValues] = field(
        default_factory=dict, init=False)
    # defaultToneId: int = field(default_factory=int, init=False)
    defaultVolume: int = field(default_factory=int, init=False)
    toneId: int = field(default_factory=int, init=False)
    # volume: int = field(default_factory=int, init=False)

    def update(
            self: CCSSEndpoint, node_id: int, endpoint_id: int,
            topic: str, payload: dict) -> None:
        """update the endpoint"""
        if node_id != self.node_id and endpoint_id != self.endpoint_id:
            return
        if hasattr(self, topic):
            value = payload.get('value')
            if value is not None:
                setattr(self, topic, int(value))

# pylint:enable=invalid-name


@dataclass
class CCSSNode:
    """Node manager"""
    node_id: int
    endpoints: Dict[int, CCSSEndpoint] = field(
        default_factory=dict, init=False)
    status_value: bool = field(default=False, init=False)
    status: str = field(default_factory=str, init=False)
    tones_count: int = field(default_factory=int, init=False)
    tones: Dict[int, SoundSwitchToneValues] = field(
        default_factory=dict, init=False)

    def __post_init__(self: CCSSNode) -> None:
        """post init"""
        # default class sound
        self.tones.update({
            0: SoundSwitchToneValues('Off', 0, 0),
            255: SoundSwitchToneValues('Default', 0, 255)
        })

    def update_endpoint(
            self: CCSSNode, node_id: int, endpoint_id: int,
            topic: str, payload: dict) -> Optional[CCSSEndpoint]:
        """update endpoints dict"""
        if node_id != self.node_id:
            return None
        cur_endpoint = self.endpoints.get(endpoint_id)
        if cur_endpoint is None:
            cur_endpoint = CCSSEndpoint(node_id, endpoint_id)
            self.endpoints.update({endpoint_id: cur_endpoint})
            helpers.status(
                f'New endpoint found: ({self.node_id}){endpoint_id}'
            )
        cur_endpoint.update(node_id, endpoint_id, topic, payload)
        return cur_endpoint

    def update_tone(self: CCSSNode, results: SendCommandResult) -> None:
        """update tones dict"""
        if results.node_id != self.node_id:
            return
        tone_id = results.command_args[0]
        self.tones.update({
            tone_id: SoundSwitchToneValues(
                results.result.get('name')[3:],
                results.result.get('duration'),
                tone_id
            )
        })

    def get_endpoint(self: CCSSNode, endpoint_id: int) -> Optional[CCSSEndpoint]:
        """get_endpoint"""
        return self.endpoints.get(endpoint_id)


class CCSSNodes(Iterable):
    """Nodes manager"""
    _nodes: Dict[int, CCSSNode] = {}
    _is_new = False
    _cur_node: Optional[CCSSNode] = None

    def update(self: CCSSNodes, topic: str, payload: bytes) -> Optional[CCSSEndpoint]:
        """update node/endpoint"""
        self._is_new = False
        if '/121/' in topic:  # is soundswitch commandclass
            return self._update_node_endpoint(topic, payload)
        if topic.endswith("sendCommand"):
            self._update_node_infos(payload)
        elif topic.endswith("status"):
            self._update_status(payload)
        else:
            helpers.error(f'Unexpected topic: {topic}')
        return None

    def _update_node_endpoint(
            self: CCSSNodes, topic: str,
            payload: bytes) -> Optional[CCSSEndpoint]:
        """node update"""
        topic_list = topic.split('/')
        if len(topic_list) == 5:  # endpoint infos
            zwave_node_id = int(topic_list[1])
            self._cur_node = self._nodes.get(zwave_node_id)
            if self._cur_node is None:  # create
                self._is_new = True
                self._cur_node = CCSSNode(zwave_node_id)
                self._nodes.update({zwave_node_id: self._cur_node})
                helpers.status(f'New node found: {zwave_node_id}')
            # update now
            return self._cur_node.update_endpoint(
                zwave_node_id,
                int(topic_list[3]),  # endpoint
                topic_list[-1],  # last topic
                loads(payload)  # converted payload
            )
        return None

    def _update_node_infos(self: CCSSNodes, payload: bytes) -> None:
        """Update node tones (count and infos)"""
        results = SendCommandResult(**loads(payload))
        self._cur_node = self._nodes.get(results.node_id)
        if results.command == 'getToneCount' and isinstance(results.result, int):
            if results.result > 0:
                helpers.status(
                    f'Update tones count: ({self._cur_node.node_id}){results.result}'
                )
                self._cur_node.tones_count = results.result
        if results.command == 'getToneInfo' and isinstance(results.result, dict):
            self._cur_node.update_tone(results)

    def _update_status(self: CCSSNodes, payload: bytes) -> None:
        """Update node status"""
        results: dict = loads(payload)
        self._cur_node = self._nodes.get(results.get('nodeId'))
        self._cur_node.status_value = results.get('value')
        self._cur_node.status = results.get('status')

    def is_new(self: CCSSNodes) -> bool:
        """check if the current node is new"""
        return self._is_new

    def is_complete(self: CCSSNodes) -> bool:
        """Check if the current node is alive and completely acquired"""
        return self._cur_node.status_value and not self.need_tone_info()

    def need_tone_info(self: CCSSNodes) -> int:
        """Return the next tone_id; 0 if no more"""
        tones_info_left: Set[int] = (
            set(range(1, self._cur_node.tones_count + 1))
            - set(self._cur_node.tones)
        )
        if len(tones_info_left) > 0:
            return tones_info_left.pop()
        return 0

    def get_cur_node(self: CCSSNodes) -> CCSSNode:
        """return the current node"""
        return self._cur_node

    def __repr__(self: CCSSNodes) -> str:
        """repr() wrapper"""
        return f'CCSSNodes({self._nodes})'

    def __iter__(self: CCSSNodes) -> Iterator[CCSSEndpoint]:
        """for ... in ... wrapper"""
        for cur_node in self._nodes.values():
            for endpoint in cur_node.endpoints.values():
                endpoint.tones = cur_node.tones.copy()
                yield endpoint
                endpoint.tones.clear()

    def get_tone_count(self: CCSSNodes) -> dict:
        """return the getToneCount command"""
        return {
            "args": [
                {
                    "nodeId": self._cur_node.node_id,
                    "commandClass": 121,
                    "endpoint": 0
                },
                "getToneCount",
                []
            ]
        }

    def get_tone_info(self: CCSSNodes, tone_id: int) -> dict:
        """return the getToneInfo command"""
        return {
            "args": [
                {
                    "nodeId": self._cur_node.node_id,
                    "commandClass": 121,
                    "endpoint": 0
                },
                "getToneInfo",
                [tone_id]
            ]
        }

    def send_command(
            self: CCSSNode, device_id: str, ocdr: OCDR) -> Optional[Dict[str, Any]]:
        """send_command"""
        node_id, endpoint_id, topic = device_id.split('_')
        self._cur_node = self._nodes.get(int(node_id))
        if self._cur_node is not None:
            endpoint = self._cur_node.get_endpoint(int(endpoint_id))
            if endpoint is not None:
                value = 0
                if ocdr.command == 'Set Level':
                    if topic == 'defaultVolume':
                        value = ocdr.level
                    elif topic == 'toneId':
                        if ocdr.level == (self._cur_node.tones_count + 1) * 10:
                            value = 255
                        else:
                            value = ocdr.level / 10
                command = {
                    'topic': f'zwave/{node_id}/121/{endpoint_id}/{topic}/set',
                    'payload': int(value)
                }
                return command
            helpers.error(
                f'<CCSSNode.send_command> Endpoint {endpoint_id} not found in node {node_id}'
            )
        helpers.error(f'<CCSSNode.send_command> Node {node_id} not found')
        return None
