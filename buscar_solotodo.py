# -*- coding: utf-8 -*-
''' Buscar en http://www.solotodo.com/
'''
from html.parser import HTMLParser
import urllib.request
from collections import defaultdict
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


def buscar_solotodo(consulta=None, archHtml=None):
    '''Buscar en http://www.solotodo.com/
    '''
    if archHtml is None:
        assert(consulta is not None)
        fileName, headers = urllib.request.urlretrieve(
            "http://www.solotodo.com/search/?keywords={}".format(consulta))
        print(archHtml)
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
    return urlsCompletas


if __name__ == '__main__':
    print(buscar_solotodo(archHtml="./index.html?keywords=usb"))
    # print(buscar_solotodo(consulta="usb"))

