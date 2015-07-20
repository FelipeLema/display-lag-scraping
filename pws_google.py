#required by pws
import requests

from pws import Google
import time

def query(q, waitfornextquery=True):
    try:
        r = Google.search(q)
    except TypeError:
        '''There's a bug involving empty results'''
        return []
    urls = []
    for result in r['results']:
        urls.append( result['link'] )
        
    if waitfornextquery:
        for i in range(20):
            time.sleep(1)
    return urls

if __name__ == '__main__':
    print(query('27EA33V site:.cl',False))
