#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Bruno Adelé <bruno@adele.im>',
]
__license__ = 'GPLv2'
__version__ = '0.1'

# System
import re
import time
import html2text
import glob
from datetime import datetime

# Third party
import sqlite3 as lite
from BeautifulSoup import BeautifulSoup

# Jobcatcher
import utilities
from jc.data import Offer
from jc.jobboard import JobBoard

# newly added
import dateparser

class JBPoleEmploi(JobBoard):

    def __init__(self, configs=None):
        self.name = "PoleEmploi"
        super(JBPoleEmploi, self).__init__(configs)
        self.encoding = {'feed': 'utf-8', 'page': 'utf-8'}

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
                    r'li data-id-offre="(.*?)"',
                    html,
                    flags=re.MULTILINE | re.DOTALL
                )

                for r in res:
                    string = r'/offres/recherche/detail/'+r.group(1)
                    url = "https://candidat.pole-emploi.fr%s" % string
                    urls.append([feedid, url])

        return urls

    def _regexExtract(self, text, soup):
        """Extract a field in html page"""

        html = unicode.join(u'\n', map(unicode, soup))
        regex='<div class="label"><span>%s</span></div>.*?<div class="value"><span.*?>(.*?)</span></div>' % text
        res = None
        m = re.search(regex, html, flags=re.MULTILINE | re.DOTALL)
        if m:
            res = utilities.htmltotext(m.group(1)).strip()

        return res

    def extractOfferId(self, page):
        offerid = None
        m = re.search(
            ur'.*?/detail/(.*)',
            page.url,
            flags=re.MULTILINE | re.DOTALL
        )
        if m:
            offerid = m.group(1)

        return offerid

    def _get_data_contract(self, soup):
        """Get the contract type in text blop"""
        res = None
        desc_aside_item = soup.find('div', attrs={'class': 'description-aside col-sm-4 col-md-5'})
        if desc_aside_item:
            pattern_cdi = r'ind\xe9termin\xe9e'
            pattern_cdd = r'd\xe9termin\xe9e'
            pattern_interim = r'int\xe9rimaire'
            html = unicode.join(u'\n', map(unicode, soup))

            m = re.search(pattern_cdi, html, flags=re.MULTILINE | re.DOTALL)
            if m:
                return "CDI"

            m = re.search(pattern_cdd, html, flags=re.MULTILINE | re.DOTALL)
            if m:
                return "CDD"

            m = re.search(pattern_interim, html, flags=re.MULTILINE | re.DOTALL)
            if m:
                return "Interim"
        return "Unknown"

    def _get_title(self, soup):
        """Get the job title"""
        h2 = soup.find('h2', attrs={'class': 't2 title'})
        if not h2:
            return "Title not found"
        return utilities.htmltotext(h2.text).strip()

    def _get_published_date(self, soup):
        """Getting the published date"""
        date_item = soup.find('p', attrs={'class': 't5 title-complementary'})
        if date_item:
            m = re.search('[0-9]{1,2} \D* [0-9]{4}', str(date_item.text))
            if m:
                return int(time.mktime(dateparser.parse(m.group(0)).date().timetuple()))
        return int(time.time())

    def _get_company(self, soup):
        company_item = soup.find('h4', attrs={'class': 't4 title'})
        if not company_item:
            return "N/A"
        return utilities.htmltotext(company_item.text).strip()

    def _get_department_num(self, soup):
        """ Getting department number """
        dep_num_item = soup.find('p', attrs={'class': 't4 title-complementary'})
        if dep_num_item:
            m = re.search('[0-9]{1,2}', utilities.htmltotext(dep_num_item.text).strip())
            if m:
                return m.group(0)
        return None

    def _get_location(self, soup):
        """ Getting location (city) """
        location_item = soup.find('p', attrs={'class': 't4 title-complementary'})
        if location_item:
            m = re.search(' - (.*) -', utilities.htmltotext(location_item.text).strip())
            if m:
                return m.group(1)
        return "N/A"

    def analyzePage(self, page):
        """Analyze page and extract datas"""

        #if not self.requireAnalyse(page):
        #    return ""

        self.datas['offerid'] = self.extractOfferId(page)
        soup = BeautifulSoup(page.content, fromEncoding=self.encoding['page'])

        unavailable_offer = soup.body.find('Offre_indisponible')
        if unavailable_offer:
            self.disableOffer(self.datas['offerid'])
            return "Offer not available"


        # searching for modal-details modal-details-offre
        item = soup.body.find('div', attrs={'class': 'modal-details modal-details-offre'})
        if not item:
            self.disableOffer(self.datas['offerid'])
            return "No modal-details-offre content found"


        # Title
        self.datas['title'] = self._get_title(item)

        # Url
        self.datas['url'] = page.url

        # Ref
        # self.datas['ref'] = self._regexExtract(u'Numéro de l\'offre', li)
        self.datas['ref'] = "N/A"

        # Last update
        li = item.find('li', attrs={'class': 'primary'})
        self.datas['lastupdate'] = page.lastupdate

        # Feed id
        self.datas['feedid'] = page.feedid

        # Date of publication
        self.datas['date_pub'] = self._get_published_date(item)

        # Add in db date
        self.datas['date_add'] = int(time.time())

        # Job informations
        self.datas['contract'] = self._get_data_contract(item)

        # Salary
        self.datas['salary'] = "N/A"
        # self.datas['salary'] = self._regexExtract(
        #     u'Salaire indicatif', item
        # )
        self.filterSalaries(self.datas)

        # Location
        self.datas['department'] = self._get_department_num(item)
        self.datas['location'] = self._get_location(item)

        # Company
        self.datas['company'] = self._get_company(item)

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
                       url TEXT, \
                       date_pub INTEGER, \
                       date_add INTEGER, \
                       title TEXT, \
                       company TEXT, \
                       contract TEXT, \
                       location TEXT, \
                       department TEXT, \
                       salary TEXT, \
                       salary_min FLOAT, \
                       salary_max FLOAT, \
                       salary_nbperiod INTEGER, \
                       salary_unit FLOAT, \
                       salary_bonus TEXT, \
                       salary_minbonus FLOAT, \
                       salary_maxbonus FLOAT, \
                       state TEXT, \
                       PRIMARY KEY(offerid))""" % self.name)

    def insertToJBTable(self):
        conn = lite.connect(self.configs.globals['database'])
        conn.text_factory = str
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO jb_%s VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" % self.name,
                           (
                               self.datas['offerid'],
                               self.datas['lastupdate'],
                               self.datas['ref'],
                               self.datas['feedid'],
                               self.datas['url'],
                               self.datas['date_pub'],
                               self.datas['date_add'],
                               self.datas['title'],
                               self.datas['company'],
                               self.datas['contract'],
                               self.datas['location'],
                               self.datas['department'],
                               self.datas['salary'],
                               self.datas['salary_min'],
                               self.datas['salary_max'],
                               self.datas['salary_nbperiod'],
                               self.datas['salary_unit'],
                               self.datas['salary_bonus'],
                               self.datas['salary_minbonus'],
                               self.datas['salary_maxbonus'],
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
        o.department = data['department']
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
                ur'(.*?) de (.*?),.*? à (.*?),.*? euros sur (.*?) mois(.*)',
                self.datas['salary'],
                flags=re.MULTILINE | re.DOTALL
            )
            if m:
                self.datas['salary_unit'] = m.group(1)
                self.datas['salary_min'] = m.group(2)
                self.datas['salary_max'] = m.group(3)
                self.datas['salary_nbperiod'] = int(m.group(4))
                self.datas['salary_bonus'] = m.group(5)

                # Format
                self.datas['salary_min'] = float(
                    re.sub(
                        r'[\W_]',
                        '',
                        self.datas['salary_min']
                    )
                )
                self.datas['salary_max'] = float(
                    re.sub(
                        r'[\W_]',
                        '',
                        self.datas['salary_max']
                    )
                )
            else:
                # Search salary
                m = re.search(
                    ur'(.*?) de (.*?),.*? euros sur (.*?) mois(.*)',
                    self.datas['salary'],
                    flags=re.MULTILINE | re.DOTALL
                )
                if m:
                    self.datas['salary_unit'] = m.group(1)
                    self.datas['salary_min'] = m.group(2)
                    self.datas['salary_max'] = 0
                    self.datas['salary_nbperiod'] = int(m.group(3))
                    self.datas['salary_bonus'] = m.group(4)

                    # Format
                    self.datas['salary_min'] = float(
                        re.sub(
                            r'[\W_]',
                            '',
                            self.datas['salary_min']
                        )
                    )

            if self.datas['salary_unit'] == 'Annuel':
                self.datas['salary_unit'] = 12
            elif self.datas['salary_unit'] == 'Mensuel':
                self.datas['salary_unit'] = 1


