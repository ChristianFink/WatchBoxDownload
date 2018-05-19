#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Author: Christian Fink <christian>
# @Date:   2018-05-18T11:00:46+02:00
# @Email:  christian.fink@bluewin.ch
# @Last modified by:   christian
# @Last modified time: 2018-05-18T18:50:40+02:00

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


def main():
    url = 'https://www.watchbox.de/serien/yosuga-no-sora-15375/staffel-1/zurueck-in-die-vergangenheit-373928.html'
    # url = 'https://www.watchbox.de/serien/real-humans-echte-menschen-14725'

    r = requests.get(url)
    if r.status_code != 200:
        sys.exit(-1)

    soup = BeautifulSoup(r.text, 'html.parser')
    for _js in soup.find_all('script', attrs={'type': 'text/javascript'}):
        if _js.get("src", None):
            continue
        m = re.search("var playerConf = ({.*);", _js.text)
        if not m:
            continue
        playerConf = json.loads(m.group(1))
        # details['hls'] = playerConf['source']['hls']
        dash = playerConf['source']['dash'].replace("\\", "")
        break

    ydl_opts = {
        # 'outtmpl': "Zurück in die Vergangenheit.%(ext)s",
        'noplayplist': True,
        'progress_hooks': [myHook],
        'quiet': True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(dash, download=False)
        # ydl.download([dash])
    # print(result)
    for format in result['formats']:
        print(format['format'])





if __name__ == "__main__":
    main()
