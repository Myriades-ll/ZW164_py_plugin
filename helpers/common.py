#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Utilitaires"""

# standards libs
from datetime import datetime
from time import strptime


# Domoticz lib
import Domoticz


def debug(*args: tuple, **kwargs: dict) -> None:
    """Extended log Debug"""
    for key, value in kwargs.items():
        Domoticz.Debug(f'{key.title()}: {value}')
    for arg in args:
        Domoticz.Debug(f'{arg}')


def status(*args: tuple, **kwargs: dict) -> None:
    """Extended log Status"""
    for key, value in kwargs.items():
        Domoticz.Status(f'{key.title()}: {value}')
    for arg in args:
        Domoticz.Status(f'{arg}')


def log(*args: tuple, **kwargs: dict) -> None:
    """Extended log Log"""
    for key, value in kwargs.items():
        Domoticz.Log(f'{key.title()}: {value}')
    for arg in args:
        Domoticz.Log(f'{arg}')


def error(*args: tuple, **kwargs: dict) -> None:
    """Extended log Error"""
    for key, value in kwargs.items():
        Domoticz.Error(f'{key.title()}: {value}')
    for arg in args:
        Domoticz.Error(f'{arg}')


def last_update_2_datetime(last_update: str) -> datetime:
    """conversion de la valeur last_update de domoticz en datetime"""
    if isinstance(last_update, type(None)):
        return datetime.now()
    if isinstance(last_update, datetime):
        return last_update
    dz_format = r'%Y-%m-%d %H:%M:%S'
    try:  # python > 3.7
        last_update_dt = datetime.strptime(
            last_update,
            dz_format
        )
    except TypeError:  # python < 3.8
        try:
            last_update_dt = datetime(
                *(strptime(last_update, dz_format)[0:6])
            )
        except AttributeError:
            Domoticz.Error(f"strptime [ {last_update} <-> {dz_format} ]")
            last_update_dt = datetime.now()
    return last_update_dt

