<!-- TODO: rewrite/read everything -->
# Zwave SoundSwitch CommandClass -  plugin for Domoticz

![GitHub release (latest by date)][release_shield] ![Domoticz 2022.2][domoticz_shield] ![Python version][python_shield] ![Zwave JS-UI version][zjsui_shield]

This plugin is intended to get you the ability to use Zwave hardwares that embed the [COMMAND_CLASS_SOUND_SWITCH (0x79|121)][def_CCSS]

## Prerequisites

- [Domoticz](https://www.domoticz.com/) functional
- A **MQTT Auto Discover Client Gateway with LAN interface** plugin functional

## functional hardwares

- [AEOTEC Siren 6 (ZW164)](https://aeotec.com/products/aeotec-siren-6)
- [AEOTEC Doorbell 6 (ZW162)](https://aeotec.com/products/aeotec-doorbell-6)

Please, send feedback for your onw hardware; not listed above ;)

## Install

In your domoticz plugin folder:

```Shell
git clone https://github.com/Myriades-ll/ZW164_py_plugin.git
sudo systemctl restart domoticz.service
```

## Configuration

### Zwave-js-ui

Set the retain flag **ON** like in the picture below. This plugin don't use the autodiscovery. It has his own system. You may have to restart zwave-js-ui to get topic retained working.

![retain flag][def_retain_flag]

### Domoticz

Add the new hardware named **CCSoundSwitch through Zwave-JS-UI**. Fill required fields, then start the plugin.

Plugin initialization may take a few time; at most 30 seconds; it has to retrieve some data from hardware.

## Usage

For every endpoint in your hardware, the plugin will create 2 devices:

- the first to control the volume
- the second to select the sound you want to play

Each device represent the actual values of your hardware.

So first, adjust the volume and then select a sound to play it instantly.

## Limits

You can't change actual volume while playing a sound. It will change for the next sound.

If you turn off the volume, the endpoint won't play anymore sound; it will be skipped.

[domoticz_shield]: <https://img.shields.io/badge/Domoticz-2022.2-brightgreen>
[python_shield]: <https://img.shields.io/badge/Python-3.7-brightgreen>
[zjsui_shield]: <https://img.shields.io/badge/Zwave_JS_UI-8.4.1-brightgreen>
[release_shield]: <https://img.shields.io/github/v/release/Myriades-ll/ZW164_py_plugin?color=green&logo=Version&style=flat>
[def_retain_flag]: /pictures/zjsui_retain.png "Retain flag"
[def_CCSS]: https://z-wave.me/files/manual/z-way/Command_Class_Reference.html#SECTION0016470000000000000000
