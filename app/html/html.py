# -*- coding: UTF-8 -*-
"""HTML page"""

# standard libs
from __future__ import annotations

import os
import shutil

# plugin libs
from domoticz.parameters import PluginParameters
import helpers

HTML_NAME = 'ZW164_py_plugin'
HTML_SOUCRE = f'./plugins/{HTML_NAME}/app/html/index.html'
HTML_DEST = f'./www/templates/{HTML_NAME}.html'


class HtmlPage:
    """The Html page"""
    parameters: PluginParameters
    src_path: str
    dst_path: str

    def on_start(self: HtmlPage, parameters: PluginParameters) -> None:
        """onStart event"""
        self.parameters = parameters
        self.src_path = os.path.join(
            self.parameters.HomeFolder, 'app/html/files'
        )
        #create index.html with your plugin name
        shutil.move(
            os.path.join(self.src_path, 'index.html'),
            os.path.join(self.src_path, self.parameters.Name + '.html')
        )
        self.dst_path = os.path.join(
            self.parameters.HomeFolder, 'www/templates'
        )
        self.__install()

    def on_stop(self: HtmlPage) -> None:
        """onStop event"""
        self.__uninstall()

    def __install(self: HtmlPage) -> None:
        """installation des fichiers"""
        # copy2(HTML_SOUCRE, HTML_DEST)
        shutil.copytree(self.src_path, self.dst_path)

    def __uninstall(self: HtmlPage) -> None:
        """suppression des fichiers"""
