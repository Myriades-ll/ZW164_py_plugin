# -*- coding: UTF-8 -*-
"""HTML page"""

# standard libs
from __future__ import annotations
from shutil import copy2
import os

HTML_NAME = 'ZW164_py_plugin'
HTML_SOUCRE = f'./plugins/{HTML_NAME}/app/html/index.html'
HTML_DEST = f'./www/templates/{HTML_NAME}.html'


class HtmlPage:
    """The Html page"""

    def on_start(self: HtmlPage) -> None:
        """onStart event"""
        copy2(HTML_SOUCRE, HTML_DEST)

    def on_stop(self: HtmlPage) -> None:
        """onStop event"""
        if os.path.exists(HTML_DEST):
            os.remove(HTML_DEST)
