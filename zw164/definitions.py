"""ZW164 définitions"""

# stabdard libs
from __future__ import annotations

from enum import Enum, unique
from typing import List, Optional, Union


class ZW164EnumMethods(Enum):
    """[DOCSTRING]"""
    @classmethod
    def find_value(cls: ZW164EnumMethods, search: int) -> Optional[ZW164Sounds]:
        """recherche l'élément search dans la liste"""
        return cls._find('value', search)

    @classmethod
    def find_name(cls: ZW164EnumMethods, search: str) -> Optional[ZW164Sounds]:
        """recherche l'élément search dans la liste

        @param search (string) le texte à chercher

        @return ZW164Sounds or None
        """
        return cls._find('name', search)

    @classmethod
    def _find(cls: ZW164EnumMethods, type_: str, search: Union[int, str]) -> Optional[ZW164Sounds]:
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
    def find_duration(cls: ZW164EnumMethods, search: int) -> Optional[List[ZW164Sounds]]:
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


@unique
class ZW164Sounds(ZW164EnumMethods):
    """ZW164 sound list"""
    OFF = {
        'name': 'Off',
        'value': 0,
        'duration': 0,
    }
    DING_DONG = {
        'name': 'Ding dong',
        'value': 1,
        'duration': 5
    }
    DING_DONG_TUBULAR = {
        'name': 'Ding dong tubular',
        'value': 2,
        'duration': 9
    }
    TRADITIONAL_APARTMENT_BUZZER = {
        'name': 'Traditional Apartment buzzer',
        'value': 3,
        'duration': 10
    }
    ELECTRIC_APARTMENT_BUZZER = {
        'name': 'Electric apartment buzzer',
        'value': 4,
        'duration': 1
    }
    WESTMINSTER_CHIMES = {
        'name': 'Westminster chimes',
        'value': 5,
        'duration': 12
    }
    CHIMES = {
        'name': 'Chimes',
        'value': 6,
        'duration': 7
    }
    CUCKOO = {
        'name': 'Cuckoo',
        'value': 7,
        'duration': 31
    }
    TRADITIONAL_BELL = {
        'name': 'Traditional bell',
        'value': 8,
        'duration': 6
    }
    SMOKE_ALARM_1 = {
        'name': 'Smoke alarm 1',
        'value': 9,
        'duration': 11
    }
    SMOKE_ALARM_2 = {
        'name': 'Smoke alarm 2',
        'value': 10,
        'duration': 5
    }
    FIRE_EVACUATION_BUZZER = {
        'name': 'Fire evacuation buzzer',
        'value': 11,
        'duration': 35
    }
    CO_SENSOR = {
        'name': 'CO sensor',
        'value': 12,
        'duration': 4
    }
    KLAXON = {
        'name': 'Klaxon',
        'value': 13,
        'duration': 6
    }
    DEEP_KLAXON = {
        'name': 'Deep klaxon',
        'value': 14,
        'duration': 40
    }
    WARNING_TONE = {
        'name': 'Warning tone',
        'value': 15,
        'duration': 37
    }
    TORNADO_SIREN = {
        'name': 'Tornado siren',
        'value': 16,
        'duration': 45
    }
    ALARM = {
        'name': 'Alarm',
        'value': 17,
        'duration': 35
    }
    DEEP_ALARM = {
        'name': 'Deep alarm',
        'value': 18,
        'duration': 62
    }
    ALARM_ARCHANGEL = {
        'name': 'Alarm Archangel',
        'value': 19,
        'duration': 15
    }
    ALARM_SHRILL = {
        'name': 'Alarm shrill',
        'value': 20,
        'duration': 7
    }
    DIGITAL_SIREN = {
        'name': 'Digital siren',
        'value': 21,
        'duration': 8
    }
    ALERT_SERIES = {
        'name': 'Alert series',
        'value': 22,
        'duration': 63
    }
    SHIP_BELL = {
        'name': 'Ship bell',
        'value': 23,
        'duration': 3
    }
    CLOCK_BUZZER = {
        'name': 'Clock buzzer',
        'value': 24,
        'duration': 9
    }
    CHRISTMAS_TREE = {
        'name': 'Christmas tree',
        'value': 25,
        'duration': 3
    }
    GONG = {
        'name': 'Gong',
        'value': 26,
        'duration': 11
    }
    SINGLE_BELL_TING = {
        'name': 'Single bell ting',
        'value': 27,
        'duration': 0
    }
    TONAL_PULSE = {
        'name': 'Tonal pulse',
        'value': 28,
        'duration': 11
    }
    UPWARDS_TONE = {
        'name': 'Upwards tone',
        'value': 29,
        'duration': 2
    }
    DOOR_OPEN = {
        'name': 'Door open',
        'value': 30,
        'duration': 27
    }
    DEFAULT = {
        'name': 'Default',
        'value': 255,
        'duration': 0
    }


# region -> tests
if __name__ == '__main__':
    print(ZW164Sounds.find_value(2))
    print(ZW164Sounds.find_name('Ding dong'))
    print(ZW164Sounds.find_duration(35))

    print(ZW164PlayModes.find_value(2))
    print(ZW164PlayModes.find_name('Single loop playback'))
# endregion
