# -*- coding: utf-8 -*-
"""
    Generic utils for Kodi addons
    Copyright (C) 2019 Mr Dini

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>
"""
from traceback import format_exc
from base64 import b64decode
from random import choice
from urllib import urlencode
from urllib2 import quote
import requests
import xbmc
import xbmcgui
import xbmcplugin


def request_page(url, **kwargs):
    # type: (str, *, str, dict, dict, dict, dict, dict, bool)
    """
    Basic request routine, supports GET and POST requests.
    If the `data` keyword argument is present, defaults to POST, otherwise GET request.
    """
    user_agent = kwargs.get("user_agent", random_uagent())
    params = kwargs.get("params")
    headers = kwargs.get("headers", {})
    additional_headers = kwargs.get("additional_headers", {})
    cookies = kwargs.get("cookies")
    data = kwargs.get("data")
    allow_redirects = kwargs.get("allow_redirects")

    headers.update({"User-Agent": user_agent})
    headers.update(additional_headers)

    if not data:
        response = requests.get(url, params=params, headers=headers, cookies=cookies, allow_redirects=allow_redirects)
    else:
        response = requests.post(url, params=params, data=data, headers=headers, cookies=cookies, allow_redirects=allow_redirects)

    return response


def random_uagent():
    # type: None -> str
    return choice(
        [
            # PC - Chrome
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            # PC - Firefox
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:59.0) Gecko/20100101 Firefox/59.0",
            "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        ]
    )


def decrypt_string(_input):
    # type: (str)
    return b64decode(_input[6:])[7:]


def add_item(plugin_prefix, handle, name, action, is_directory, **kwargs):
    url = "%s?action=%s&name=%s" % (plugin_prefix, action, quote(name))
    item = xbmcgui.ListItem(name)
    info_labels = {}
    if kwargs.get("description"):
        url += "&descr=%s" % (quote(kwargs["description"]))
        info_labels.update({"plot": kwargs["description"]})
    arts = {}
    if kwargs.get("icon"):
        url += "&icon=%s" % (quote(kwargs["icon"]))
        arts.update({"thumb": kwargs["icon"], "icon": kwargs["icon"]})
    if kwargs.get("fanart"):
        url += "&fanart=%s" % (quote(kwargs["fanart"]))
        arts.update({"fanart": kwargs["fanart"]})
        item.setProperty("Fanart_Image", kwargs["fanart"])
    if kwargs.get("type"):
        info_labels.update({"mediatype": kwargs["type"]})
    if kwargs.get("id"):
        url += "&id=%s" % (kwargs["id"])
    if kwargs.get("extra"):
        url += "&extra=%s" % (kwargs["extra"])
    if kwargs.get("is_livestream"):
        # see https://forum.kodi.tv/showthread.php?pid=2743328#pid2743328 to understand this hack
        # useful for livestreams to not to mark the item as watched + adds switch to channel context menu item
        # NOTE: MUST BE THE LAST PARAMETER in the URL
        url += "&pvr=.pvr"
    item.setArt(arts)
    item.setInfo(type="Video", infoLabels=info_labels)
    try:
        item.setContentLookup(False)
    except:
        pass  # if it's a local dir, no need for it
    if kwargs.get("refresh"):
        item.addContextMenuItems([("Frissítés", "XBMC.Container.Refresh()")])
    xbmcplugin.addDirectoryItem(int(handle), url, item, is_directory)


def play(handle, url, _type, **kwargs):
    name = kwargs.get("name")
    icon = kwargs.get("icon")
    description = kwargs.get("description")
    user_agent = kwargs.get("user_agent", random_uagent())
    url = "%s|User-Agent=%s" % (url, quote(user_agent))

    item = xbmcgui.ListItem(label=name, thumbnailImage=icon)
    item.setInfo(type=_type, infoLabels={"Title": name, "Plot": description})
    xbmc.Player().play(url, item)


class Error(Exception):
    def __init__(self, e):
        xbmc.log(format_exc(e), xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Hiba", "További infók a logban.", xbmcgui.NOTIFICATION_ERROR, 5000
        )


class Utils:
    def __init__(self, addon):
        self.addon = addon
        self.addon_name = addon.getAddonInfo("name")
        self.icon = addon.getAddonInfo("icon")
        self.fanart = addon.getAddonInfo("fanart")
        self.version = addon.getAddonInfo("version")

    def create_notification(self, description, **kwargs):
        # type: (str, *, str, int, str) -> None
        title = kwargs.get("title", self.addon_name)
        length = kwargs.get("length", 5000)
        icon = kwargs.get("icon", self.icon)
        # xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (title, description, length, icon))
        xbmcgui.Dialog().notification(title, description, icon, length)

    def create_ok_dialog(self, text, **kwargs):
        # type: (str, *, str) -> None
        title = kwargs.get("title", self.addon_name)
        xbmcgui.Dialog().ok(title, text.replace("\n", "[CR]"))

    def create_textbox(self, text, **kwargs):
        # type: (str, *, str) -> None
        title = kwargs.get("title", self.addon_name)
        xbmcgui.Dialog().textviewer(title, text.replace("\n", "[CR]"))

    def create_yesno_dialog(self, text, **kwargs):
        title = kwargs.get("title", self.addon_name)
        no = kwargs.get("no", "Nem")
        yes = kwargs.get("yes", "Igen")

        if not kwargs.get("time_to_close"):
            ret = xbmcgui.Dialog().yesno(title, text, nolabel=no, yeslabel=yes)
        else:
            ret = xbmcgui.Dialog().yesno(
                title, text, nolabel=no, yeslabel=yes, autoclose=kwargs["time_to_close"]
            )
        return ret

    def open_settings(self):
        # type: (None) -> None
        self.addon.openSettings()

    def get_setting(self, setting_key):
        # type: (str) -> Union[str, None]
        return self.addon.getSetting(setting_key) or None

    def set_setting(self, setting_key, value):
        # type: (str, str)
        self.addon.setSetting(setting_key, value)
