#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Yoann Sculo <yoann.sculo@gmail.com>',
    'Bruno Adelé <bruno@adele.im>',
    'Yankel Scialom <yankel.scialom@mail.com>'
]
__license__ = 'GPLv2'
__version__ = '0.1'

# System
import re
import sys
import time
import glob
from datetime import datetime

# Third party
import sqlite3 as lite
from BeautifulSoup import BeautifulSoup

# Jobcatcher
import utilities
from jc.data import Offer
from jc.jobboard import JobBoard

class JBApec(JobBoard):

    def __init__(self, configs=[]):
        self.name = "Apec"
        super(JBApec, self).__init__(configs)
        self.encoding = {'feed': 'utf-8', 'page': 'iso-8859-1'}

    def getUrls(self):
        """Get Urls offers from feed"""

        urls = list()
        searchdir = "%s/feeds/*.feed" % self._processingDir

        for feed in glob.glob(searchdir):
            # Load the HTML feed
            page = utilities.openPage(feed)

            if page:
                feedid = page.pageid
                html = page.content

                # Search result
                res = re.finditer(
                    r'<item>(.*?)</item>',
                    html,
                    flags=re.MULTILINE | re.DOTALL
                )
                for r in res:
                    # Check if URL is valid
                    m = re.search(r'<link>(http://cadres\.apec\.fr/offres-emploi-cadres/.*?)</link>', r.group(1))
                    if m:
                        urls.append([feedid, m.group(1)])

        return urls

    def _extractItem(self, itemname, soup):
        """Extract a field in html page"""

        html = unicode.join(u'\n', map(unicode, soup))

        res = None
        regex = '<th.*?>%s :.*?</th>.*?<td.*?>(.*?)</td>' % itemname

        m = re.search(regex, html, flags=re.MULTILINE | re.DOTALL)
        if m:
            res = utilities.htmltotext(m.group(1)).strip()

        return res

    def _extractCompany(self, soup):
        """Extract a field in html page"""

        html = unicode.join(u'\n', map(unicode, soup))

        res = None
        regex = u'<tr>.*?<th valign="top">Société :</th>(.*?)</tr>'
        m = re.search(regex, html, flags=re.MULTILINE | re.DOTALL)
        if m:
            company = re.sub(r'<img.*?/>','', m.group(1), flags=re.MULTILINE | re.DOTALL)
            company = re.sub(r'<a href.*?</a>','', company, flags=re.MULTILINE | re.DOTALL)
            company = utilities.htmltotext(company)
            company = company.strip()
            # remove ** (because <strong>company</strong> becomes **company**)
            company = re.sub(ur'\*\*','', company)
            res = company

        return res

    def extractOfferId(self, page):
        offerid = None
        m = re.search(
            ur'.*?/.*?_([0-9]+W)_.*',
            page.url,
            flags=re.MULTILINE | re.DOTALL
        )
        if m:
            offerid = m.group(1)

        return offerid

    def analyzePage(self, page):
        """Analyze page and extract datas"""

        if not self.requireAnalyse(page):
            return ""

        self.datas['offerid'] = self.extractOfferId(page)
        soup = BeautifulSoup(page.content, fromEncoding=self.encoding['page'])
        item = soup.body.find('div', attrs={'class': 'boxMain boxOffres box'})

        if not item:
            content = soup.body.find('p')
            if (content.text == u'L\'offre que vous souhaitez afficher n\'est plus disponible.Cliquer sur le bouton ci-dessous pour revenir à l\'onglet Mes Offres'):
                self.disableOffer(self.datas['offerid'])
                return ""

        # Title
        h1 = soup.body.find('h1', attrs={'class': 'detailOffre'})
        if not item:
            return "No title found"

        self.datas['title'] = utilities.htmltotext(h1.text).replace('Détail de l\'offre : ', '').strip()

        # Refs
        table = item.find('table', attrs={'class': 'noFieldsTable'})
        if not table:
            return "No fields found"

        self.datas['lastupdate'] = page.lastupdate
        self.datas['ref'] = self._extractItem(u"Référence Apec", table)
        self.datas['feedid'] = page.feedid
        self.datas['url'] = page.url
        self.datas['refsoc'] = self._extractItem(u"Référence société", table)

        self.datas['date_add'] = int(time.time())
        self.datas['date_pub'] = datetime.strptime(
            self._extractItem("Date de publication", table),
            "%d/%m/%Y").strftime('%s')

        # Job informations
        self.datas['location'] = self._extractItem("Lieu", table)
        self.datas['company'] = self._extractCompany(table)
        self.datas['contract'] = self._extractItem("Nombre de postes", table)
        self.datas['salary'] = self._extractItem("Salaire", table)
        self.datas['experience'] = self._extractItem("Expérience", table)
        self.filterSalaries(self.datas)

        # Insert to jobboard table
        self.datas['state'] = 'ACTIVE'
        self.insertToJBTable()

        return None

    def createTable(self,):
        if self.isTableCreated():
            return

        conn = None
        conn = lite.connect(self.configs.globals['database'])
        cursor = conn.cursor()

        # create a table
        cursor.execute("""CREATE TABLE jb_%s( \
                       offerid TEXT, \
                       lastupdate INTEGER, \
                       ref TEXT, \
                       feedid TEXT, \
                       refsoc TEXT, \
                       url TEXT, \
                       date_pub INTEGER, \
                       date_add INTEGER, \
                       title TEXT, \
                       company TEXT, \
                       contract TEXT, \
                       location TEXT, \
                       salary TEXT, \
                       salary_min FLOAT, \
                       salary_max FLOAT, \
                       salary_nbperiod INTEGER, \
                       salary_unit FLOAT, \
                       salary_bonus TEXT, \
                       salary_minbonus FLOAT, \
                       salary_maxbonus FLOAT, \
                       experience TEXT, \
                       state TEXT, \
                       PRIMARY KEY(offerid))""" % self.name)

    def insertToJBTable(self):
        conn = lite.connect(self.configs.globals['database'])
        conn.text_factory = str
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO jb_%s VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" % 
                           self.name, (
                               self.datas['offerid'],
                               self.datas['lastupdate'],
                               self.datas['ref'],
                               self.datas['feedid'],
                               self.datas['refsoc'],
                               self.datas['url'],
                               self.datas['date_pub'],
                               self.datas['date_add'],
                               self.datas['title'],
                               self.datas['company'],
                               self.datas['contract'],
                               self.datas['location'],
                               self.datas['salary'],
                               self.datas['salary_min'],
                               self.datas['salary_max'],
                               self.datas['salary_nbperiod'],
                               self.datas['salary_unit'],
                               self.datas['salary_bonus'],
                               self.datas['salary_minbonus'],
                               self.datas['salary_maxbonus'],
                               self.datas['experience'],
                               self.datas['state'],

                           )
                       )

            conn.commit()
        except lite.IntegrityError:
            pass
        finally:
            if conn:
                conn.close()

        return 0

    def createOffer(self, data):
        """Create a offer object with jobboard data"""
        data = dict(data)

        o = Offer()
        o.src = self.name
        o.url = data['url']
        o.offerid = data['offerid']
        o.lastupdate = data['lastupdate']
        o.ref = data['ref']
        o.feedid = data['feedid']
        o.title = data['title']
        o.company = data['company']
        o.contract = data['contract']
        o.location = data['location']
        o.salary = data['salary']
        o.salary_min = data['salary_min']
        o.salary_max = data['salary_max']
        o.salary_unit = data['salary_unit']
        o.salary_nbperiod = data['salary_nbperiod']
        o.salary_bonus = data['salary_bonus']
        o.salary_minbonus = data['salary_minbonus']
        o.salary_maxbonus = data['salary_maxbonus']
        o.date_pub = data['date_pub']
        o.date_add = data['date_add']
        o.state = data['state']

        if o.offerid and o.ref and o.company:
            return o

        return None

    def filterSalaries(self, data):
        minbonus = 0
        maxbonus = 0

        if self.datas['salary']:
            # Salary
            self.datas['salary_unit'] = ''
            self.datas['salary_min'] = 0
            self.datas['salary_max'] = 0
            self.datas['salary_nbperiod'] = 0
            # Bonus
            self.datas['salary_bonus'] = ''
            self.datas['salary_minbonus'] = 0
            self.datas['salary_maxbonus'] = 0

            # Search salary range
            m = re.search(
                ur'([0-9]+)([/-])([0-9]+)K€ *(brut)?/an(.*)',
                self.datas['salary'],
                flags=re.MULTILINE | re.DOTALL
            )
            if m:
                self.datas['salary_unit'] = 12
                self.datas['salary_min'] = m.group(1)
                self.datas['salary_max'] = m.group(3)
                self.datas['salary_nbperiod'] = 12
                self.datas['salary_bonus'] = m.group(5)

                # Format
                self.datas['salary_min'] = float(
                    re.sub(
                        r'[^0-9.]',
                        '',
                        self.datas['salary_min']
                    )
                ) * 1000
                self.datas['salary_max'] = float(
                    re.sub(
                        r'[^0-9.]',
                        '',
                        self.datas['salary_max']
                    )
                ) * 1000
            else:
                # Search salary
                m = re.search(
                    ur'([0-9]+) *K€ *brut/an(.*)',
                    self.datas['salary'],
                    flags=re.MULTILINE | re.DOTALL
                )
                if m:
                    self.datas['salary_unit'] = 12
                    self.datas['salary_min'] = m.group(1)
                    self.datas['salary_max'] = 0
                    self.datas['salary_nbperiod'] = 12
                    self.datas['salary_bonus'] = m.group(2)

                    # Format
                    self.datas['salary_min'] = float(
                        re.sub(
                            r'[^0-9.]',
                            '',
                            self.datas['salary_min']
                        )
                    ) * 1000

            if self.datas['salary_unit'] == 'Annuel':
                self.datas['salary_unit'] = 12
            elif self.datas['salary_unit'] == 'Mensuel':
                self.datas['salary_unit'] = 1
