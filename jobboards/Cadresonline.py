#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Jonathan Courtoux <j.courtoux@gmail.com>',
    'Bruno Adelé <bruno@adele.im>'
]
__copyright__ = 'Copyright (C) 2013 jonathan courtoux'
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

import dateparser

class JBCadresonline(JobBoard):

    def __init__(self, configs=[]):
        self.name = "Cadresonline"
        super(JBCadresonline, self).__init__(configs)
        self.encoding = {'feed': 'utf-8', 'page': 'iso-8859-1'}

        # self.url = "http://www.cadresonline.com"
        # self.lastFetch = ""
        # self.processingDir = self.dlDir + "/cadresonline"
        # self.lastFetchDate = 0

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
                    m = re.search(r'<link>(https://www\.cadresonline\.com/.*?)</link>', r.group(1))
                    if m:
                        urls.append([feedid, m.group(1)])
        return urls

    # def fetch_url(self, url):
    #     filename = url.split('/')[-1]
    #     utilities.download_file(url, self.processingDir)

    #     xmldoc = minidom.parse(os.path.join(self.processingDir, filename))

    #     MainPubDate = xmldoc.getElementsByTagName('pubDate')[0].firstChild.data

    #     itemlist = xmldoc.getElementsByTagName('item')

    #     for elt in itemlist :
    #         # TODO : Test object first
    #         title = elt.getElementsByTagName('title')[0].firstChild.data
    #         link = elt.getElementsByTagName('link')[0].firstChild.data.split("?")[0]
    #         pubDate = elt.getElementsByTagName('pubDate')[0].firstChild.data

    #         if (not os.path.isfile(os.path.join(self.processingDir, link.split('/')[-1]))):
    #             print "Downloading %s" % (link)
    #             utilities.download_file(link, self.processingDir)

    # def fetch(self):
    #     print "Fetching " + self.name

    #     feed_list = configs['cadresonline']['feeds']
    #     if (not os.path.isdir(self.processingDir)):
    #             os.makedirs(self.processingDir)

    #     for url in feed_list :
    #         self.fetch_url(url)

    #     self.processOffers()

    # def processOffers(self):
    #     for file in os.listdir(self.processingDir):
    #         if (not file.lower().endswith('.html')):
    #                 continue

    #         print "Processing %s" % (file)
    #         offer = CadreonlineOffer()
    #         res = offer.loadFromHtml(os.path.join(self.processingDir, file))
    #         if (res != 0):
    #             continue
    #         offer.date_add = int(time.time())
    #         loc = Location()
    #         # loc.loadFromAddress(offer.location)
    #         offer.lat = loc.lat
    #         offer.lon = loc.lon
    #         if (offer.add_db() == 0):
    #             os.remove(os.path.join(self.processingDir,file))

    # def setup(self):
    #     print "setup " + self.name

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

    def _get_title(self, soup):
        """Get the job title"""
        title_item = soup.find('h1', attrs={'itemprop': 'title'})
        title = "Title not found"
        if not title_item:
            return title
        full_title = utilities.htmltotext(title_item.text).strip()
        m = re.search('(\D*)', full_title)
        if m:
            title = m.group(1)
        return title

    def _get_job_ref(self, soup):
        """Get the job ref"""
        ref_item = soup.find('li', attrs={'itemprop': 'jobReference'})
        ref = "N/A"
        if not ref_item:
            return ref
        full_ref = utilities.htmltotext(ref_item.text).strip()
        m = re.search(' :(.*)', full_ref)
        if m:
            ref = m.group(1)
        return ref

    def _get_last_update(self, soup):
        """Get the job ref"""
        lu_item = soup.find('strong', attrs={'itemprop': 'datePosted'})
        if not lu_item:
            return int(time.time())
        date_str = utilities.htmltotext(lu_item.text).strip()
        return int(time.mktime(dateparser.parse(date_str).date().timetuple()))

    def _get_data_contract(self, soup):
        contract_item = soup.find('strong', attrs={'itemprop': 'employmentType'})
        if not contract_item:
            return "N/A"
        return utilities.htmltotext(contract_item.text).strip()

    def _get_location(self, soup):
        location_item = soup.find('strong', attrs={'itemprop': 'addressRegion'})
        if not location_item:
            return "N/A"
        return utilities.htmltotext(location_item.text).strip()

    def _get_company(self, soup):
        resume_item = soup.find('ul', attrs={'class': 'resume'})
        if resume_item:
            m = re.search('<strong>([a-zA-Z\ ]*)<\/strong>', str(resume_item))
            if m:
                return str(m.group(1))
        return "N/A"

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

    def analyzePage(self, page):
        """Analyze page and extract datas"""

        #if not self.requireAnalyse(page):
        #    return ""

        self.datas['offerid'] = self.extractOfferId(page)
        soup = BeautifulSoup(page.content, fromEncoding=self.encoding['page'])
        item = soup.body.find('div', attrs={'class': 'boxMain boxOffres box'})

        if not item:
            content = soup.body.find('p')
            if (content.text == u'L\'offre que vous souhaitez afficher n\'est plus disponible.Cliquer sur le bouton ci-dessous pour revenir à l\'onglet Mes Offres'):
                self.disableOffer(self.datas['offerid'])
                return ""

        # @TODO to change ?
        self.datas['offerid'] = self._get_job_ref(soup)

        # Title
        self.datas['title'] = self._get_title(soup)

        # Url
        self.datas['url'] = page.url

        # Ref
        self.datas['ref'] = self._get_job_ref(soup)

        # Last update
        self.datas['lastupdate'] = self._get_last_update(soup)

        # Feed id
        self.datas['feedid'] = page.feedid

        # Date of publication
        self.datas['date_pub'] = self.datas['lastupdate']

        # Add in db date
        self.datas['date_add'] = int(time.time())

        # Job informations
        self.datas['contract'] = self._get_data_contract(soup)

        # # Salary
        self.datas['salary'] = "N/A"
        # # self.datas['salary'] = self._regexExtract(
        # #     u'Salaire indicatif', item
        # # )
        self.filterSalaries(self.datas)

        # # Location
        # self.datas['department'] = self._get_department_num(item)
        self.datas['department'] = "N/A"
        self.datas['location'] = self._get_location(soup)

        # # Company
        self.datas['company'] = self._get_company(soup)

        # Insert to jobboard table
        self.datas['state'] = 'ACTIVE'

        self.insertToJBTable()

        return None

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

        print("Create offer return None")
        print("o.offerid:", o.offerid)
        print("o.ref:", o.ref)
        print("o.company:", o.company)
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
                               self.datas['state']
                           )
                       )

            conn.commit()
        except lite.IntegrityError:
            pass
        finally:
            if conn:
                conn.close()

        return 0

