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
from sets import Set
import YDStreamExtractor


def getChannels():
    return {'Derana', 'ITN', 'Rupavahini', 'Swarnavahini'}


class Channel(object):
    def __init__(self, url):
        self.channelUrl = url

    def getSource(self, relativePath):
        content_url = self.channelUrl + relativePath
        # print "content_url="+content_url
        source = urllib2.urlopen(content_url).read()
        return source.replace('\n', ' ').replace('\r', ' ')

    def removeComments(self, source):
        return re.sub('<!--(.*?)-->', '', source, flags=re.DOTALL)


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
        # print "category path=" + category_path
        source = super(ITN, self).getSource(category_path)
        # print source
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


class Derana(Channel):
    def __init__(self):
        super(Derana, self).__init__("http://www.derana.lk")
        self.categories = {'Music': "/", 'Talk Shows': "/", 'Magazine & Variety': "/", 'Reality Shows': "/"}
        self.textRepresentation = {"Music": "Music", "Talk Shows": "Talk Shows",
                                   "Magazine & Variety": "Magazine &amp; Variety", "Reality Shows": "Reality Shows"}

    def getCategories(self):
        return tuple(self.categories.keys())

    def getProgrammes(self, category):
        category_path = self.categories[category]
        source = super(Derana, self).getSource(category_path)
        regex_block = re.compile(
            r"<div class=\"header\">\s*<ul>\s*<li>" + self.textRepresentation[
                category] + "</li>\s*</ul>" + "(.+?)</li>\s*</ul>\s*</div>",
            re.DOTALL)
        htmlFragments = regex_block.findall(source)
        # remove commented blocks
        htmlFragments[0] = super(Derana, self).removeComments(htmlFragments[0])
        # print "getProgrammes: html fragment with comments stripped off= " + htmlFragments[0]
        regex = re.compile(
            r",\'http://www.derana.lk(?P<programme_path>[- a-zA-Z0-9/]+?)\'(.+?)<h2>(?P<programme_name>.+?)</h2>\s*<p>",
            re.DOTALL)
        programmeItr = regex.finditer(htmlFragments[0])
        uniqueProgrammes = Set()
        for programmeDetails in programmeItr:
            programme = (programmeDetails.group('programme_name'), programmeDetails.group('programme_path') )
            uniqueProgrammes.add(programme)
        for programme in uniqueProgrammes:
            yield programme


    def getEpisodes(self, programPagePath):
        regex_block = re.compile(
            r"<div class=\"header\">\s*<ul>\s*<li>" + "Video Gallery" + "</li>\s*</ul>" + "(.+?)</a>\s*</div>\s*</div>\s*</div>\s*<div class=\"clearfix\"",
            re.DOTALL)
        regex = re.compile(
            r",\'http://www.derana.lk(?P<episode_path>[- a-zA-Z0-9/&=]+?)'\);\">"
            # r"(.+?)"
            r"\s*"
            r"<img\s*src=\"(?P<img_url>http://derana.lk/[- a-zA-Z0-9\_/.]+)\""
            r"(.+?)"
            r"\s*<p>(?P<title>[- a-zA-Z0-9|]+)</p>"
            , re.DOTALL)
        source = super(Derana, self).getSource(programPagePath)
        # print "before removing comments= "+source
        # remove commented blocks
        source = super(Derana, self).removeComments(source)
        # print "comments removed= "+source
        htmlFragments = regex_block.findall(source)
        # print htmlFragments
        episodes = regex.finditer(htmlFragments[0])
        for episodeDetails in episodes:
            imgUrl = episodeDetails.group('img_url').replace(" ", "%20")
            # print "episode Details=" + episodeDetails.group(
            #     'episode_path') + " image url=" + imgUrl + " title=" + episodeDetails.group('title')
            episode = (episodeDetails.group('title').replace("&#8211;", "-"), episodeDetails.group('episode_path'),
                       imgUrl)
            yield episode


    def getVideo(self, episodePagePath):
        videoUrlRegex = re.compile(
            r"\s{2}<iframe (?:.+?)\s+src=\"(?P<video_page>http://www.youtube.com[-_a-zA-Z0-9\/]+)?")
        videoPageSource = super(Derana, self).getSource(episodePagePath)
        # print "video page source="+videoPageSource
        YDStreamExtractor.disableDASHVideo(True)
        video_urls = videoUrlRegex.findall(videoPageSource)
        url = video_urls[0]
        vid = YDStreamExtractor.getVideoInfo(url, quality=1)
        return vid.streamURL()


