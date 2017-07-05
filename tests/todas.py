# -*- coding: utf-8 -*-
import re
import unittest
from src.buscar_solotodo import buscar_solotodo
from src.get_displaylag_tellys import get_displaylag_screens
from src.memoize_function_deco import file_memoized


@file_memoized()
def cached_solotodo(*args, **kargs):
    return buscar_solotodo(*args, **kargs)


@file_memoized()
def cached_tellys(*args, **kargs):
    return get_displaylag_screens(*args, **kargs)


class PruebaSolotodo(unittest.TestCase):
    def test_trae(self):
        "Va a buscar algo (lo que sea)"
        resultados = cached_solotodo("usb")
        self.assertTrue(resultados)


class PruebaMonitorSolotodo(unittest.TestCase):
    def test_trae(self):
        "Va a buscar algo (monitor de verdad)"
        resultados = cached_solotodo("MX279H")
        self.assertTrue(resultados)



class PruebaParserDisplayLag(unittest.TestCase):
    def test_formato(self):
        '''Revisa el formato de los resultados.'''
        pantallas = cached_tellys()
        for pantalla in pantallas:
            for etiqueta in ['brand',
                             'size',
                             'model',
                             'resolution',
                             'screen_type',
                             'input_lag']:
                self.assertIn(etiqueta, pantalla)
            self.assertIsNotNone(re.match(r'^\d{2}ms$', pantalla['input_lag']))
            self.assertIsNotNone(re.match(r'^[0-9.]+"$', pantalla['size']))


if __name__ == '__main__':
    unittest.main()
