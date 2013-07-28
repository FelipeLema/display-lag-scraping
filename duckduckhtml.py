'''Another duckduckgo searcher

Returns only urls
'''
from BeautifulSoup import BeautifulSoup
import urllib2
import re
import time


def query(q):
    url = 'http://duckduckgo.com/html/?q={0}'.format(q)
    req = urllib2.Request(url, headers={'User-Agent':'Felipe Luna-{0}'.format(time.clock())})
    site = urllib2.urlopen(req)
    data = site.read()

    parsed = BeautifulSoup(data)
    link_tags = parsed.findAll('div', {'class': re.compile('links_main*')})
    urls = [lt.a['href'] for lt in link_tags]

    return urls


if __name__ == '__main__':
    #from pudb import set_trace;set_trace()
    print query('UN32EH4003+site:.cl')
