#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""App base"""

# standard libs
from __future__ import annotations

from typing import Dict, Optional

# plugin libs
import Domoticz
import helpers
from app.devices.devices import DzDevices
from app.mqtt.mqtt import Mqtt, MQTTResponse
from app.zwave.soundswitch import CCSSEndpoint, CCSSNodes
from app.zwave.zwave import ZwaveGateway
from domoticz.responses import OnCommandResponse as OCDR
from domoticz.responses import OnConnectResponse as OCTR
from domoticz.responses import OnDeviceRemovedResponse as ODRR
from domoticz.responses import OnDisconnectResponse as ODTR
from domoticz.responses import OnMessageResponse as OMER

__version__ = "2.0.1"
__version_info__ = (2, 0, 1)
__author__ = "Laurent aka Myriades"


class App2:
    """The core V2"""
    _mqtt = Mqtt()
    _zwave_gateway = ZwaveGateway()
    _soundswitches = CCSSNodes()
    _dz_devices = DzDevices()
    _dom_api_plan: Optional[helpers.api.Plan] = None

    def on_start(self: App2, parameters: dict, devices: Dict[int, Domoticz.Device]) -> None:
        """place this in `onStart`"""
        self._mqtt.on_start(parameters)
        self._dz_devices.on_start(devices)
        # Plugin plan
        self._dom_api_plan = helpers.api.Plan(helpers.PluginConfig.plugin_name)
        # self._dom_api_plan.create()

    def on_stop(self: App2) -> None:
        """place this in `onStop`"""
        self._mqtt.on_stop()

    def on_connect(self: App2, octr: OCTR) -> None:
        """place this in `onConnect`"""
        if octr.connection.Name == helpers.api.DOM_API_CON_NAME:
            self._dom_api_plan.next_step()
        else:
            self._mqtt.on_connect(octr)

    def on_disconnect(self: App2, odtr: ODTR) -> None:
        """place this in `onConnect`"""
        self._mqtt.on_disconnect(odtr)

    @helpers.log_func('debug', True, True)
    def on_command(self: App2, ocdr: OCDR) -> None:
        """place this in `onConnect`"""
        command = self._soundswitches.send_command(
            self._dz_devices.get_device_from_unit_id(ocdr.unit).DeviceID,
            ocdr
        )
        if command is not None:
            self._mqtt.publish(**command)

    def on_heartbeat(self: App2) -> None:
        """place this in `onHeartbeat`"""
        self._mqtt.on_heartbeat()

    def on_message(self: App2, omer: OMER) -> None:
        """place this in `onMessage`
        this the place where the plugin starts working
        """
        # Domoticz API response
        if omer.connection.Name == helpers.api.DOM_API_CON_NAME:
            # TODO: fix omer to helpers.requestreponse
            self._dom_api_plan.message(omer)
        else:
            message: Optional[MQTTResponse] = self._mqtt.on_message(omer)
            if isinstance(message, MQTTResponse):
                if message.is_success():
                    if message.Verb == "PUBLISH":
                        self._on_publish(message)
                else:
                    helpers.error(message.Error)

    # @helpers.log_func('debug', True, True)
    def _on_publish(self: App2, response: MQTTResponse) -> None:
        """Recieve message from broker
        #ignore_self_arg
        """
        if response.Topic.startswith("zwave/_CLIENTS/"):
            if response.Topic.endswith("sendCommand"):
                self._soundswitches.update(response.Topic, response.Payload)
                cur_node = self._soundswitches.get_cur_node()
                next_tone_id = self._soundswitches.need_tone_info()
                if next_tone_id:  # next tone info
                    self._mqtt.publish(
                        self._zwave_gateway.command_topic,
                        self._soundswitches.get_tone_info(next_tone_id)
                    )
                else:
                    helpers.status(f'Node {cur_node.node_id} is complete')
                    if self._soundswitches.is_complete():
                        for endpoint in self._soundswitches:
                            self._dz_devices.update(endpoint)
            elif not self._zwave_gateway.is_complete():
                self._zwave_gateway.update(response.Topic, response.Payload)
                if self._zwave_gateway.is_complete():
                    helpers.status(
                        f'Zwave Gateway found: {self._zwave_gateway.response_topic}'
                    )
                    # unsubscribe to global gateway
                    self._mqtt.unsubscribe("zwave/_CLIENTS/#")
                    # subscribe to specific gateway command topic response (sendCommand)
                    self._mqtt.subscribe(self._zwave_gateway.response_topic)
                    # now searching for nodes that have soundswitch endpoints
                    self._mqtt.subscribe('zwave/+/121/+/#')
        else:
            endpoint = self._soundswitches.update(
                response.Topic, response.Payload
            )
            if self._soundswitches.is_new():
                cur_node = self._soundswitches.get_cur_node()
                # subscribing node status
                self._mqtt.subscribe(f'zwave/{cur_node.node_id}/status')
                # send the getToneCount command
                self._mqtt.publish(
                    self._zwave_gateway.command_topic,
                    self._soundswitches.get_tone_count()
                )
            elif self._soundswitches.is_complete():
                if isinstance(endpoint, CCSSEndpoint):
                    self._dz_devices.update(endpoint)

    def on_device_removed(self: App2, odrr: ODRR) -> None:
        """on_device_removed"""
        self._dz_devices.remove_device(odrr)
