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
        self.mirandoEntradaDeResultado = False

    def handle_starttag(self, tag, attrs):
        _attrs = defaultdict(lambda: None)
        for k,v in attrs:
            _attrs[k] = v

        if tag == "h4" and _attrs["class"] == "search-result-title":
            self.mirandoEntradaDeResultado = True
            return

        if self.mirandoEntradaDeResultado and tag == "a":
            self.resultados.append(_attrs["href"])
            return
            
    def handle_endtag(self, tag):
        if tag == "div":
            self.mirandoEntradaDeResultado = False

    def handle_data(self, data):
        pass


def buscar_solotodo(consulta=None, archHtml=None,
                    descanso=datetime.timedelta(seconds=30)):
    '''Buscar en http://www.solotodo.com/
    '''
    if archHtml is None:
        assert(consulta is not None)
        fileName, headers = urllib.request.urlretrieve(
            "http://www.solotodo.com/search/?keywords={}".format(consulta))
    else:
        assert(consulta is None)
        fileName = archHtml

    parser = SolotodoParser()
    with open(fileName) as htmlFile:
        htmlStr = '\n'.join(htmlFile.readlines())
        parser.feed(htmlStr)
        if not parser.resultados:
            nombreRegistro = "./última_consulta.html"
            with open(nombreRegistro, "w") as registro:
                registro.write(htmlStr)
            warnings.warn("Sin resultados, revisa {}".format(nombreRegistro))
    urlsCompletas = list(map(lambda url: "http://www.solotodo.com"+url,
                             parser.resultados))

    # Al parececer, solotodo no deja buscar de corrido
    time.sleep(ceil(descanso.total_seconds()))
    
    return urlsCompletas
