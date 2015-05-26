'''Another duckduckgo searcher

Returns only urls
'''
from bs4 import BeautifulSoup
import urllib.request
import re
import time


def query(q, waitfornextquery=True):
    url = 'http://duckduckgo.com/html/?q={0}'.format(q)
    req = urllib.request.Request(url, headers={'User-Agent':'Felipe Luna-{0}'.format(time.clock())})
    site = urllib.request.urlopen(req)
    data = site.read()

    parsed = BeautifulSoup(data)
    link_tags = parsed.findAll('div', {'class': re.compile('links_main*')})
    urls = []
    for lt in link_tags:
        if not lt.text.strip().lower().replace('  ',' ').startswith('no results'):
            urls.append(lt.a['href'])

    #parece que hay que esperar un poco
    
    if waitfornextquery:
        for i in range(20):
            time.sleep(1)
    return urls


if __name__ == '__main__':
    print(query('27EA33V+site:.cl',False))
