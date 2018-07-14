# -*- coding: utf-8 -*-
''' Buscar en http://www.solotodo.com/
'''
from collections import defaultdict
from html.parser import HTMLParser
from math import ceil
import urllib.request
import datetime
import time
import warnings


class SolotodoParser(HTMLParser):
    def __init__(self):
        super(SolotodoParser, self).__init__()
        self.resultados = []

    def handle_starttag(self, tag, attrs):
        _attrs = defaultdict(lambda: None)
        for k,v in attrs:
            _attrs[k] = v

        if tag != "a":
            return
        if "href" not in _attrs.keys():
            return
        if not _attrs["href"].startswith('/products/'):
            return

        self.resultados.append(_attrs["href"])
        return
            
    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass


def buscar_solotodo(consulta=None, archHtml=None,
                    descanso=datetime.timedelta(seconds=60),
                    avisarVacíos=False):
    '''Buscar en http://www.solotodo.com/
    '''
    if archHtml is None:
        assert(consulta is not None)
        request = urllib.request.Request(
            "https://www.solotodo.com/search?search={}".format(consulta),
            headers={'User-Agent': 'Mozilla/5.0'})
        htmlStr = urllib.request.urlopen(request).read().decode(encoding='utf-8')
    else:
        assert(consulta is None)
        with open(archHtml) as htmlFile:
            htmlStr = '\n'.join(htmlFile.readlines())

    raise RuntimeError("Aprender a ocupar selenium")
    parser = SolotodoParser()
    parser.feed(htmlStr)
    if not parser.resultados and avisarVacíos:
        nombreRegistro = "./última_consulta-{0}.html".format(
            datetime.datetime.now().isoformat())
        with open(nombreRegistro, "w") as registro:
            registro.write(htmlStr)
        warnings.warn("Sin resultados, revisa {}".format(nombreRegistro))
    resultadosÚnicos = list(set(parser.resultados))
    urlsCompletas = list(map(lambda url: "http://www.solotodo.com"+url,
                             resultadosÚnicos))

    # Al parececer, solotodo no deja buscar de corrido
    time.sleep(ceil(descanso.total_seconds()))
    
    return urlsCompletas
