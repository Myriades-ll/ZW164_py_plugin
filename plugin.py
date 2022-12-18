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
import helpers
import app
from domoticz.responses import OnConnectResponse as OCTR
from domoticz.responses import OnDisconnectResponse as ODTR
from domoticz.responses import OnMessageResponse as OMER
from domoticz.responses import OnDeviceRemovedResponse as ODRR
from domoticz.responses import OnCommandResponse as OCDR

__version__ = "2.1.0"
__version_info__ = (2, 1, 0)
__author__ = "Laurent aka Myriades"

APP2 = app.App2()


def onStart():  # pylint:disable=invalid-name
    """Démarrage du plugin"""
    # pylint:disable=undefined-variable

    # Configuration, parameters, ...
    helpers.PluginConfig(Parameters)

    # now start
    APP2.on_start(Parameters, Devices)
    # pylint:enable=undefined-variable


@helpers.log_func('debug', separator_line=True)
def onStop():  # pylint: disable=invalid-name
    """onStop"""
    APP2.on_stop()


@helpers.log_func('debug', separator_line=True)
def onConnect(*args):  # pylint: disable=invalid-name
    """onConnect"""
    octr = OCTR(*args)
    if octr.is_success():
        APP2.on_connect(octr)
    else:
        helpers.error(octr)


@helpers.log_func('debug', separator_line=True)
def onMessage(*args):  # pylint: disable=invalid-name
    """onMessage"""
    APP2.on_message(OMER(*args))


@helpers.log_func('debug', separator_line=True)
def onCommand(*args):  # pylint: disable=invalid-name
    """onCommand"""
    APP2.on_command(OCDR(*args))


@helpers.log_func('debug', separator_line=True)
def onNotification(*_args):  # pylint: disable=invalid-name
    """onNotification"""


@helpers.log_func('debug', separator_line=True)
def onDisconnect(*args):  # pylint: disable=invalid-name
    """onDisconnect"""
    APP2.on_disconnect(ODTR(*args))


@helpers.log_func('debug', separator_line=True)
def onHeartbeat() -> None:  # pylint: disable=invalid-name
    """onHeartbeat"""
    APP2.on_heartbeat()


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
    APP2.on_device_removed(ODRR(*args))


@helpers.log_func('debug', separator_line=True)
def onSecurityEvent(*_args) -> None:  # pylint: disable=invalid-name
    """onSecurityEvent"""
