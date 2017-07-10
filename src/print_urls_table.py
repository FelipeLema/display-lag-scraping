# -*- coding: utf-8 -*-
# system imports
import itertools as it
import pickle
import re
from io import StringIO
import urllib
import sys

# custom imports
import src.pws_google as pws_google
from src.get_displaylag_tellys import get_displaylag_screens
from src.memoize_function_deco import file_memoized
from src.buscar_solotodo import buscar_solotodo


class Screen(object):
    def __init__(self, brand, size, model, resolution, screen_type, input_lag):
        delay = input_lag
        del input_lag
        g = re.search(r'[0-9]+', delay)
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


def imprimirTabla(listaDeUrls, f):
    comoTabla = it.zip_longest(*listaDeUrls, fillvalue='')
    # https://stackoverflow.com/a/6473724/3637404
    transpuesta = map(list, zip(*comoTabla))
    for fila in transpuesta:
        filaFormateada = '|'.join(list(fila))
        f.write('|{0}\n'.format(filaFormateada))


def fill_screen_urls(screen, engine='solotodo'):
    model = screen.model
    try:
        f = {'py-web-search': search_for_urls_pwsg,
             'solotodo': buscar_solotodo, 
             }[engine]
    except KeyError:
        raise NotImplementedError('no conozco el motor "{0}"'.format(engine))
    r = f(model)
    for s in r:
        assert isinstance(s, str)
    screen.urls = r
    return r


@file_memoized()
def memo_get_displaylag_screens():
    return get_displaylag_screens()


if __name__ == '__main__':

    f = StringIO()
    f.write('|========\n')
    # Obtener modelos de pantallas
    screens_kargs = memo_get_displaylag_screens()
    all_screens = [Screen(**karg) for karg in screens_kargs]
    selected_scrns = list(filter(
            lambda x: x.delay <= 30.0,
            all_screens))
    screens = selected_scrns
    # cabeceras
    cabeceras = '|'.join(
        ['{0} {1} ({2}\',{3}ms)'.format(
            s.brand, s.model, s.size, s.delay)
            for s in screens])
    f.write('|{0}\n'.format(cabeceras))

    # evitar buscar dos veces (comparar usando modelo)
    model_set = set()
    to_del = []
    for s in screens:
        if s.model not in model_set:
            model_set.add(s.model)
        else:
            to_del.append(s)
    for td in to_del:
        screens.remove(td)
    # obtener urls para cada modelo
    for i_s,s in enumerate(screens):
        sys.stderr.write('Buscando {0} ({1}/{2})…'.format(
                s.model,
                i_s+1,
                len(screens)))
        sys.stderr.flush()
        fill_screen_urls(s)
        sys.stderr.write(' obtuve {0} resultados\n'.format(
            len(s.urls)))
        sys.stdout.flush()
    # rellenar
    max_l = -1
    for s in screens:
        max_l = max(max_l, len(s.urls))
    for s in screens:
        s.urls += list(it.repeat('', max_l-len(s.urls)))

    # imprimir urls
    imprimirTabla([s.urls for s in screens], f)

    # cerrar tabla
    f.write('|========\n')
    try:
        sys.stdout.write(f.getvalue())
    except Exception as e:
        pickle.dump(f, open("f_io.pickle", "wb"))
        raise e
