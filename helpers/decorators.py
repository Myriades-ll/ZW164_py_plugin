#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helpers decorators"""

# standard libs
from typing import Callable, Optional, Union

# Domoticz lib
import Domoticz

# local libs
# from helpers.common import debug


def _action_log(action: str, text: str) -> None:
    """Résout l'action à réaliser avec domoticz

    [args]:
        - action (str): Possible values[`log`, `error`,`debug`, `status`]; default to `log`
        - text (str): the text to log
    """
    if action == 'debug':
        Domoticz.Debug("Debug: " + text)
    elif action == 'status':
        Domoticz.Status(text)
    elif action == 'error':
        Domoticz.Error(text)
    else:
        Domoticz.Log(text)


def log_func(
        action: str = 'log',
        log_args: bool = False,
        separator_line: bool = False,
        callback: Optional[Union[Callable, str]] = None,
        log_return: bool = False) -> Callable:
    # pylint:disable=line-too-long
    """log function decorator

    [args]:
        - action (str): Possible values[`log`, `error`,`debug`, `status`]; default to `log`
        - log_args (bool): if `True`, add additionnal lines with `args` and `kwargs` representation
        - separator_line (bool): If `True`, add an additionnal empty line before messages

    [special]:
        - use `#ignore_self_arg` in function docstring if you want to ignore the self arg of class method
        - use `str` in callback arg to invoke __str__() or __repr__() class method, else callback()
    """
    # pylint:enable=line-too-long

    def decorator(func: Callable) -> Callable:
        """decorator function"""

        def inner(*args: tuple, **kwargs: dict) -> Callable:
            """inner function"""
            if separator_line:
                _action_log(action, "")
            if isinstance(func.__doc__, str):
                has_ignore_self_arg = "#ignore_self_arg" in func.__doc__
                message_ext = ' - ' + (func.__doc__.splitlines())[0]
            else:
                has_ignore_self_arg = False
                message_ext = ''
            _action_log(
                action,
                f"{func.__module__}.{func.__name__}{message_ext}"
            )
            if log_args:
                if args:
                    list_args = list(args)
                    if has_ignore_self_arg:
                        list_args.pop(0)
                    formated_args = []
                    for arg in list_args:
                        type_arg = type(arg)
                        if isinstance(arg, Domoticz.Device):
                            arg = arg.Name
                        formated_args.append(
                            {
                                'type': type_arg,
                                'value': repr(arg)
                            }
                        )
                    _action_log(action, f"args={formated_args}")
                if kwargs:
                    formated_kwargs = [
                        {
                            'name': key,
                            'type': type(value),
                            'value': repr(value)
                        } for key, value in kwargs.items()
                    ]
                    _action_log(action, f"kwargs={formated_kwargs}")

            # call __str__ method
            if callback == "str":
                _action_log(action, args[0])
            elif callable(callback):
                callback()

            ret = func(*args, **kwargs)
            # log return
            if log_return:
                _action_log(action, f"Return: {ret}")
            return ret

        return inner

    return decorator


def replace_unit_id_by_device(devices: dict) -> Callable:
    """Search device from unit_id

    [args]:
        - unit_id (int): the unit id transmit by Domoticz

    [exception]:
        - raise KeyError if unit_id is not found in Domoticz.Devices

    [return]:
        - Domoticz device if found or None
    """
    def decorator(func: Callable) -> Callable:
        """"""

        def inner(*args: tuple) -> Callable:
            """inner function"""
            list_args = list(args)
            if list_args:
                unit_id = list_args.pop(0)
                if unit_id in devices:
                    device = devices.get(unit_id)
                    list_args.insert(0, device)
                else:
                    raise KeyError(f"Unknown unit({unit_id}) in plugin")
            return func(*list_args)

        return inner

    return decorator
