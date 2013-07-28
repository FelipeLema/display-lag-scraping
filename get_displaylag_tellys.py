'''Gets monitor info from displaylag.com 
'''
from BeautifulSoup import BeautifulSoup
import urllib
import re

def get_displaylag_screens(max_screens=30):
    site = urllib.urlopen('http://www.displaylag.com/display-database/')
    data = site.read()
    parsed = BeautifulSoup(data)
    del data
    #build re
    fields = ['brand','size','model','resolution','screen_type','input_lag']

    by_fields={}
    for f in fields:
        le_re = r'{0}-field'.format(\
            f)
        markups = parsed.findAll('td', {'class': le_re})
        #from pudb import set_trace; set_trace() 
        by_fields[f]=[m.text.replace('&quot;','\'') for m in markups]

    l=-1
    for f in fields:
        if l<0:
            l=len(by_fields[f])
        assert l==len(by_fields[f]),'{0} != {1}'.format(l,len(by_fields[f]))
    out=[]
    for i in xrange(l):
        out.append(dict([ \
                (f,by_fields[f][i]) for f in fields]))
    return out

if __name__ == '__main__':
    for i in get_displaylag_screens()[:12]:
        print i