class Swarnavahini(Channel):
    def __init__(self):
        super(Swarnavahini, self).__init__("http://www.swarnavahini.lk")
        self.categories = {'News': 0, 'Teledrama': 1, 'Entertainment': 2, 'Political': 3}
        self.textRepresentation = {"Music": "Music", "Talk Shows": "Talk Shows",
                                   "Magazine & Variety": "Magazine &amp; Variety", "Reality Shows": "Reality Shows"}

    def getCategories(self):
        return tuple(self.categories.keys())

    def getProgrammes(self, category):
        category_index = self.categories[category]
        source = super(Swarnavahini, self).getSource("/")
        regex_block = re.compile('<ul class=\"dropdown-menu\">(.+?)</ul>', re.DOTALL)
        htmlFragments = regex_block.findall(source)
        # print "getProgrammes: html fragment with comments stripped off= " + htmlFragments[0]
        regex = re.compile(
            r'\"http://www.swarnavahini.lk(?P<programme_path>[- a-zA-Z0-9/]+?)\">(?P<programme_name>.+?)</a></li>',
            re.DOTALL)
        programmeItr = regex.finditer(htmlFragments[category_index])
        uniqueProgrammes = Set()
        for programmeDetails in programmeItr:
            programme = (programmeDetails.group('programme_name'), programmeDetails.group('programme_path') )
            uniqueProgrammes.add(programme)
        for programme in uniqueProgrammes:
            yield programme


    def getEpisodes(self, programPagePath):
        regex = re.compile(r"<div class=\"col-sm-3 col-xs-6 item post\">(?:.+?)src=\""
                           r"(?P<img_url>http://[-a-zA-Z0-9/\.]+jpg)(?:.+?)<h3>"
                           r"<a href=\"http://www.swarnavahini.lk(?P<episode_path>[-a-zA-Z0-9/%]+)\">(?P<title>.+?)</a></h3>", re.DOTALL)
        source = super(Swarnavahini, self).getSource(programPagePath)
        # print "before removing comments= "+source
        # remove commented blocks
        source = super(Swarnavahini, self).removeComments(source)
        # print "comments removed= "+source
        episodes = regex.finditer(source)
        for episodeDetails in episodes:
            imgUrl = episodeDetails.group('img_url').replace(" ", "%20")
            title = episodeDetails.group('title')
            separator_index= title.find('|')
            if separator_index > 0:
                title = title[:separator_index]
            title =  re.sub(r"&#[0-9]{4};","",title)
            # title = re.sub(r"&#[0-9]{4};","",episodeDetails.group('title').decode('unicode_escape').encode('ascii','ignore'))
            # print "episode Details=" + episodeDetails.group('episode_path') + " image url=" + imgUrl + " title=" + title
            episode = (title, episodeDetails.group('episode_path'),
                       imgUrl)
            yield episode


    def getVideo(self, episodePagePath):
        videoUrlRegex = re.compile(
            r"<iframe (?:.+?)\s+src=\"(?P<video_page>https*://www.youtube.com[-_a-zA-Z0-9\/]+)?")
        videoPageSource = super(Swarnavahini, self).getSource(episodePagePath)
        # print "video page source="+videoPageSource
        YDStreamExtractor.disableDASHVideo(True)
        video_urls = videoUrlRegex.findall(videoPageSource)
        url = video_urls[0]
        vid = YDStreamExtractor.getVideoInfo(url, quality=1)
        return vid.streamURL()
