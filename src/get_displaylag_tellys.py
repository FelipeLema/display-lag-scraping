'''Gets monitor info from displaylag.com and a few more

See http://forums.shoryuken.com/discussion/comment/8676004#Comment_8676004
'''
from html.parser import HTMLParser
import urllib.request
import re

fields = ['brand',    'size',     'model',    'resolution', 'screen_type', 'input_lag']
tags   = ['column-3', 'column-2', 'column-4', 'column-5',   'column-8',    'column-9']
# filas de la 2 en adelante
rowClassRE = re.compile(r'row-([2-9]|\d{2,}) (odd|even)')


class DisplayLagParser(HTMLParser):
    classRe = r"column-(1|2)"

    def __init__(self):
        super(DisplayLagParser, self).__init__()
        self.inRow = False
        # class→field
        self.currentTv = {}
        # "column-4", "column-3",…
        self.currentColumn = None
        self.allTv = []

    def _getClass(self, attrs):
        _attrs = dict()
        for p in attrs:
            _attrs[p[0]] = p[1]
        _class = _attrs['class']
        return _class

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            _class = self._getClass(attrs)
            if _class is not None and re.match(rowClassRE, _class):
                self.inRow = True
                return
        if self.inRow and tag == "td":
            _class = self._getClass(attrs)
            self.currentColumn = _class

    def handle_endtag(self, tag):
        if tag == "tr":
            self.inRow = False
            if self.currentTv is not None and self.currentTv:
                self.allTv.append(self.currentTv.copy())
                self.currentTv.clear()
            return

    def handle_data(self, data):
        if self.inRow and len(data.strip()) > 0:
            self.currentTv[self.currentColumn] = data


def html_parse_get(htmlStr):
    parser = DisplayLagParser()
    parser.feed(htmlStr)
    return parser.allTv


def urllib_and_html_parse_get(max_screens=30, htmlFilePath=None):
    if htmlFilePath is None:
        fileName, headers = urllib.request.urlretrieve(
            "https://displaylag.com/display-database/")
    else:
        fileName = htmlFilePath
    with open(fileName) as htmlFile:
        listOfTvs = html_parse_get('\n'.join(htmlFile.readlines()))
        global fields
        out = []
        for tv in listOfTvs:
            translatedFields = {}
            for f, t in zip(fields, tags):
                try:
                    translatedFields[f] = tv[t]
                except KeyError as e:
                    print(tv)
                    raise RuntimeError from e
            out.append(translatedFields)
        return out[:max_screens]


def get_displaylag_screens():
    return urllib_and_html_parse_get() + \
        get_squidoo_monitors() + \
        monitores_particulares()


def formatear(cabecera, datos):
    '''Toma una lista como cabecera, datos como
lista de strings y retorna una tabla'''
    # datos como lista
    datos_l = [i.split() for i in datos]
    for single in datos_l:
        assert len(cabecera) == len(single)
    salida = []
    for single in datos_l:
        if len(single) == 0:
            continue
        salida.append(dict([
                (k, single[idx]) for idx, k in enumerate(cabecera)]))
    return salida


def get_squidoo_monitors():
    '''
    I could've done a parser, but this is a one-time list.
    No use in making it re-runnable
    '''
    cabecera = \
        ['brand', 'size', 'model', 'resolution', 'screen_type', 'input_lag']
    listaMonitores = [
            'Asus 21.5 VE228H 1x1 monitor 7ms',
            'BenQ 27 GW2750HM 1X1 monitor 7ms',
            'Dell 27 S2740L 1x1 monitor 6.3ms',
            'LG 27 IPS277L-BN 1x1 monitor 6.2ms ',
            'BenQ 24 GW2450 1920x1080 monitor 4ms',
            'AOC 23 e2352PHZ 1x1 monitor 5.1ms',
            'Viewsonic 24 VX2453MH 1920x1080 monitor 4.9ms',
            'Foris 23 FS2333-BK 1x1 monitor 4.6ms',
            'Viewsonic 23 VX2370SMH 1920x1080 monitor 4.9ms',
            'BenQ 24 RL2450HT 1x1 monitor 4.2ms',
            'Dell 23 S2330MX 1x1 monitor 3.8ms ',
            'Asus 27 MX279H 1x1 monitor 3.8ms',
            'Viewsonic 27 VX2770SMH 1x1 monitor 3.5ms',
            'Acer 27 S27HLbmii 1x1 monitor 3.4ms',
            'LG 27 VG278HE 1x1 monitor 7.3ms',
            'LG 27 VG278H 1x1 monitor 6.5ms',
            'BenQ 24 XL2420T 1x1 monitor 4.9ms',
            'Asus 24 VG248QE 1x1 monitor 3.1ms',
            ]
    return formatear(cabecera, listaMonitores)


# see #1
def monitores_particulares():
    cabecera = \
        ['brand', 'size', 'model', 'resolution', 'screen_type', 'input_lag']
    listaMonitores = [
        #                               ↓ No sé, en realidad
        'Samsung 24 C27F398 1x1 monitor 11ms',
        'Samsung 27 LC24F390FHLX 1x1 monitor 4ms',
    ]
    return formatear(cabecera, listaMonitores)
