#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Bruno Adelé <bruno@adele.im>',
    'Yoann Sculo <yoann.sculo@gmail.com>',
    'Yankel Scialom (YSC) <yankel.scialom@mail.com>',
]
__license__ = 'GPLv2'
__version__ = '0.1'

# Uncomment feed entries to enable them

configs = {
    # 'PoleEmploi': {
    #     # How to add a custom feed?
    #     # STEP 1: Go to https://www.pole-emploi.fr/accueil/
    #     # STEP 2: Fill a keyword + Location
    #     # STEP 3: Save link as per example below
    #     'feeds': [
    #         {
    #             # Mot clé: Embarqué
    #             # Lieu: Nantes (50km)
    #             'url': 'https://candidat.pole-emploi.fr/offres/recherche?lieux=44109&motsCles=embarqu%C3%A9&offresPartenaires=true&rayon=50&tri=0'
    #         },
    #         {
    #             # Mot clé: Embedded
    #             # Lieu: Rennes (50km)
    #             'url': 'https://candidat.pole-emploi.fr/offres/recherche?motsCles=Embarqu%C3%A9&offresPartenaires=true&range=0-9&rayon=50&tri=0'
    #         }
    #     ]
    # },
    # How to add a custom feed?
    # 1. Go to https://cadres.apec.fr/home/mon-compte/abonnements-flux-rss.html
    # 2. Fill the form;
    # 3. Find and click the RSS icon next to "Voici le flux RSS généré correspondant à vos critères;"
    # 4. Copy the url and add it below: "{'url': 'PASTE HERE'},";
    # 5. Swear & curse Apec.fr for not providing more custom feeds.
    # 'Apec': {
    #    'feeds': [
    #         {
    #             # APEC, Informatique industrielle, Bretagne
    #             'url': 'https://www.apec.fr/fluxRss/XML/OffresCadre_F101810_R705.xml'
    #         }
    #     ]
    # },
    # How to add a custom feed?
    # 1. Go to https://www.cadresonline.com/recherche-emploi
    # 2. Fill the form;
    # 3. Click "Lancer la recherche" (Search);
    # 4. Find & click the RSS logo (on the right-hand side of "x offres correspondent à votre recherche d'emploi;"
    # 5. Copy the url and add it below: "{'url': 'PASTE HERE'},".
    # 'Cadresonline': {
    #    'feeds': [
    #         {
    #             # Ingénieur en Pays de Loire
    #             'url': 'https://www.cadresonline.com/resultat-emploi/feed.rss?flux=1&kw=Ing%C3%A9nieur&kt=1&sr=17t.0.1.2.3.4&jc=5t.0.1.2.3.4.5.6.7&dt=1534706430'
    #         },
    #    ]
    # },
    # How to add a custom feed?
    # 1. Select your region                             {REGION_CODE}
    #   See ./help/regionjobs-region-codes.txt
    # 2. Select your job sector                         {SECTOR_CODE}
    #   See ./help/regionjobs-sector-codes.txt
    # 3. Craft your feed url {URL} =
    #   http://www.{REGION_CODE}/fr/rss/flux.aspx?&fonction={SECTOR_CODE}
    # 4. Add the line {'url': '{URL}'},
    # 'RegionJob': {
    #    'feeds': [
    #         {
    #             # Nantes, Embarqué, CDI
    #             'url': 'https://www.ouestjob.com/emplois/recherche.html?l=Nantes+44000&l_autocomplete=http%3A%2F%2Fwww.rj.com%2Fcommun%2Flocalite%2Fcommune%2F44109&f=Informatique_dev&c=CDI&k=embarqu%C3%A9&q=Ingenieur_B5'
    #         }
    #    ]
    # },
    'Septlieues': {
       'feeds': [
            {
                # Toute la France, logiciel embarqué
                'url': 'http://www.sept-lieues.com/Jobs/Search?EmbeddedSoftwareGroup=true'
            }
       ]
    },
}
