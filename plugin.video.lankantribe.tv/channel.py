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

import re
import urllib2


def getChannels():
    return {'ITN', 'Rupavahini'}


class Channel(object):
    def __init__(self, url):
        self.channelUrl = url

    def getSource(self, relativePath):
        content_url = self.channelUrl + relativePath
        source = urllib2.urlopen(content_url).read()
        return source.replace('\n', ' ').replace('\r', ' ')


class Rupavahini(Channel):
    def __init__(self):
        super(Rupavahini, self).__init__("http://www.rupavahini.lk")
        self.categories = {"Drama": "Teledrama", "News": "News"}

    def getCategories(self):
        return tuple(self.categories.keys())

    def getProgrammes(self, category):
        selectedCategory = self.categories[category]
        homePageContent = super(Rupavahini, self).getSource("")
        categoryBlockRegex = re.compile(
            "<span>" + selectedCategory + "</span>(.+?)<span class=\"separator level1 parent\">",
            re.DOTALL)
        categoryBlock = categoryBlockRegex.findall(homePageContent)
        programmesRegex = re.compile(
            "<a href=\"(?P<programme_path>[-a-zA-Z./]+)\" class=\"level2\"><span>(?P<programme_name>[ a-zA-Z]+)</span>")
        programmes = programmesRegex.finditer(categoryBlock[0])
        for programmeDetails in programmes:
            programme = ( programmeDetails.group('programme_name'), programmeDetails.group('programme_path'))
            yield programme

    def getEpisodes(self, programPagePath):
        source = super(Rupavahini, self).getSource(programPagePath)
        episodesRegex = re.compile(
            "<a href=\"(?P<path>[-_a-zA-Z0-9/.]+?)\"><img src=\"(?P<img>[- _a-zA-Z0-9/.]+?)\" (?:.+?)title=\"(?P<episode_name>[- _a-zA-Z0-9]+)\"",
            re.DOTALL)
        episodes = episodesRegex.finditer(source)
        for episodeDetails in episodes:
            episode = (episodeDetails.group('episode_name'), episodeDetails.group('path'),
                       self.channelUrl + episodeDetails.group('img'))
            yield episode

    def getVideo(self, episodePagePath):
        videoUrlRegex = re.compile("<div align=\"center\">(?:.+?)<iframe src=\"(?P<video>.+?)\" frameborder", re.DOTALL)
        videoPageSource = super(Rupavahini, self).getSource(episodePagePath)
        video_urls = videoUrlRegex.findall(videoPageSource)
        source = urllib2.urlopen(video_urls[0]).read()
        playListRegex = re.compile("file: \"(?P<video>http://[-_a-zA-Z0-9./]+.m3u8)\"")
        video = playListRegex.findall(source)
        return video[0]


class ITN(Channel):
    def __init__(self):
        super(ITN, self).__init__("http://www.itn.lk")
        self.categories = {"Drama": "/category/current-dramas", "Entertainment": "/category/entertainment"}

    def getCategories(self):
        return tuple(self.categories.keys())

    def getProgrammes(self, category):
        category_path = self.categories[category]
        source = super(ITN, self).getSource(category_path)
        regex = re.compile(
            r"href=\"http://www.itn.lk(?P<programme_path>" + category_path + "/[-a-zA-Z]+?/)\"\s*>(?P<programme_name>[- a-zA-Z]+?)</a>")
        programmeItr = regex.finditer(source)
        for programmeDetails in programmeItr:
            programme = (programmeDetails.group('programme_name'), programmeDetails.group('programme_path') )
            yield programme


    def getEpisodes(self, programPagePath):
        regex_block = re.compile(r"<div class=\"nag cf\">(.+?)<div id=\"sidebar\" ", re.DOTALL)
        regex = re.compile(
            r"<a class=\"clip-link\" data-id=\"[0-9]+\" title=\"(?P<title>.+?)\" href=\"http://www.itn.lk(?P<episode_path>/[-a-zA-Z0-9/]+)\">"
            r"(?:.+?)"
            r"<img src=\"(?P<img_url>http://www.itn.lk/[-a-zA-Z0-9_/.]+)\"", re.DOTALL)
        source = super(ITN, self).getSource(programPagePath)
        htmlFragments = regex_block.findall(source)
        episodes = regex.finditer(htmlFragments[0])
        for episodeDetails in episodes:
            episode = (episodeDetails.group('title').replace("&#8211;", "-"), episodeDetails.group('episode_path'),
                       episodeDetails.group('img_url'))
            yield episode


    def getVideo(self, episodePagePath):
        videoUrlRegex = re.compile(r"</span><a href=\"(?P<video_page>http://[-_a-zA-Z0-9/.]+)\">")
        videoPageSource = super(ITN, self).getSource(episodePagePath)
        video_urls = videoUrlRegex.findall(videoPageSource)
        return video_urls[0]
