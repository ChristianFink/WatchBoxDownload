#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Author: Christian Fink <christian>
# @Date:   2018-05-18T11:00:46+02:00
# @Email:  christian.fink@bluewin.ch
# @Last modified by:   christian
# @Last modified time: 2018-05-19T11:45:58+02:00

import sys
import re
import requests
from bs4 import BeautifulSoup
import json
import youtube_dl


def myHook(d):
    if d['status'] == 'finished':
        print("Download beendet")
    elif d['status'] == "downloading":
        print("{0:5.2f}%".format(d['elapsed']))
    else:
        print(d)
# [download]  26.6% of ~494.84MiB at  1.53MiB/s ETA 05:53
# {
#  'status': 'downloading',
#  'downloaded_bytes': 138273888,
#  'fragment_index': 198,
#  'fragment_count': 743,
#  'filename': 'Zurück in die Vergangenheit.fvideo=2800000.mp4',
#  'tmpfilename': 'Zurück in die Vergangenheit.fvideo=2800000.mp4.part',
#  'elapsed': 128.2676911354065,
#  'total_bytes_estimate': 518876256.4848485,
#  'eta': 353,
#  'speed': 1604477.9087344012,
#  '_eta_str': '05:53',
#  '_percent_str': ' 26.6%',
#  '_speed_str': ' 1.53MiB/s',
#  '_total_bytes_estimate_str': '494.84MiB'
# }

def __mainContent(url):
    breadCrumb = url.split("/")[3:]
    details = {'contentType': breadCrumb[0]}

    r = requests.get(url)
    if r.status_code != 200:
        return False
    soup = BeautifulSoup(r.text, 'html.parser')

    _image = soup.find("div", attrs={'class': "video-details__image"})
    if _image:
        _img = _image.find('img')
        if _img['src'].startswith("/"):
            _img['src'] = "http:{0}".format(_img['src'])
            details['image'] = _img["src"]
            details['title'] = _img['alt']

            if details['contentType'] == "filme":
                details['destName'] = "{0}.%(ext)s".format(
                    details['title']
                )
    _dataAsset = soup.find("div", class_="big-teaser-video")
    if _dataAsset:
        details['data-asset-id'] = _dataAsset['data-asset-id']

    for _js in soup.find_all('script', attrs={'type': 'text/javascript'}):
        if _js.get("src", None):
            continue
        m = re.search("var playerConf = ({.*);", _js.text)
        if not m:
            continue
        playerConf = json.loads(m.group(1))
        details['hls'] = playerConf['source']['hls']
        details['dash'] = playerConf['source']['dash']
        break

    if details['contentType'] == "filme":
        yield details
    elif details['contentType'] == "serien":
        _SerienURL = ['http://watchbox.de', 'serien', breadCrumb[1]]
        if 'dash' in details:
            """
            url war Episode
            Serientitel, Bild und Episodentitel ermitteln
            """
            serien_content = __serienContent("/".join(_SerienURL))
            episoden_content = __episodeContent(url, soup)
            details['destName'] = "{0} - S{1:02d} E{2:02d} - {3}.%(ext)s".format(
                serien_content['title'],
                episoden_content['season'],
                episoden_content['episode'],
                episoden_content['episodeTitle']
            )
            details['image'] = serien_content['image']
            yield details
        else:
            """
            url war Staffel oder Serie
            Staffelinhalt oder Serieninhalt ermitteln
            und alle Episoden zurückgeben
            """
            serien_content = __serienContent(url)
            if len(breadCrumb) == 2:
                for season in serien_content['seasons']:
                    for episode in __staffelContent(
                        season['url'],
                        details['data-asset-id']
                    ):
                        episoden_content = __episodeContent(episode['url'])
                        yield {
                            'contentType': 'serien',
                            'hls': episoden_content['hls'],
                            'dash': episoden_content['dash'],
                            'destName': "{0} - S{1:02d} E{2:02d} - {3}.%(ext)s".format(
                                serien_content['title'],
                                episoden_content['season'],
                                episoden_content['episode'],
                                episoden_content['episodeTitle']
                            ),
                            'image': serien_content['image']
                        }

            if len(breadCrumb) == 3:
                staffelContent = __staffelContent(
                    url,
                    details['data-asset-id'],
                    soup
                )
                for episode in staffelContent:
                    episoden_content = __episodeContent(episode['url'])
                    yield {
                        'contentType': 'serien',
                        'hls': episoden_content['hls'],
                        'dash': episoden_content['dash'],
                        'destName': "{0} - S{1:02d} E{2:02d} - {3}.%(ext)s".format(
                            serien_content['title'],
                            episoden_content['season'],
                            episoden_content['episode'],
                            episoden_content['episodeTitle']
                        ),
                        'image': serien_content['image']
                    }

