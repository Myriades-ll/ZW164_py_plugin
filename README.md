<!-- TODO: rewrite/read everything -->
# Zwave SoundSwitch CommandClass -  plugin for Domoticz

![GitHub release (latest by date)][release_shield] ![Domoticz 2022.2][domoticz_shield] ![Python version][python_shield] ![Zwave JS-UI version][zjsui_shield]

This plugin is intended to get you the ability to use the [AEOTEC Ltd. Siren ZW164](https://aeotec.com/products/aeotec-siren-6/)

## Prerequisites

- [Domoticz](https://www.domoticz.com/) functionnal
- A `MQTT Auto Discover Client Gateway with LAN interface` plugin functionnal

## Tested on

- raspberry pi 4B+; Debian (buster)
- Domoticz - Version: 2022.2
- Python 3.7

### functionnal hardwares

- AOETEC ZW164
- AOETEC ZW162

Please, send feedback for your onw hardware; not listed above

## Install

In your domoticz plugin folder:

```Shell
git clone https://github.com/Myriades-ll/ZW164_py_plugin.git
sudo systemctl restart domoticz.service
```

## Configuration

### Zwave-js-ui

Set the retain flag ON
![retain flag](/pictures/zjsui_retain.png "Retain flag")

### Domoticz

Add the new hardware named `CCSoundSwitch through Zwave-JS-UI`. Feed param fields, then start the plugin.

## Usage

For every endpoint in your hardware, the plugin will create 2 devices:

- the first to control the volume
- the second to select the sound you want to play

Each device represent the actual values of your hardware.

So first, adjust the volume and then select a sound to play it instantly.

## Limits

You can't change actual volume while playing a sound. It will change for the next sound.

If you turn off the volume, the endpoint won't play anymore sound; it will be skipped.

## Notes

- might work with every z-wave device that embed the  [COMMAND_CLASS_SOUND_SWITCH](https://z-wave.me/files/manual/z-way/Command_Class_Reference.html#SECTION0016470000000000000000).

[def_retain_flag]: [retain flag](https://github.com/Myriades-ll/ZW164_py_plugin/blob/Dev/pictures/zjsui_retain.png) "Retain flag"
[domoticz_shield]: <https://img.shields.io/badge/Domoticz-2022.2-brightgreen>
[python_shield]: <https://img.shields.io/badge/Python-3.7-brightgreen>
[zjsui_shield]: <https://img.shields.io/badge/Python-3.7-brightgreen>
[release_shield]: <https://img.shields.io/github/v/release/Myriades-ll/ZW164_py_plugin?color=green&logo=Version&style=flat>
