# -*- coding: UTF-8 -*-
"""HTML page"""

# standard libs
from __future__ import annotations

import os
from shutil import copy2

# plugin libs
from domoticz.parameters import PluginParameters
import helpers

HTML_NAME = 'ZW164_py_plugin'
HTML_SOUCRE = f'./plugins/{HTML_NAME}/app/html/index.html'
HTML_DEST = f'./www/templates/{HTML_NAME}.html'


class HtmlPage:
    """The Html page"""
    parameters: PluginParameters

    def on_start(self: HtmlPage, parameters: PluginParameters) -> None:
        """onStart event"""
        self.parameters = parameters
        self.__install()

    def on_stop(self: HtmlPage) -> None:
        """onStop event"""
        self.__uninstall()

    def __install(self: HtmlPage) -> None:
        """installation des fichiers"""
        # copy2(HTML_SOUCRE, HTML_DEST)
        src_path = os.path.join(self.parameters.HomeFolder, 'app/html/files')
        helpers.debug(src_path)
        # for root, dirs, files in os.walk(top)

    def __uninstall(self: HtmlPage) -> None:
        """suppression des fichiers"""
