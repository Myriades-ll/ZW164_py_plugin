#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# pylint: disable=line-too-long
"""
<plugin key="zw164_pyplug" name="CCSoundSwitch through Zwave-JS-UI" author="Myriades" version="2.1.0" wikilink="https://github.com/Myriades-ll/ZW164_py_plugin/blob/master/README.md">
    <params>
        <param field="Address" label="IP du broker MQTT" width="100px" required="true" default="IPV4 (eg: 127.0.0.1)"/>
        <param field="Port" label="Port" width="50px" required="true" default="1883"/>
        <param field="Username" label="MQTT login" width="150px"/>
        <param field="Password" label="MQTT password" width="150px" password="true"/>
        <param field="Mode1" label="Plan name" width="100px"/>
        <param field="Mode6" label="Debugging">
            <options>
                <option label="Nothing" value="0" default="true" />
                <option label="All" value="1" />
                <option label="Python - all" value="2.0" />
                <option label="Python - Plugin" value="2.1" />
                <option label="Python - Zwave" value="2.2" />
                <option label="Python - MQTT" value="2.3" />
            </options>
        </param>
    </params>
</plugin>
"""
# pylint: enable=line-too-long

# standard libs

# plugin libs
import app
import domoticz
import helpers

__version__ = "2.1.1"
__version_info__ = (2, 1, 1)
__author__ = "Laurent aka Myriades"

APP2 = app.App2()


def onStart() -> None:  # pylint:disable=invalid-name
    """Démarrage du plugin"""
    # pylint:disable=undefined-variable

    # Configuration, parameters, ...
    helpers.PluginConfig(Parameters)

    # now start
    APP2.on_start(Parameters, Devices)
    # pylint:enable=undefined-variable


@helpers.log_func('debug', separator_line=True)
def onStop() -> None:  # pylint: disable=invalid-name
    """onStop"""
    APP2.on_stop()


@domoticz.on_event
def onConnect(octr: domoticz.OnConnectResponse) -> None:  # pylint: disable=invalid-name
    """onConnect"""
    if octr.is_success():
        APP2.on_connect(octr)
    else:
        helpers.error(octr)


@domoticz.on_event
def onMessage(omer: domoticz.OnMessageResponse) -> None:  # pylint: disable=invalid-name
    """onMessage"""
    APP2.on_message(omer)


@domoticz.on_event
def onCommand(ocdr: domoticz.OnCommandResponse) -> None:  # pylint: disable=invalid-name
    """onCommand"""
    APP2.on_command(ocdr)


@helpers.log_func('debug', separator_line=True)
def onNotification(*_args: tuple) -> None:  # pylint: disable=invalid-name
    """onNotification"""


@domoticz.on_event
def onDisconnect(odtr: domoticz.OnDisconnectResponse) -> None:  # pylint: disable=invalid-name
    """onDisconnect"""
    APP2.on_disconnect(odtr)


@helpers.log_func('debug', separator_line=True)
def onHeartbeat() -> None:  # pylint: disable=invalid-name
    """onHeartbeat"""
    APP2.on_heartbeat()


@helpers.log_func('debug', separator_line=True)
def onDeviceModified(*_args: tuple) -> None:  # pylint: disable=invalid-name
    """onDeviceModified"""


@helpers.log_func('debug', separator_line=True)
def onTimeout(*_args: tuple) -> None:  # pylint: disable=invalid-name
    """onTimeout"""


@helpers.log_func('debug', separator_line=True)
def onDeviceAdded(*_args: tuple) -> None:  # pylint: disable=invalid-name
    """onDeviceAdded"""


@domoticz.on_event
def onDeviceRemoved(odrr: domoticz.OnDeviceRemovedResponse) -> None:  # pylint: disable=invalid-name
    """onDeviceRemoved"""
    APP2.on_device_removed(odrr)


@helpers.log_func('debug', separator_line=True)
def onSecurityEvent(*_args: tuple) -> None:  # pylint: disable=invalid-name
    """onSecurityEvent"""
