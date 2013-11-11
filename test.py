#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Yoann Sculo <yoann.sculo@gmail.com>',
    'Bruno Adelé <bruno@adele.im>',
]
__copyright__ = 'Copyright (C) 2013 Yoann Sculo'
__license__ = 'GPLv2'
__version__ = '1.0'

import os
import unittest
import utilities
from config import configstest as configs

import jobcatcher


class TestPackages(unittest.TestCase):

    def cleanDatas(self, jobboardname):
        """Clean jobboard datas"""
        rootdir = configs['global']['rootdir']
        feedsdir = '%s/%s/feeds' % (rootdir, jobboardname)
        pagesdir = '%s/%s/pages' % (rootdir, jobboardname)

        # remove feeds & pages
        utilities.removeFiles(feedsdir, '*.feed')
        utilities.removeFiles(pagesdir, '*.page')

    def setUp(self):
        """Test & Create database"""
        # Remove exist database
        if os.path.isfile(configs['global']['database']):
            os.remove(configs['global']['database'])

        # Check if database not exist
        exists = utilities.db_istableexists(configs, 'offers')
        self.assertEqual(exists, False)

        # Create database & check
        utilities.db_create(configs)
        exists = utilities.db_istableexists(configs, 'offers')
        self.assertEqual(exists, True)

    def test_JBEures(self):
        """ Test Eures jobboard"""

        # Jobboardname
        jobboard = 'Eures'

        # Clean datas
        self.cleanDatas(jobboard)

        # Get feed content
        plugin = utilities.loadJobBoard(jobboard, configs)
        url = configs[jobboard]['feeds'][0]
        filename = plugin.downloadFeed(url)
        self.assertEqual(
            filename,
            '/tmp/dl/Eures/feeds/0855c939d3b5b5cd1fffeb1665dcecfc.feed'
        )

        # Dowload page
        urls = plugin.getUrls()
        self.assertEqual(len(urls), 5)
        plugin.downloadPages(urls)

    def test_JBApec(self):
        """ Test Apec jobboard"""

        # Jobboardname
        jobboard = 'Apec'

        # Clean datas
        self.cleanDatas(jobboard)

        # Get feed content
        plugin = utilities.loadJobBoard(jobboard, configs)
        url = configs[jobboard]['feeds'][0]
        filename = plugin.downloadFeed(url)
        self.assertEqual(
            filename,
            '/tmp/dl/Apec/feeds/17a63531332158f5b8204dadc24efcb4.feed'
        )

        # Dowload page
        urls = plugin.getUrls()
        self.assertEqual(len(urls), 30)
        plugin.downloadPages(urls)

    def test_JBRegionJob(self):
        """ Test RegionJob jobboard"""

        # Jobboardname
        jobboard = 'RegionJob'

        # Clean datas
        self.cleanDatas(jobboard)

        # Get feed content
        plugin = utilities.loadJobBoard(jobboard, configs)
        url = configs[jobboard]['feeds'][0]
        filename = plugin.downloadFeed(url)
        self.assertEqual(
            filename,
            '/tmp/dl/RegionJob/feeds/56d1b5fea7dee697630e6457ac3e1e5e.feed'
        )

        # Clean datas
        self.cleanDatas(jobboard)

        # Download all feeds
        feeds = configs[jobboard]['feeds']
        for url in feeds:
            plugin.downloadFeed(url)

        # Dowload page
        urls = plugin.getUrls()
        self.assertEqual(len(urls), 80)
        plugin.downloadPages(urls)

    def test_jobcatcher(self):
        """Execute the jobcatcher functions"""
        jobcatcher.executeall(configs)

if __name__ == "__main__":
    unittest.main(verbosity=2)
