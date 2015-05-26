# -*- coding: utf-8 -*-
#system imports
import itertools as it
import pickle
import re
from io import StringIO
import sys
import time
import urllib 

#custom imports
import duckduckhtml
from get_displaylag_tellys import get_displaylag_screens
from memoize_function_deco import file_memoized

class Screen(object):
    def __init__(self,brand,size,model,resolution,screen_type,input_lag):
        delay=input_lag
        del input_lag
        g = re.search(r'[0-9]+',delay)
        #assert(g, print u'No number in delay ("{0}")'.format(delay))
        delay = g.group(0)
        size = size.strip('\'"')
        self.brand = brand
        self.size  = float(size)
        self.model = model
        self.res   = resolution
        self.type  = screen_type
        self.delay = float(delay)
        self.urls  = []

def search_for_urls_ddgh(model):
    '''Use duckduckgo (uncensored) frontpage
    '''
    urls = duckduckhtml.query(u'{0}+site:.cl'.format(model))
    urls += duckduckhtml.query(u'{0}+site:falabella.com'.format(model))
    return urls

def search_for_urls_ddg(model):
    ''' Search using duckduckgo official (limited api)
    '''
    sites=['.cl','falabella.com']
    out=[]
    for site in sites:
        r = duckduckgo.query(u'{1}+site:{0}'.format(site,model),useragent='FelipeLuna')
        #avoid duckduckgo anti-spam system
        time.sleep(20)
        if r.type != u'answer':
            continue
        out += [r_i.url for r_i in r]
    return out

def print_table(t,f):
   for line in t:
       #en una línea hay una url por modelo
       f.write(u'<tr>\n')
       for url in line:
           parsed_url = urllib.parse.urlparse(url)
           base_url = '.'.join(parsed_url.netloc.split('.')[-2:])
           #remover puerto
           base_url = base_url.split(':')[0]
           f.write(u'<td>\n')
           f.write(u'<a href="{0}" target="_blank" >{1}</a>\n'.format(\
                    url,\
                    base_url ))
           f.write(u'</td>\n')
       f.write(u'</tr>\n')
   f.write(u'</table>\n')
@file_memoized
def fill_screen_urls(screen,engine='duckduckgohtml'):
    model = screen.model
    try:
        f={'duckduckgo':search_for_urls_ddg,\
           'duckduckgohtml':search_for_urls_ddgh
                }[engine]
    except KeyError:
        raise NotImplementedError(u'No such engine "{0}"'.format(engine))
    r = f(model)
    for s in r:
        assert isinstance(s,str)
    screen.urls = r
    return r


if __name__ == '__main__':

    f = StringIO()
    f.write(u'<table border="1">\n')
    #Obtener pantallas
    #screens = [Screen(u'Samsung',"32''",u'UN32EH4003','720p','LED','19ms')]
    screens_kargs = get_displaylag_screens()
    all_screens = [Screen(**karg) for karg in screens_kargs]
    selected_scrns = list(filter(\
            lambda x: x.delay <= 30.0,\
            all_screens))
    screens = selected_scrns
    #from pudb import set_trace;set_trace()


    #cabeceras
    f.write(u'<tr>\n')
    for s in screens:
        f.write(u'<th>{0} {1} ({2}\',{3}ms)</th>\n'.format(\
                s.brand, s.model, s.size, s.delay))
    f.write(u'</tr>')
    #evitar buscar dos veces
    model_set = set()
    to_del = []
    for s in screens:
        if s.model not in model_set:
            model_set.add(s.model)
        else:
            to_del.append(s)
    for td in to_del:
        screens.remove(td)
    #obtener urls
    for i_s,s in enumerate(screens):
        sys.stderr.write(u'Looking for {0} ({1}/{2})\n'.format(\
                s.model,\
                i_s+1,\
                len(screens)))
        sys.stderr.flush()
        #s.urls = search_for_urls(s.model)
        fill_screen_urls(s)
        #print u'{0} para {1}'.format(len(s.urls),s.model)
        sys.stdout.flush()
        print('')
        


    #rellenar
    max_l = -1
    for s in screens:
        max_l = max(max_l,len(s.urls))
    for s in screens:
        s.urls+=list(it.repeat('',max_l-len(s.urls))) 

    #imprimir urls
    print_table(list(it.izip(*[s.urls for s in screens])),f)

    try:
        print(f.getvalue().encode( 'utf-8' ))
    except Exception as e:
        pickle.dump(f, open("f_io.pickle","wb"))
        raise e

