#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

payload = {
    'active': "true",
    'maxPerPage': 28,
    'page': 1,
    'term': "Hentai*",
    'types': '["film", "serie"]'
    # 'types': '["serie"]'
}

url = "https://api.watchbox.de/v1/search/"
mimeType = "application/json; charset=utf-8"
r = requests.get(url, params=payload)

urlBase = "https://www.watchbox.de/{0}/{1}-{2}/"

if r.status_code == 200:
    data = r.json()

    print(50*"=")
    print(data['total'])
    print(50*"=")
    for item in data['items']:
        itemURL = urlBase.format(
            "filme" if item['type'] == "film" else "serien",
            item['seoPath'],
            item['entityId']
        )
        print("{0} {1} [{2}]".format(
            "*" if item["active"] else " ",
            item["formatTitle"],
            itemURL
        ))
        print(50*"-")
        # for k, v in item.items():
        #     print("{0:50} : {1}".format(k, v))

# type                                               : film
# entityId                                           : 15887
# headline                                           : Hentai Kamen 2 - The Abnormal Crisis
# description                                        : Die Welt steht vor dramatischen Veränderungen: Täglich verschwinden immer mehr Damenhöschen von der Bildfläche! Für Kyosuke, den Superhelden Hentai Kamen, sind die Slips aber unabdingbar, denn nur mit einem Schlüpfer seiner Freundin Aiko über dem Gesicht kann er seine Superkräfte entfalten und die Welt vor allem Übel beschützen. Als Aiko ihre Höschen aufgrund der weltweiten Knappheit zurückfordert, wird es tragisch: Unbeabsichtigt verletzt Kyosuke Aikos Gefühle, nicht wissend, dass Tadashi Makoto, ein Klassenkamerad von Aiko, die Beziehung der beiden argwöhnisch beäugt. Ausgerechnet jetzt, wo er Aikos Zuneigung verliert und die Schlüpfer von der Erde weichen, trifft Hentai Kamen auf seinen größten Feind...
# fsk                                                : 16
# duration                                           : 01:53:07
# views                                              : {'last24Hours': 2, 'last7Days': 33, 'allTime': 298}
# productionCountry                                  : Japan
# productionYear                                     : 2016
# seoPath                                            : hentai-kamen-2-the-abnormal-crisis
# genres                                             : ['Action', 'Fantasy', 'Komödie', 'Asian']
# tags                                               : []
# createdAt                                          : {'date': '2018-03-01 00:00:00', 'timezone_type': 1, 'timezone': '+01:00'}
# active                                             : True
# rating                                             :
# onlineDate                                         : {'date': '2018-03-01 00:00:00', 'timezone_type': 1, 'timezone': '+01:00'}
# offlineDate                                        : {'date': '2019-12-31 23:59:59', 'timezone_type': 1, 'timezone': '+01:00'}
# season                                             : None
# episode                                            : None
# movieId                                            : 422590
# formatTitle                                        : Hentai Kamen 2 - The Abnormal Crisis
# teaserText                                         : None
# infoTextShort                                      : Fortsetzung der abgedrehten Superhelden-Geschichte mit Trash-Faktor.
# subHeadline                                        : None



else:
    print(r.status_code)
