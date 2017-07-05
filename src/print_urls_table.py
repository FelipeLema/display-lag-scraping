# -*- coding: utf-8 -*-
#system imports
import itertools as it
import pickle
import re
from io import StringIO
import sys

# custom imports
import pws_google
from get_displaylag_tellys import get_displaylag_screens
from memoize_function_deco import file_memoized


class Screen(object):
    def __init__(self,brand,size,model,resolution,screen_type,input_lag):
        delay=input_lag
        del input_lag
        g = re.search(r'[0-9]+',delay)
        assert g is not None, "No delay in \"{0}\"".format(delay)
        delay = g.group(0)
        size = size.strip('\'"')
        self.brand = brand
        self.size  = float(size)
        self.model = model
        self.res   = resolution
        self.type  = screen_type
        self.delay = float(delay)
        self.urls  = []

@file_memoized()
def search_for_urls_pwsg(model):
    '''Use py-web-search
    '''
    urls = pws_google.query('{0} site:.cl'.format(model))
    urls += pws_google.query('{0} site:falabella.com'.format(model))
    return urls


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

def fill_screen_urls(screen,engine='py-web-search'):
    model = screen.model
    try:
        f={'py-web-search':search_for_urls_pwsg,
          'solotodo':search_for_urls_pwsg, 
                }[engine]
    except KeyError:
        raise NotImplementedError('no conozco el motor "{0}"'.format(engine))
    r = f(model)
    for s in r:
        assert isinstance(s,str)
    screen.urls = r
    return r

@file_memoized()
def memo_get_displaylag_screens():
    return get_displaylag_screens()

if __name__ == '__main__':

    f = StringIO()
    f.write(u'<table border="1">\n')
    #Obtener pantallas
    screens_kargs = memo_get_displaylag_screens()
    all_screens = [Screen(**karg) for karg in screens_kargs]
    selected_scrns = list(filter(\
            lambda x: x.delay <= 30.0,\
            all_screens))
    screens = selected_scrns


    #cabeceras
    f.write(u'<tr>\n')
    for s in screens:
        f.write(u'<th>{0} {1} ({2}\',{3}ms)</th>\n'.format(\
                s.brand, s.model, s.size, s.delay))
    f.write(u'</tr>')
    #evitar buscar dos veces (comparar usando modelo)
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
        sys.stderr.write('Buscando {0} ({1}/{2})\n'.format(\
                s.model,\
                i_s+1,\
                len(screens)))
        sys.stderr.flush()
        fill_screen_urls(s)
        sys.stdout.flush()
        print('')
        


    #rellenar
    max_l = -1
    for s in screens:
        max_l = max(max_l,len(s.urls))
    for s in screens:
        s.urls+=list(it.repeat('',max_l-len(s.urls))) 

    #imprimir urls
    print_table(list(zip(*[s.urls for s in screens])),f)

    try:
        print(f.getvalue().encode( 'utf-8' ))
    except Exception as e:
        pickle.dump(f, open("f_io.pickle","wb"))
        raise e

