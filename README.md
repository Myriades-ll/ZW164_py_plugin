# ZW164 plugin for Domoticz

This plugin is intended to get you ability to use of [AEOTEC Ltd. Siren ZW164](https://aeotec.com/products/aeotec-siren-6/)

## Prerequisites

- [Domoticz](https://www.domoticz.com/) functionnal
- A `MQTT Auto Discovery Client Gateway with LAN interface` plugin functionnal

## Tested on

- raspberry pi 4B+; Debian (buster)
- Domoticz - Version: 2022.2
- Python 3.7

## Install

```Shell
git clone https://github.com/Myriades-ll/ZW164_py_plugin.git
sudo systemctl restart domoticz.service
```

## Notes

- might work with every z-wave device that embed the  [COMMAND_CLASS_SOUND_SWITCH](https://z-wave.me/files/manual/z-way/Command_Class_Reference.html#SECTION0016470000000000000000); so the zw164 is not only concerned by this plugin.
- sound names and duration may vary on other hardware.
