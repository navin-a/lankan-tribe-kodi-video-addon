__author__ = 'Navin'

import unittest
from channel import ITN
from channel import Rupavahini


class TestITN(unittest.TestCase):
    def setUp(self):
        self.channel = ITN()

    def testGetSource(self):
        source = self.channel.getSource("/")
        self.assertIsNotNone(source)
        self.assertGreater(source, 0, "ITN Home page source not available")
        self.assertTrue(len(self.channel.getSource("/")) > 10000, "ITN home page source length is too short")

    def testGetCategories(self):
        self.assertEquals(self.channel.getCategories(), ('Drama', 'Entertainment'))

    def testGetProgrammesForDramaCategory(self):
        programmes = self.channel.getProgrammes('Drama')
        self.assertIsNotNone(programmes)
        noOfProgrammes = 0
        for prg in programmes:
            self.assertIsInstance(prg, tuple, "Does not return the expected data structure (tuple)")
            self.assertTrue(len(prg) == 2, "Does not provide the expected details of the programme")
            self.assertIsNotNone(prg[0])
            self.assertIsNotNone(prg[1])
            noOfProgrammes += 1
        self.assertGreater(noOfProgrammes, 5, "Number of programmes found is too low. Could be an error")
        self.assertLess(noOfProgrammes, 40, "Number of programmes found is too high. Could be an error")

    def testGetEpisodesForDrama(self):
        programmes = self.channel.getProgrammes("Drama")
        programme = programmes.next()
        episodes = self.channel.getEpisodes(programme[1])
        noOfEpisodes = 0
        for episode in episodes:
            self.assertIsInstance(episode, tuple, "Does not return the expected data structure (tuple)")
            self.assertTrue(len(episode) == 3, "Does not provide the expected details of the episode")
            self.assertIsNotNone(episode[0])
            self.assertIsNotNone(episode[1])
            self.assertIsNotNone(episode[2])
            noOfEpisodes += 1
        self.assertGreater(noOfEpisodes, 0, "Episodes for programme " + programme[1] + " not found")
        self.assertLess(noOfEpisodes, 14, "Too many episodes found. Could be an error")

    def testGetProgrammesForEntertainmentCategory(self):
        programmes = self.channel.getProgrammes('Entertainment')
        self.assertIsNotNone(programmes)
        noOfProgrammes = 0
        for prg in programmes:
            self.assertIsInstance(prg, tuple, "Does not return the expected data structure (tuple)")
            self.assertTrue(len(prg) == 2, "Does not provide the expected details of the programme")
            self.assertIsNotNone(prg[0])
            self.assertIsNotNone(prg[1])
            noOfProgrammes += 1
        self.assertGreater(noOfProgrammes, 5, "Number of programmes found is too low. Could be an error")
        self.assertLess(noOfProgrammes, 40, "Number of programmes found is too high. Could be an error")


class TestRupavahini(unittest.TestCase):
    def setUp(self):
        self.channel = Rupavahini()

    def testGetSource(self):
        source = self.channel.getSource("/")
        self.assertIsNotNone(source)
        self.assertGreater(source, 0, "Rupavahini Home page source not available")
        self.assertTrue(len(source) > 10000, "Rupavahini home page source length is too short")

    def testGetCategories(self):
        self.assertEquals(self.channel.getCategories(), ('Drama', 'News'))

    def testGetProgrammesForDramaCategory(self):
        programmes = self.channel.getProgrammes('Drama')
        self.assertIsNotNone(programmes)
        noOfProgrammes = 0
        for prg in programmes:
            self.assertIsInstance(prg, tuple, "Does not return the expected data structure (tuple)")
            self.assertTrue(len(prg) == 2, "Does not provide the expected details of the programme")
            self.assertIsNotNone(prg[0])
            self.assertIsNotNone(prg[1])
            noOfProgrammes += 1
        self.assertGreater(noOfProgrammes, 5, "Number of programmes found is too low. Could be an error")
        self.assertLess(noOfProgrammes, 40, "Number of programmes found is too high. Could be an error")

    def testGetEpisodesForDrama(self):
        programmes = self.channel.getProgrammes('Drama')
        programme = programmes.next()
        episodes = self.channel.getEpisodes(programme[1])
        noOfEpisodes = 0
        for episode in episodes:
            self.assertIsInstance(episode, tuple, "Does not return the expected data structure (tuple)")
            self.assertTrue(len(episode) == 3, "Does not provide the expected details of the episode")
            self.assertIsNotNone(episode[0])
            self.assertIsNotNone(episode[1])
            self.assertIsNotNone(episode[2])
            noOfEpisodes += 1
        self.assertGreater(noOfEpisodes, 0, "Episodes for programme " + programme[1] + " not found")
        self.assertLess(noOfEpisodes, 21, "Too many episodes found. Could be an error")

    def testGetProgrammesForNewsCategory(self):
        programmes = self.channel.getProgrammes('News')
        self.assertIsNotNone(programmes)
        noOfProgrammes = 0
        for prg in programmes:
            self.assertIsInstance(prg, tuple, "Does not return the expected data structure (tuple)")
            self.assertTrue(len(prg) == 2, "Does not provide the expected details of the programme")
            self.assertIsNotNone(prg[0])
            self.assertIsNotNone(prg[1])
            noOfProgrammes += 1
        self.assertGreater(noOfProgrammes, 2, "Number of programmes found is too low. Could be an error")
        self.assertLess(noOfProgrammes, 40, "Number of programmes found is too high. Could be an error")


if __name__ == '__main__':
    unittest.main()

