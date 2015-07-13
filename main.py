#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Copyright (C) 2014  Navin Ariyaratna (navinnda@yahoo.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Navin'

import sys
import urlparse
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import channel


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'videos')
mode = args.get('mode', None)


def addDirectory(folderName, url, thumbnailImage=None, isFolder=True, iconImage='DefaultFolder.png',
                 handle=addon_handle):
    if thumbnailImage is None:
        li = xbmcgui.ListItem(folderName, iconImage)
    else:
        li = xbmcgui.ListItem(folderName, iconImage, thumbnailImage=thumbnailImage)
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=isFolder)


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)
    # xbmc.executebuiltin('Notification(%s, %s)'%(channelName, element))


def displayProgramme(channelName, mode, elements, folderNameIndex=1, directoryNameIndex=0):
    for element in elements:
        url = build_url({'mode': mode, 'foldername': element[folderNameIndex], 'channel': channelName})
        addDirectory(element[directoryNameIndex], url)
    xbmcplugin.endOfDirectory(addon_handle)


def displayCategory(channelName, mode, elements):
    for element in elements:
        url = build_url({'mode': mode, 'foldername': element, 'channel': channelName})
        addDirectory(element, url)
    xbmcplugin.endOfDirectory(addon_handle)


def displayVideo(channelName, mode, elements, folderNameIndex=1, directoryNameIndex=0, thumbnailImgIndex=2):
    for element in elements:
        url = build_url({'mode': mode, 'foldername': element[folderNameIndex], 'channel': channelName})
        addDirectory(element[directoryNameIndex], url, element[thumbnailImgIndex])
    xbmcplugin.endOfDirectory(addon_handle)


def getChannelInstance(channelName):
    channelObj = getattr(channel, channelName)()
    return channelObj


if mode is None:
    for channelName in channel.getChannels():
        url = build_url({'mode': 'categories', 'foldername': channelName, 'channel': channelName})
        addDirectory(folderName=channelName, url=url, handle=addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)
else:
    channelName = args.get('channel')[0]
    channelObj = getChannelInstance(channelName)
    selection = args.get('foldername')[0]
    if mode[0] == 'categories':
        categories = channelObj.getCategories()
        displayCategory(channelName, 'programmes', categories)
    elif mode[0] == 'programmes':
        programmes = channelObj.getProgrammes(selection)
        displayProgramme(channelName, 'episodes', programmes)
    elif mode[0] == 'episodes':
        episodes = channelObj.getEpisodes(selection)
        displayVideo(channelName, 'playVideo', episodes)
    elif mode[0] == 'playVideo':
        video = channelObj.getVideo(selection)
        if xbmc.Player().isPlayingVideo() == False:
            xbmc.Player().play(video)
