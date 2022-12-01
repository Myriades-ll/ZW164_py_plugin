# ZW164 plugin for Domoticz

This plugin is intended to get you the ability to use the [AEOTEC Ltd. Siren ZW164](https://aeotec.com/products/aeotec-siren-6/)

## Prerequisites

- [Domoticz](https://www.domoticz.com/) functionnal
- A `MQTT Auto Discovery Client Gateway with LAN interface` plugin functionnal

## Tested on

- raspberry pi 4B+; Debian (buster)
- Domoticz - Version: 2022.2
- Python 3.7

## Install

`git clone https://github.com/Myriades-ll/ZW164_py_plugin.git`

## Usage

For every endpoint in the hardware; 8 in the ZW164; the plugin will create 2 devices:

- the first to control the volume
- the second to select the sound you want to play; over a choice of 30

Each device represent the actual values of your hardware.

So first, adjust the volume and then select a sound to play it instantly.

## Limitation

You can't change actual volume while playing a sound. It will change for the next sound. If you turn off the volume, the endpoint won't play anymore sound; it will be skipped.
Endpoints have 4 levels of priority. Please refer to [ZW164 spec_tech](https://aeotec.freshdesk.com/helpdesk/attachments/6086177008) (pdf file)

## Notes

- might work with every z-wave device that embed the  [COMMAND_CLASS_SOUND_SWITCH](https://z-wave.me/files/manual/z-way/Command_Class_Reference.html#SECTION0016470000000000000000); so the zw164 is not only concerned by this plugin.
- sound names and duration may vary on other hardware.

## TODO

- retrieve sounds name and duration from hardware and for each endpoint
