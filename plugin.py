#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Freebox Python Plugin

# pylint: disable=line-too-long
"""
<plugin key="zw164_pyplug" name="ZW164 through Zwave-JS-UI" author="Myriades" version="1.0.0" wikilink="https://github.com/Myriades-ll/FreeBox/blob/Dev/README.md">
    <params>
        <param field="Address" label="IP du broker MQTT" width="100px" required="true" default="IPV4 (eg: 127.0.0.1)"/>
        <param field="Port" label="Port" width="50px" required="true" default="1883"/>
        <param field="Username" label="MQTT login" width="150px" required="true"/>
        <param field="Password" label="MQTT password" width="150px" required="true" password="true"/>
        <param field="Mode1" label="Plan name" width="100px"/>
        <param field="Mode6" label="Debugging">
            <options>
                <option label="Nothing" value="0" default="true" />
                <option label="All" value="1" />
                <option label="Python - all" value="2.0" />
                <option label="Python - Plugin" value="2.1" />
                <option label="Python - ZW164" value="2.2" />
                <option label="Python - MQTT" value="2.3" />
            </options>
        </param>
    </params>
</plugin>
"""
# pylint: enable=line-too-long

# standard libs

# plugin libs
import helpers
from app import DomXZW164
from mqtt import Mqtt
from zw164 import ZW164Nodes

DOMXZW164 = DomXZW164()
MQTT = Mqtt()
ZW164 = ZW164Nodes()
# pylint:enable=undefined-variable


__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__author__ = "Laurent aka Myriades"


def onStart():  # pylint:disable=invalid-name
    """Démarrage du plugin"""
    # pylint:disable=undefined-variable

    # Configuration, parameters, ...
    helpers.PluginConfig(Parameters)

    # publish callbacks
    ZW164.set_publish_callback(DOMXZW164.cb_publish)
    MQTT.set_publish_callback(ZW164.cb_publish)
    DOMXZW164.set_publish_callback(MQTT.publish)

    # now start
    DOMXZW164.on_start(Devices)
    MQTT.on_start(Parameters)
    # pylint:enable=undefined-variable


@helpers.log_func('debug', separator_line=True)
def onStop():  # pylint: disable=invalid-name
    """onStop"""
    MQTT.on_stop()


@helpers.log_func('debug', separator_line=True)
def onConnect(*args):  # pylint: disable=invalid-name
    """onConnect"""
    status: int = args[1]
    if status == 0:  # Success
        MQTT.on_connect(*args)
    else:
        for arg in args:
            helpers.error(arg)


@helpers.log_func('debug', separator_line=True)
def onMessage(*args):  # pylint: disable=invalid-name
    """onMessage"""
    MQTT.on_message(*args)



@helpers.log_func('debug', separator_line=True)
def onCommand(*args):  # pylint: disable=invalid-name
    """onCommand"""
    DOMXZW164.on_command(*args)


@helpers.log_func('debug', separator_line=True)
def onNotification(*_args):  # pylint: disable=invalid-name
    """onNotification"""


@helpers.log_func('debug', separator_line=True)
def onDisconnect(*args):  # pylint: disable=invalid-name
    """onDisconnect"""
    MQTT.on_disconnect(*args)


@helpers.log_func('debug', separator_line=True)
def onHeartbeat() -> None:  # pylint: disable=invalid-name
    """onHeartbeat"""
    MQTT.on_heartbeat()


@helpers.log_func('debug', separator_line=True)
def onDeviceModified(*_args) -> None:  # pylint: disable=invalid-name
    """onDeviceModified"""


@helpers.log_func('debug', separator_line=True)
def onTimeout(*_args) -> None:  # pylint: disable=invalid-name
    """onTimeout"""


@helpers.log_func('debug', separator_line=True)
def onDeviceAdded(*_args) -> None:  # pylint: disable=invalid-name
    """onDeviceAdded"""


@helpers.log_func('debug', log_args=True, separator_line=True)
def onDeviceRemoved(*args) -> None:  # pylint: disable=invalid-name
    """onDeviceRemoved"""
    DOMXZW164.on_device_removed(*args)


@helpers.log_func('debug', separator_line=True)
def onSecurityEvent(*_args) -> None:  # pylint: disable=invalid-name
    """onSecurityEvent"""