def __staffelContent(url, assetID, soup=None):
    episoden = []
    if soup is None:
        if url is None:
            return None
        r = requests.get(url)
        if r.status_code != 200:
            print("FEHLER : {0}".format(r.status_code))
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
    for _ep in soup.find_all(
        "a",
        class_="teaserset__teaser",
        attrs={'data-asset-id': assetID}
    ):
        url = "http://www.watchbox.de{0}".format(_ep['href'])
        _info = _ep.find("div", class_='teaser__season-info')
        if _info:
            m = re.search(
                "Staffel (\d*), Episode (\d*)",
                _info.text.replace("\n", "").strip()
            )
            if m:
                season = int(m.group(1))
                episode = int(m.group(2))
        _header = _ep.find("div", class_="teaser__header")
        if _header:
            episodeTitle = _header.text.replace(
                "\n", ""
            ).strip()
        episoden.append({
            'season': season,
            'episode': episode,
            'episodeTitle': episodeTitle,
            'url': url
        })
    return episoden

def __serienContent(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    dataAssetID = soup.find(
        "div",
        class_="big-teaser-video"
    )['data-asset-id']
    details = {'data-asset-id': dataAssetID, 'seasons': []}
    _image = soup.find("div", attrs={'class': "video-details__image"})
    if _image:
        _img = _image.find('img')
        if _img['src'].startswith("/"):
            _img['src'] = "http:{0}".format(_img['src'])
        details['image'] = _img["src"]
        details['title'] = _img['alt']

    _seasons = soup.find('ul', class_="season-panel")
    if _seasons:
        details['seasons'] = [
            {
                'nr': int(season['data-season-number']),
                'title': season.text.replace("\n", "").strip(),
                'url': "http://watchbox.de{0}".format(
                    season.find('a')['href']
                )
            }
            for season in _seasons.find_all(
                "li",
                class_="season-panel__item"
            )
        ]
    return details

def __episodeContent(url, soup=None):
    if soup is None:
        if url is None:
            return None
        r = requests.get(url)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
    m = re.search("-(\d*)\.html", url)
    if m:
        id_episode = int(m.group(1))
        _ep = soup.find(
            "a",
            class_="teaserset__teaser",
            attrs={'data-movie-id': str(id_episode)}
        )
        if _ep:
            _info = _ep.find("div", class_='teaser__season-info')
            if _info:
                m = re.search(
                    "Staffel (\d*), Episode (\d*)",
                    _info.text.replace("\n", "").strip()
                )
                if m:
                    season = int(m.group(1))
                    episode = int(m.group(2))
            _header = _ep.find("div", class_="teaser__header")
            if _header:
                episodeTitle = _header.text.replace(
                    "\n", ""
                ).strip()
    for _js in soup.find_all('script', attrs={'type': 'text/javascript'}):
        if _js.get("src", None):
            continue
        m = re.search("var playerConf = ({.*);", _js.text)
        if not m:
            continue
        playerConf = json.loads(m.group(1))
        hls = playerConf['source']['hls']
        dash = playerConf['source']['dash']
        break

    return {
        'season': season,
        'episode': episode,
        'episodeTitle': episodeTitle,
        'hls': hls,
        'dash': dash
    }


def main():
    # url = 'https://www.watchbox.de/serien/yosuga-no-sora-15375/staffel-1/zurueck-in-die-vergangenheit-373928.html'
    # url = 'https://www.watchbox.de/serien/real-humans-echte-menschen-14725/staffel-1/folge-9-346072.html'

    url = 'https://www.watchbox.de/serien/real-humans-echte-menschen-14725/staffel-1'
    # url = 'https://www.watchbox.de/serien/real-humans-echte-menschen-14725'
    # url = 'https://www.watchbox.de/filme/venus-im-pelz-16041.html'

    # print(__mainContent(url))
    for i in __mainContent(url):
        print(i)


if __name__ == "__main__":
    main()
