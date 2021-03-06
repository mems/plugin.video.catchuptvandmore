# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Original work (C) JUL1EN094, SPM, SylvainCecchetto
    Copyright (C) 2016  SylvainCecchetto

    This file is part of Catch-up TV & More.

    Catch-up TV & More is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Catch-up TV & More is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with Catch-up TV & More; if not, write to the Free Software Foundation,
    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import os
import imp
import time
import requests
from random import randint
from resources.lib import common

# Useful path
cache_path = common.sp.xbmc.translatePath(
    os.path.join(
        'special://profile/addon_data',
        common.ADDON.id,
        'cache'
    )
)

cache_path = cache_path.decode(
    "utf-8").encode(common.FILESYSTEM_CODING)

default_ua = "Mozilla/5.0 (X11; Linux x86_64) " \
             "AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/60.0.3112.78 Safari/537.36"

user_agents = [
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14'
    ' (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
    'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14'
    ' (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/55.0.2883.87 Safari/537.36'
]


def get_random_ua_hdr():
    ua = user_agents[randint(0, len(user_agents) - 1)]
    return {
        'User-Agent': ua
    }


def download_catalog(
        url,
        file_name,
        force_dl=False,
        request_type='get',
        post_dic={},
        random_ua=False,
        specific_headers={},
        params={}):
    file_name = format_filename(file_name)
    common.ADDON.log('URL download_catalog : ' + url)

    if not os.path.exists(cache_path):
        os.makedirs(cache_path, mode=0777)
    file_path = os.path.join(cache_path, file_name)

    if os.path.exists(file_path):
        mtime = os.stat(file_path).st_mtime
        dl_file = (time.time() - mtime > 60)
    else:
        dl_file = True
    if dl_file or force_dl:
        if random_ua:
            ua = user_agents[randint(0, len(user_agents) - 1)]
        else:
            ua = default_ua

        if specific_headers:
            headers = specific_headers
            if 'User-Agent' not in headers:
                headers['User-Agent'] = ua
        else:
            headers = {'User-Agent': ua}

        if request_type == 'get':
            r = requests.get(url, headers=headers, params=params)

        elif request_type == 'post':
            r = requests.post(
                url, headers=headers, data=post_dic, params=params)

        with open(file_path, 'wb') as f:
            f.write(r.content)

    return file_path


def format_filename(filename):
    keepcharacters = ('_', '.')
    return "".join(
        c for c in filename if c.isalnum() or c in keepcharacters).rstrip()


def get_webcontent(
        url,
        request_type='get',
        post_dic={},
        random_ua=False,
        specific_headers={},
        params={}):
    common.ADDON.log('URL get_webcontent : ' + url)
    if random_ua:
            ua = user_agents[randint(0, len(user_agents) - 1)]
    else:
        ua = default_ua

    if specific_headers:
        headers = specific_headers
        if 'User-Agent' not in headers:
            headers['User-Agent'] = ua
    else:
        headers = {'User-Agent': ua}

    if request_type == 'get':
        r = requests.get(url, headers=headers, params=params)

    elif request_type == 'post':
        r = requests.post(url, headers=headers, data=post_dic, params=params)

    return r.content


def get_redirected_url(
        url,
        random_ua=False,
        specific_headers={}):
    if random_ua:
            ua = user_agents[randint(0, len(user_agents) - 1)]
    else:
        ua = default_ua

    if specific_headers:
        headers = specific_headers
        if 'User-Agent' not in headers:
            headers['User-Agent'] = ua
    else:
        headers = {'User-Agent': ua}

    r = requests.head(url, allow_redirects=True, headers=headers)
    return r.url


def send_notification(
        message, title=common.PLUGIN_NAME, time=5000, sound=True):
    common.sp.xbmcgui.Dialog().notification(
        title, message, common.ADDON.icon, time)


def clear_cache():
    for file in os.listdir(cache_path):
        file_path = os.path.join(cache_path, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)
    send_notification(common.GETTEXT('Cache cleared'))


def vpn_context_menu_item():
    vpn_label = common.GETTEXT('Connect VPN')
    storage = common.sp.MemStorage('vpn')
    if 'status' in storage:
        if storage['status'] == "connected":
            vpn_label = common.GETTEXT('Disconnect VPN')
    else:
        storage['status'] = "disconnected"
    vpn = (
        vpn_label,
        'XBMC.RunPlugin(' + common.PLUGIN.get_url(
            action='vpn_entry') + ')'
    )
    return vpn


def get_module(params):
    """
    get_module allows us to load the desired python file
    """
    module_name = eval(params.module_path)[-1]

    module_path = common.sp.xbmc.translatePath(
        common.sp.os.path.join(
            common.LIB_PATH,
            *(eval(params.module_path))
        )
    )
    module_filepath = module_path + ".py"
    module_filepath = module_filepath.decode(
        "utf-8").encode(common.FILESYSTEM_CODING)

    return imp.load_source(
        module_name,
        module_filepath
    )