# class CadreonlineOffer(Offer):

#     src     = 'CADRESONLINE'
#     license = ''

#     def loadFromHtml(self, filename):
#         fd = open(filename, 'rb')
#         html = fd.read()
#         fd.close()

#         soup = BeautifulSoup(html, fromEncoding="UTF-8")

#         # Offer still available ?
#         res = soup.body.find('div', attrs={'id':'job_offer'})
#         if (res != None):
#             content = res.find('p')
#             if (content.text == u'L\'offre que vous souhaitez afficher n\'est plus disponible.Cliquer sur le bouton c\
#                 i-dessous pour revenir à l\'onglet Mes Offres'):
#                 return 1

#         # Title
#         res = soup.body.find("div", attrs={'id': 'ariane'})
#         if not res:
#             return -1
#         res = res.find('strong')
#         self.title = HTMLParser().unescape(res.text)

#         # Other information
#         res = soup.body.find("ul", attrs={'class': 'resume'})
#         if not res:
#             return -1

#         res = res.findAll("li")
#         if not res:
#             return -1

#         for elt in res:
#             # Contract
#             m = re.match(ur'^Contrat.* :(.*)', elt.text)
#             if m:
#                 self.contract = m.group(1)
#                 self.cleanContract()

#             # Company
#             m = re.match(ur'^Soci.* :(.*)', elt.text)  # TODO fix a UTF problem
#             if m:
#                 self.company = m.group(1)

#             # Location
#             m = re.match(ur'^Localisation.* :(.*)', elt.text)
#             if m:
#                 self.location = m.group(1)

#             # Reference
#             m = re.match(ur'^R.*f.*ence.* :(.*)', elt.text)
#             if m:
#                 self.ref = m.group(1)

#             # Reference
#             m = re.match(ur'^Publi.* le :(.*)', elt.text)
#             if m:
#                 self.date_pub = datetime.datetime.strptime(m.group(1), "%d/%m/%Y").strftime('%s')
#                 print self.date_pub


#         # Content
#         # res = soup.body.find('div', attrs={'class':'contentWithDashedBorderTop marginTop boxContent'})
#         # res = res.find('div', attrs={'class':'boxContentInside'})
#         # self.content = HTMLParser().unescape(res.text);

#         self.url = "http://cadresonline.com/" + os.path.basename(filename)

#         return 0
